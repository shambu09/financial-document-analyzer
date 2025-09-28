from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import FileResponse
from typing import Optional, List
import os
import math

from app.models.auth import DatabaseManager, AnalysisReport, User
from app.api.routers.auth import get_current_active_user, get_current_admin_user
from app.models.schemas import (
    AnalysisReportResponse, 
    AnalysisReportListResponse, 
    AnalysisReportSearchParams,
    AnalysisReportUpdate
)

router = APIRouter(prefix="/reports", tags=["reports"])

# Initialize database manager
db_manager = DatabaseManager()
analysis_reports = AnalysisReport(db_manager)


@router.get("/", response_model=AnalysisReportListResponse)
async def list_reports(
    analysis_type: Optional[str] = Query(None, description="Filter by analysis type"),
    search_query: Optional[str] = Query(None, description="Search in file names, queries, and summaries"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of reports per page"),
    current_user: User = Depends(get_current_active_user)
):
    """List analysis reports for the current user with optional filtering and pagination"""
    
    offset = (page - 1) * page_size
    
    try:
        # Get reports from database
        reports_data = analysis_reports.get_user_reports(
            user_id=current_user.id,
            analysis_type=analysis_type,
            search_query=search_query,
            limit=page_size,
            offset=offset
        )
        
        # Get total count for pagination
        total_count = analysis_reports.get_reports_count(
            user_id=current_user.id,
            analysis_type=analysis_type
        )
        
        # Convert to response format
        reports = []
        for report_data in reports_data:
            # Generate download URL
            download_url = f"/reports/{report_data['id']}/download" if os.path.exists(report_data['report_path']) else None
            
            report = AnalysisReportResponse(
                id=report_data['id'],
                user_id=report_data['user_id'],
                document_id=report_data['document_id'],
                analysis_type=report_data['analysis_type'],
                query=report_data['query'],
                file_name=report_data['file_name'],
                report_path=report_data['report_path'],
                status=report_data['status'],
                summary=report_data['summary'],
                created_at=report_data['created_at'],
                updated_at=report_data['updated_at'],
                download_url=download_url
            )
            reports.append(report)
        
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
        
        return AnalysisReportListResponse(
            reports=reports,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reports: {str(e)}")


@router.get("/{report_id}", response_model=AnalysisReportResponse)
async def get_report(
    report_id: int = Path(..., description="Report ID"),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific analysis report by ID"""
    
    try:
        report_data = analysis_reports.get_report(report_id, current_user.id)
        
        if not report_data:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Generate download URL
        download_url = f"/reports/{report_data['id']}/download" if os.path.exists(report_data['report_path']) else None
        
        return AnalysisReportResponse(
            id=report_data['id'],
            user_id=report_data['user_id'],
            document_id=report_data['document_id'],
            analysis_type=report_data['analysis_type'],
            query=report_data['query'],
            file_name=report_data['file_name'],
            report_path=report_data['report_path'],
            status=report_data['status'],
            summary=report_data['summary'],
            created_at=report_data['created_at'],
            updated_at=report_data['updated_at'],
            download_url=download_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving report: {str(e)}")


@router.get("/{report_id}/download")
async def download_report(
    report_id: int = Path(..., description="Report ID"),
    current_user: User = Depends(get_current_active_user)
):
    """Download an analysis report file"""
    
    try:
        report_data = analysis_reports.get_report(report_id, current_user.id)
        
        if not report_data:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_path = report_data['report_path']
        
        if not os.path.exists(report_path):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        # Return the file
        return FileResponse(
            path=report_path,
            filename=report_data['file_name'],
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading report: {str(e)}")


@router.put("/{report_id}", response_model=AnalysisReportResponse)
async def update_report(
    report_id: int = Path(..., description="Report ID"),
    update_data: AnalysisReportUpdate = ...,
    current_user: User = Depends(get_current_active_user)
):
    """Update an analysis report (currently only summary can be updated)"""
    
    try:
        # Check if report exists and belongs to user
        report_data = analysis_reports.get_report(report_id, current_user.id)
        if not report_data:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Update summary if provided
        if update_data.summary is not None:
            success = analysis_reports.update_report_summary(
                report_id, current_user.id, update_data.summary
            )
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update report")
        
        # Get updated report data
        updated_report_data = analysis_reports.get_report(report_id, current_user.id)
        
        # Generate download URL
        download_url = f"/reports/{updated_report_data['id']}/download" if os.path.exists(updated_report_data['report_path']) else None
        
        return AnalysisReportResponse(
            id=updated_report_data['id'],
            user_id=updated_report_data['user_id'],
            document_id=updated_report_data['document_id'],
            analysis_type=updated_report_data['analysis_type'],
            query=updated_report_data['query'],
            file_name=updated_report_data['file_name'],
            report_path=updated_report_data['report_path'],
            status=updated_report_data['status'],
            summary=updated_report_data['summary'],
            created_at=updated_report_data['created_at'],
            updated_at=updated_report_data['updated_at'],
            download_url=download_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating report: {str(e)}")


@router.delete("/{report_id}")
async def delete_report(
    report_id: int = Path(..., description="Report ID"),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an analysis report and its associated file"""
    
    try:
        # Get report data first to get file path
        report_data = analysis_reports.get_report(report_id, current_user.id)
        if not report_data:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Delete from database
        success = analysis_reports.delete_report(report_id, current_user.id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete report from database")
        
        # Delete file if it exists
        report_path = report_data['report_path']
        if os.path.exists(report_path):
            try:
                os.remove(report_path)
            except Exception as e:
                # Log error but don't fail the request since DB record is already deleted
                print(f"Warning: Could not delete file {report_path}: {str(e)}")
        
        return {"message": "Report deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting report: {str(e)}")


@router.get("/stats/summary")
async def get_reports_stats(
    current_user: User = Depends(get_current_active_user)
):
    """Get summary statistics for user's analysis reports"""
    
    try:
        # Get counts by analysis type
        comprehensive_count = analysis_reports.get_reports_count(current_user.id, "comprehensive")
        investment_count = analysis_reports.get_reports_count(current_user.id, "investment")
        risk_count = analysis_reports.get_reports_count(current_user.id, "risk")
        verification_count = analysis_reports.get_reports_count(current_user.id, "verification")
        total_count = analysis_reports.get_reports_count(current_user.id)
        
        return {
            "total_reports": total_count,
            "by_analysis_type": {
                "comprehensive": comprehensive_count,
                "investment": investment_count,
                "risk": risk_count,
                "verification": verification_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")


@router.delete("/admin/{report_id}")
async def admin_delete_report(
    report_id: int = Path(..., description="Report ID"),
    current_user: User = Depends(get_current_admin_user)
):
    """Admin endpoint to delete any analysis report"""
    
    try:
        # Get report data first to get file path
        report_data = analysis_reports.get_report(report_id, 1)  # Use admin user ID
        if not report_data:
            # Try to get report with any user ID (admin override)
            with db_manager.db_path as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM analysis_reports WHERE id = ?",
                    (report_id,)
                )
                report_data = cursor.fetchone()
                if not report_data:
                    raise HTTPException(status_code=404, detail="Report not found")
        
        # Delete from database
        success = analysis_reports.delete_report(report_id, 1)  # Use admin user ID
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete report from database")
        
        # Delete file if it exists
        report_path = report_data['report_path'] if isinstance(report_data, dict) else report_data[6]
        if os.path.exists(report_path):
            try:
                os.remove(report_path)
            except Exception as e:
                print(f"Warning: Could not delete file {report_path}: {str(e)}")
        
        return {"message": "Report deleted successfully by admin"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting report: {str(e)}")

