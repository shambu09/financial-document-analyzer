from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import uuid
import asyncio
from typing import Optional, Union, Dict, Any
from datetime import datetime

from crewai import Crew, Process
from app.domain.agents import financial_analyst, verifier, investment_advisor, risk_assessor
from app.domain.task import analyze_financial_document, investment_analysis, risk_assessment, verification
from app.api.routers.auth import get_current_active_user
from app.models.auth import User, DatabaseManager, AnalysisReport
from app.models.factory import get_document_model, get_analysis_report_model
from app.models.schemas import ReportStatus
from app.celery_tasks import get_celery_task

router = APIRouter(prefix="/analysis", tags=["analysis"])

# Initialize database manager
db_manager = DatabaseManager()
analysis_reports = AnalysisReport(db_manager)
document_model = get_document_model()

def run_crew(agents, tasks, query: str, file_path: str):
    """Run the crew with specified agents and tasks"""
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
    )
    
    result = crew.kickoff({'query': query, 'file_path': file_path})
    return result

def validate_document_ownership(document_id: Optional[str], user_id: str) -> None:
    """Validate that the document belongs to the user"""
    if document_id is not None:
        document = document_model.get_document(document_id, user_id)
        if not document:
            raise HTTPException(
                status_code=404, 
                detail="Document not found or you don't have permission to access it"
            )

def save_analysis_report(
    user_id: int,
    analysis_type: str,
    query: str,
    file_name: str,
    analysis_result: str,
    document_id: Optional[str] = None
) -> int:
    """Save analysis report to database and filesystem"""
    try:
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        
        # Generate unique report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{analysis_type}_{user_id}_{timestamp}.txt"
        report_path = os.path.join("outputs", report_filename)
        
        # Save analysis result to file
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"Analysis Type: {analysis_type}\n")
            f.write(f"Query: {query}\n")
            f.write(f"Original File: {file_name}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 50 + "\n\n")
            f.write(str(analysis_result))
        
        # Create summary (first 200 characters)
        summary = str(analysis_result)[:200] + "..." if len(str(analysis_result)) > 200 else str(analysis_result)
        
        # Save to database
        report_id = analysis_reports.create_report(
            user_id=user_id,
            analysis_type=analysis_type,
            query=query,
            file_name=file_name,
            report_path=report_path,
            document_id=document_id,
            summary=summary,
            status="completed"
        )
        
        return report_id
        
    except Exception as e:
        print(f"Error saving analysis report: {str(e)}")
        raise

@router.post("/comprehensive")
async def analyze_comprehensive(
    query: str = Form(default="Analyze this financial document for comprehensive insights"),
    file: Optional[UploadFile] = File(None),
    document_id: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Comprehensive financial document analysis - runs in background"""
    
    # Validate that either file or document_id is provided, but not both
    if not file and not document_id:
        raise HTTPException(
            status_code=400,
            detail="Either file upload or document_id must be provided"
        )
    
    if file and document_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide both file upload and document_id. Choose one."
        )
    
    # Validate document ownership if document_id is provided
    if document_id:
        validate_document_ownership(document_id, current_user["id"])
        # Get document details for analysis
        document = document_model.get_document(document_id, current_user["id"])
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        file_path = document['path']
        file_name = document['original_name']
    else:
        # Handle file upload
        file_id = str(uuid.uuid4())
        # Get file extension from uploaded file
        file_extension = ""
        if file.filename and "." in file.filename:
            file_extension = "." + file.filename.split(".")[-1]
        else:
            file_extension = ".pdf"  # Default to PDF if no extension
        
        file_path = f"data/analysis_{file_id}_{current_user['id']}{file_extension}"
        file_name = file.filename or f"upload_{file_id}{file_extension}"
    
    try:
        # Only save file if it was uploaded (not using document_id)
        if file:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            # Save uploaded file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        
        # Validate query
        if not query or query.strip() == "":
            query = "Analyze this financial document for comprehensive insights"
        
        # Create report with pending status
        analysis_reports = get_analysis_report_model()
        report_data = analysis_reports.create_report(
            user_id=current_user["id"],
            analysis_type="comprehensive",
            query=query.strip(),
            file_name=file_name,
            analysis_result="Analysis queued...",
            document_id=document_id
        )
        report_id = report_data["id"] if isinstance(report_data, dict) else report_data
        
        # Start Celery task
        celery_task = get_celery_task("comprehensive")
        task = celery_task.delay(
            report_id=report_id,
            query=query.strip(),
            file_path=file_path,
            file_name=file_name,
            user_id=current_user["id"],
            document_id=document_id
        )
        
        # Create task-report mapping
        from app.models.factory import get_task_report_mapping_model
        mapping_model = get_task_report_mapping_model()
        mapping_model.create_mapping(
            task_id=task.id,
            report_id=report_id,
            user_id=current_user["id"],
            analysis_type="comprehensive"
        )
        
        return {
            "status": "queued",
            "analysis_type": "comprehensive",
            "query": query,
            "file_processed": file_name,
            "user_id": current_user["id"],
            "report_id": report_id,
            "task_id": task.id,
            "report_status": ReportStatus.PENDING.value,
            "report_download_url": f"/reports/{report_id}/download",
            "task_status_url": f"/tasks/{task.id}/status",
            "message": "Analysis has been queued and will be processed in the background"
        }
        
    except Exception as e:
        # Only cleanup uploaded file, not existing documents
        if file and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")

@router.post("/investment")
async def analyze_investment(
    query: str = Form(default="Analyze this financial document for investment opportunities"),
    file: Optional[UploadFile] = File(None),
    document_id: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Investment-focused financial document analysis"""
    
    # Validate that either file or document_id is provided, but not both
    if not file and not document_id:
        raise HTTPException(
            status_code=400,
            detail="Either file upload or document_id must be provided"
        )
    
    if file and document_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide both file upload and document_id. Choose one."
        )
    
    # Validate document ownership if document_id is provided
    if document_id:
        validate_document_ownership(document_id, current_user["id"])
        # Get document details for analysis
        document = document_model.get_document(document_id, current_user["id"])
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        file_path = document['path']
        file_name = document['original_name']
    else:
        # Handle file upload
        file_id = str(uuid.uuid4())
        # Get file extension from uploaded file
        file_extension = ""
        if file.filename and "." in file.filename:
            file_extension = "." + file.filename.split(".")[-1]
        else:
            file_extension = ".pdf"  # Default to PDF if no extension
        
        file_path = f"data/investment_{file_id}_{current_user['id']}{file_extension}"
        file_name = file.filename or f"upload_{file_id}{file_extension}"
    
    try:
        # Only save file if it was uploaded (not using document_id)
        if file:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            # Save uploaded file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        
        # Validate query
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment opportunities"
        
        # Create report with pending status
        analysis_reports = get_analysis_report_model()
        report_data = analysis_reports.create_report(
            user_id=current_user["id"],
            analysis_type="investment",
            query=query.strip(),
            file_name=file_name,
            analysis_result="Investment analysis queued...",
            document_id=document_id
        )
        report_id = report_data["id"] if isinstance(report_data, dict) else report_data
        
        # Start Celery task
        celery_task = get_celery_task("investment")
        task = celery_task.delay(
            report_id=report_id,
            query=query.strip(),
            file_path=file_path,
            file_name=file_name,
            user_id=current_user["id"],
            document_id=document_id
        )
        
        # Create task-report mapping
        from app.models.factory import get_task_report_mapping_model
        mapping_model = get_task_report_mapping_model()
        mapping_model.create_mapping(
            task_id=task.id,
            report_id=report_id,
            user_id=current_user["id"],
            analysis_type="investment"
        )
        
        return {
            "status": "queued",
            "analysis_type": "investment",
            "query": query,
            "file_processed": file_name,
            "user_id": current_user["id"],
            "report_id": report_id,
            "task_id": task.id,
            "report_status": ReportStatus.PENDING.value,
            "report_download_url": f"/reports/{report_id}/download",
            "task_status_url": f"/tasks/{task.id}/status",
            "message": "Investment analysis has been queued and will be processed in the background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing investment analysis: {str(e)}")
    
    finally:
        # Only cleanup uploaded file, not existing documents
        if file and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors

@router.post("/risk")
async def analyze_risk(
    query: str = Form(default="Analyze this financial document for risk assessment"),
    file: Optional[UploadFile] = File(None),
    document_id: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Risk-focused financial document analysis"""
    
    # Validate that either file or document_id is provided, but not both
    if not file and not document_id:
        raise HTTPException(
            status_code=400,
            detail="Either file upload or document_id must be provided"
        )
    
    if file and document_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide both file upload and document_id. Choose one."
        )
    
    # Validate document ownership if document_id is provided
    if document_id:
        validate_document_ownership(document_id, current_user["id"])
        # Get document details for analysis
        document = document_model.get_document(document_id, current_user["id"])
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        file_path = document['path']
        file_name = document['original_name']
    else:
        # Handle file upload
        file_id = str(uuid.uuid4())
        # Get file extension from uploaded file
        file_extension = ""
        if file.filename and "." in file.filename:
            file_extension = "." + file.filename.split(".")[-1]
        else:
            file_extension = ".pdf"  # Default to PDF if no extension
        
        file_path = f"data/risk_{file_id}_{current_user['id']}{file_extension}"
        file_name = file.filename or f"upload_{file_id}{file_extension}"
    
    try:
        # Only save file if it was uploaded (not using document_id)
        if file:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            # Save uploaded file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        
        # Validate query
        if not query or query.strip() == "":
            query = "Analyze this financial document for risk assessment"
        
        # Create report with pending status
        analysis_reports = get_analysis_report_model()
        report_data = analysis_reports.create_report(
            user_id=current_user["id"],
            analysis_type="risk",
            query=query.strip(),
            file_name=file_name,
            analysis_result="Risk analysis queued...",
            document_id=document_id
        )
        report_id = report_data["id"] if isinstance(report_data, dict) else report_data
        
        # Start Celery task
        celery_task = get_celery_task("risk")
        task = celery_task.delay(
            report_id=report_id,
            query=query.strip(),
            file_path=file_path,
            file_name=file_name,
            user_id=current_user["id"],
            document_id=document_id
        )
        
        # Create task-report mapping
        from app.models.factory import get_task_report_mapping_model
        mapping_model = get_task_report_mapping_model()
        mapping_model.create_mapping(
            task_id=task.id,
            report_id=report_id,
            user_id=current_user["id"],
            analysis_type="risk"
        )
        
        return {
            "status": "queued",
            "analysis_type": "risk",
            "query": query,
            "file_processed": file_name,
            "user_id": current_user["id"],
            "report_id": report_id,
            "task_id": task.id,
            "report_status": ReportStatus.PENDING.value,
            "report_download_url": f"/reports/{report_id}/download",
            "task_status_url": f"/tasks/{task.id}/status",
            "message": "Risk analysis has been queued and will be processed in the background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing risk analysis: {str(e)}")
    
    finally:
        # Only cleanup uploaded file, not existing documents
        if file and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors

@router.post("/verify")
async def verify_document(
    query: str = Form(default="Verify if this is a valid financial document"),
    file: Optional[UploadFile] = File(None),
    document_id: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Verify if the document is a valid financial record"""
    
    # Validate that either file or document_id is provided, but not both
    if not file and not document_id:
        raise HTTPException(
            status_code=400,
            detail="Either file upload or document_id must be provided"
        )
    
    if file and document_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide both file upload and document_id. Choose one."
        )
    
    # Validate document ownership if document_id is provided
    if document_id:
        validate_document_ownership(document_id, current_user["id"])
        # Get document details for analysis
        document = document_model.get_document(document_id, current_user["id"])
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        file_path = document['path']
        file_name = document['original_name']
    else:
        # Handle file upload
        file_id = str(uuid.uuid4())
        # Get file extension from uploaded file
        file_extension = ""
        if file.filename and "." in file.filename:
            file_extension = "." + file.filename.split(".")[-1]
        else:
            file_extension = ".pdf"  # Default to PDF if no extension
        
        file_path = f"data/verify_{file_id}_{current_user['id']}{file_extension}"
        file_name = file.filename or f"upload_{file_id}{file_extension}"
    
    try:
        # Only save file if it was uploaded (not using document_id)
        if file:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            # Save uploaded file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        
        # Validate query
        if not query or query.strip() == "":
            query = "Verify if this is a valid financial document"
        
        # Create report with pending status
        analysis_reports = get_analysis_report_model()
        report_data = analysis_reports.create_report(
            user_id=current_user["id"],
            analysis_type="verification",
            query=query.strip(),
            file_name=file_name,
            analysis_result="Verification analysis queued...",
            document_id=document_id
        )
        report_id = report_data["id"] if isinstance(report_data, dict) else report_data
        
        # Start Celery task
        celery_task = get_celery_task("verification")
        task = celery_task.delay(
            report_id=report_id,
            query=query.strip(),
            file_path=file_path,
            file_name=file_name,
            user_id=current_user["id"],
            document_id=document_id
        )
        
        # Create task-report mapping
        from app.models.factory import get_task_report_mapping_model
        mapping_model = get_task_report_mapping_model()
        mapping_model.create_mapping(
            task_id=task.id,
            report_id=report_id,
            user_id=current_user["id"],
            analysis_type="verification"
        )
        
        return {
            "status": "queued",
            "analysis_type": "verification",
            "query": query,
            "file_processed": file_name,
            "user_id": current_user["id"],
            "report_id": report_id,
            "task_id": task.id,
            "report_status": ReportStatus.PENDING.value,
            "report_download_url": f"/reports/{report_id}/download",
            "task_status_url": f"/tasks/{task.id}/status",
            "message": "Verification analysis has been queued and will be processed in the background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document verification: {str(e)}")
    
    finally:
        # Only cleanup uploaded file, not existing documents
        if file and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors

@router.get("/types")
async def get_analysis_types(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Get available analysis types"""
    return {
        "available_analysis_types": [
            {
                "type": "comprehensive",
                "endpoint": "/analysis/comprehensive",
                "description": "Comprehensive financial document analysis with all metrics and insights"
            },
            {
                "type": "investment",
                "endpoint": "/analysis/investment", 
                "description": "Investment-focused analysis with specific recommendations"
            },
            {
                "type": "risk",
                "endpoint": "/analysis/risk",
                "description": "Risk assessment analysis across multiple dimensions"
            },
            {
                "type": "verification",
                "endpoint": "/analysis/verify",
                "description": "Verify if document is a valid financial record"
            }
        ]
    }
