from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import re
import uuid
import shutil
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.api.routers.auth import get_current_active_user
from app.models.auth import DatabaseManager

DATA_DIR = "data"

router = APIRouter(prefix="/documents", tags=["documents"])
dbm = DatabaseManager()

# Models
class DocumentMetadata(BaseModel):
    name: str
    size_bytes: int
    modified_at: str
    path: str
    download_url: str

# Helpers
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

SAFE_FILENAME_REGEX = re.compile(r"[^A-Za-z0-9._-]+")

def sanitize_filename(filename: str) -> str:
    base = os.path.basename(filename)
    base = base.strip()
    base = SAFE_FILENAME_REGEX.sub("_", base)
    # prevent empty filenames
    if not base or base in {".", ".."}:
        base = f"upload_{uuid.uuid4().hex}"
    return base

def build_metadata(file_path: str) -> DocumentMetadata:
    stat = os.stat(file_path)
    return DocumentMetadata(
        name=os.path.basename(file_path),
        size_bytes=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
        path=file_path,
        download_url=f"/documents/download/{os.path.basename(file_path)}",
    )

# Endpoints
@router.get("/", response_model=List[DocumentMetadata])
async def list_documents(q: Optional[str] = None, current_user: Dict[str, Any] = Depends(get_current_active_user)):
    ensure_data_dir()
    files = []
    # Enforce per-user visibility: look up rows in documents table when present; fallback to filesystem for existing installs
    import sqlite3
    try:
        with sqlite3.connect(dbm.db_path) as conn:
            cursor = conn.cursor()
            if current_user.get("is_admin"):
                if q:
                    cursor.execute("""
                        SELECT path FROM documents WHERE original_name LIKE ? ORDER BY created_at DESC
                    """, (f"%{q}%",))
                else:
                    cursor.execute("""
                        SELECT path FROM documents ORDER BY created_at DESC
                    """)
            else:
                if q:
                    cursor.execute("""
                        SELECT path FROM documents WHERE user_id = ? AND original_name LIKE ? ORDER BY created_at DESC
                    """, (current_user["id"], f"%{q}%"))
                else:
                    cursor.execute("""
                        SELECT path FROM documents WHERE user_id = ? ORDER BY created_at DESC
                    """, (current_user["id"],))
            rows = cursor.fetchall()
            for (path,) in rows:
                if os.path.isfile(path):
                    files.append(build_metadata(path))
    except Exception:
        # Fallback to filesystem listing if DB missing rows (legacy files)
        for entry in os.scandir(DATA_DIR):
            if entry.is_file():
                if q and q.lower() not in entry.name.lower():
                    continue
                files.append(build_metadata(entry.path))
    files.sort(key=lambda m: m.modified_at, reverse=True)
    return files

@router.post("/upload", response_model=DocumentMetadata)
async def upload_document(
    file: UploadFile = File(...),
    name: Optional[str] = Form(default=None),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    ensure_data_dir()
    original_name = name or file.filename or f"upload_{uuid.uuid4().hex}"
    safe_name = sanitize_filename(original_name)
    # Avoid overwriting existing files
    final_name = safe_name
    counter = 1
    while os.path.exists(os.path.join(DATA_DIR, final_name)):
        stem, dot, ext = safe_name.rpartition('.')
        if dot:
            final_name = f"{stem}_{counter}.{ext}"
        else:
            final_name = f"{safe_name}_{counter}"
        counter += 1

    dest_path = os.path.join(DATA_DIR, final_name)
    try:
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(file.file, out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    finally:
        try:
            await file.close()
        except Exception:
            pass

    meta = build_metadata(dest_path)

    # Record ownership in DB
    import sqlite3
    try:
        with sqlite3.connect(dbm.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO documents (user_id, original_name, stored_name, path, size_bytes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (current_user["id"], original_name, final_name, dest_path, meta.size_bytes),
            )
            conn.commit()
    except Exception:
        # Non-fatal: file is saved but DB row failed
        pass

    return meta

@router.get("/download/{filename}")
async def download_document(filename: str, current_user: Dict[str, Any] = Depends(get_current_active_user)):
    safe = sanitize_filename(filename)
    file_path = os.path.join(DATA_DIR, safe)
    # Enforce ownership unless admin
    if not current_user.get("is_admin"):
        import sqlite3
        with sqlite3.connect(dbm.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM documents WHERE user_id = ? AND stored_name = ?", (current_user["id"], safe))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=403, detail="Not authorized to access this file")
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=safe)

@router.delete("/{filename}")
async def delete_document(filename: str, current_user: Dict[str, Any] = Depends(get_current_active_user)):
    safe = sanitize_filename(filename)
    file_path = os.path.join(DATA_DIR, safe)
    # Enforce ownership unless admin
    if not current_user.get("is_admin"):
        import sqlite3
        with sqlite3.connect(dbm.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM documents WHERE user_id = ? AND stored_name = ?", (current_user["id"], safe))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=403, detail="Not authorized to delete this file")
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        os.remove(file_path)
        # Remove DB entry
        try:
            import sqlite3
            with sqlite3.connect(dbm.db_path) as conn:
                cursor = conn.cursor()
                if current_user.get("is_admin"):
                    cursor.execute("DELETE FROM documents WHERE stored_name = ?", (safe,))
                else:
                    cursor.execute("DELETE FROM documents WHERE user_id = ? AND stored_name = ?", (current_user["id"], safe))
                conn.commit()
        except Exception:
            pass
        return {"status": "deleted", "filename": safe}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
