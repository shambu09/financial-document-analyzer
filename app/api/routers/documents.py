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
from app.models.factory import get_document_model

DATA_DIR = "data"

router = APIRouter(prefix="/documents", tags=["documents"])
document_model = get_document_model()

# Models
class DocumentMetadata(BaseModel):
    id: str  # Document ID from database
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

def build_metadata(file_path: str, document_id: str = None) -> DocumentMetadata:
    stat = os.stat(file_path)
    return DocumentMetadata(
        id=document_id or "unknown",
        name=os.path.basename(file_path),
        size_bytes=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
        path=file_path,
        download_url=f"/documents/download/{os.path.basename(file_path)}",
    )

# Endpoints
@router.get("/", response_model=List[DocumentMetadata])
async def list_documents(q: Optional[str] = None, current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """List documents for the current user with optional search"""
    try:
        # Get documents from database using the proper model
        documents = document_model.get_user_documents(
            user_id=current_user["id"],
            search_query=q,
            limit=100,  # Reasonable limit
            offset=0
        )
        
        files = []
        for doc in documents:
            # Check if file still exists on filesystem
            if os.path.isfile(doc["path"]):
                files.append(DocumentMetadata(
                    id=str(doc["id"]),
                    name=doc["original_name"],
                    size_bytes=doc["size_bytes"],
                    modified_at=doc["created_at"],
                    path=doc["path"],
                    download_url=f"/documents/download/{os.path.basename(doc['path'])}"
                ))
        
        return files
        
    except Exception as e:
        # Fallback to filesystem listing if database fails
        ensure_data_dir()
        files = []
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
    """Upload a new document"""
    ensure_data_dir()
    original_name = name or file.filename or f"upload_{uuid.uuid4().hex}"
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Create document using the proper model
        doc_result = document_model.create_document(
            user_id=current_user["id"],
            original_name=original_name,
            file_content=file_content,
            upload_path=DATA_DIR
        )
        
        # Return metadata with document ID
        return DocumentMetadata(
            id=str(doc_result["id"]),
            name=doc_result["original_name"],
            size_bytes=doc_result["size_bytes"],
            modified_at=doc_result["created_at"],
            path=doc_result["path"],
            download_url=f"/documents/download/{os.path.basename(doc_result['path'])}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    finally:
        try:
            await file.close()
        except Exception:
            pass

@router.get("/download/{filename}")
async def download_document(filename: str, current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Download a document by filename"""
    safe = sanitize_filename(filename)
    
    # Find document in database
    try:
        # Get all user documents and find the one with matching filename
        documents = document_model.get_user_documents(current_user["id"])
        target_doc = None
        for doc in documents:
            if os.path.basename(doc["path"]) == safe:
                target_doc = doc
                break
        
        if not target_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path = target_doc["path"]
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(file_path, filename=target_doc["original_name"])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing document: {str(e)}")

@router.delete("/{filename}")
async def delete_document(filename: str, current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Delete a document by filename"""
    safe = sanitize_filename(filename)
    
    try:
        # Find document in database
        documents = document_model.get_user_documents(current_user["id"])
        target_doc = None
        for doc in documents:
            if os.path.basename(doc["path"]) == safe:
                target_doc = doc
                break
        
        if not target_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from database
        success = document_model.delete_document(target_doc["id"], current_user["id"])
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete document from database")
        
        # Delete file from filesystem
        file_path = target_doc["path"]
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                # Log but don't fail - database record is already deleted
                print(f"Warning: Could not delete file {file_path}: {e}")
        
        return {"status": "deleted", "filename": safe, "document_id": str(target_doc["id"])}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
