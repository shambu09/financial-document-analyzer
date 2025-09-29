from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from math import ceil

from app.api.routers.auth import get_current_active_user
from app.models.factory import get_task_report_mapping_model
from app.models.schemas import TaskReportMappingResponse, TaskReportMappingListResponse

router = APIRouter(prefix="/task-mappings", tags=["task-mappings"])


@router.get("/by-task/{task_id}", response_model=TaskReportMappingResponse)
async def get_mapping_by_task_id(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get task-report mapping by task ID"""
    try:
        mapping_model = get_task_report_mapping_model()
        mapping = mapping_model.get_mapping_by_task_id(task_id)
        
        if not mapping:
            raise HTTPException(status_code=404, detail="Task mapping not found")
        
        # Verify user owns this mapping
        if mapping["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return mapping
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task mapping: {str(e)}")


@router.get("/by-report/{report_id}", response_model=TaskReportMappingResponse)
async def get_mapping_by_report_id(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get task-report mapping by report ID"""
    try:
        mapping_model = get_task_report_mapping_model()
        mapping = mapping_model.get_mapping_by_report_id(report_id)
        
        if not mapping:
            raise HTTPException(status_code=404, detail="Report mapping not found")
        
        # Verify user owns this mapping
        if mapping["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return mapping
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving report mapping: {str(e)}")


@router.get("/", response_model=TaskReportMappingListResponse)
async def get_user_mappings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get task-report mappings for the current user"""
    try:
        mapping_model = get_task_report_mapping_model()
        offset = (page - 1) * page_size
        
        mappings = mapping_model.get_user_mappings(
            user_id=current_user["id"],
            limit=page_size,
            offset=offset
        )
        
        # Get total count (simplified - in production you might want a separate count method)
        total_mappings = len(mapping_model.get_user_mappings(
            user_id=current_user["id"],
            limit=1000,  # Get a large number to count
            offset=0
        ))
        
        total_pages = ceil(total_mappings / page_size) if total_mappings > 0 else 1
        
        return TaskReportMappingListResponse(
            mappings=mappings,
            total=total_mappings,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user mappings: {str(e)}")


@router.delete("/by-task/{task_id}")
async def delete_mapping_by_task_id(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete task-report mapping by task ID"""
    try:
        mapping_model = get_task_report_mapping_model()
        
        # First check if mapping exists and user owns it
        mapping = mapping_model.get_mapping_by_task_id(task_id)
        if not mapping:
            raise HTTPException(status_code=404, detail="Task mapping not found")
        
        if mapping["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete the mapping
        success = mapping_model.delete_mapping_by_task_id(task_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete mapping")
        
        return {"message": "Task mapping deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task mapping: {str(e)}")


@router.delete("/by-report/{report_id}")
async def delete_mapping_by_report_id(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete task-report mapping by report ID"""
    try:
        mapping_model = get_task_report_mapping_model()
        
        # First check if mapping exists and user owns it
        mapping = mapping_model.get_mapping_by_report_id(report_id)
        if not mapping:
            raise HTTPException(status_code=404, detail="Report mapping not found")
        
        if mapping["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete the mapping
        success = mapping_model.delete_mapping_by_report_id(report_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete mapping")
        
        return {"message": "Report mapping deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting report mapping: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_mappings(
    days_old: int = Query(30, ge=1, le=365, description="Number of days old to clean up"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Clean up old task-report mappings (admin only)"""
    try:
        # Check if user is admin
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        mapping_model = get_task_report_mapping_model()
        cleaned_count = mapping_model.cleanup_old_mappings(days_old)
        
        return {
            "message": f"Cleaned up {cleaned_count} old mappings",
            "cleaned_count": cleaned_count,
            "days_old": days_old
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up mappings: {str(e)}")
