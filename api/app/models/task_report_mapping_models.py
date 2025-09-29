import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.database import TaskReportMappingRepository

logger = logging.getLogger(__name__)


class TaskReportMapping:
    """Task-Report Mapping model for managing task-report relationships"""
    
    def __init__(self, mapping_repo: TaskReportMappingRepository):
        self.mapping_repo = mapping_repo
    
    def create_mapping(self, task_id: str, report_id: str, user_id: str, analysis_type: str) -> Dict[str, Any]:
        """Create a new task-report mapping"""
        try:
            mapping_id = self.mapping_repo.create_mapping(
                task_id=task_id,
                report_id=report_id,
                user_id=user_id,
                analysis_type=analysis_type
            )
            
            # Fetch the created mapping to get full data including timestamps
            mapping_data = self.mapping_repo.get_mapping_by_task_id(task_id)
            if mapping_data:
                return mapping_data
            else:
                # Fallback if get_mapping_by_task_id fails
                return {
                    "id": mapping_id,
                    "task_id": task_id,
                    "report_id": report_id,
                    "user_id": user_id,
                    "analysis_type": analysis_type,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error creating task-report mapping: {str(e)}")
            raise
    
    def get_mapping_by_task_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get mapping by task ID"""
        try:
            return self.mapping_repo.get_mapping_by_task_id(task_id)
        except Exception as e:
            logger.error(f"Error getting mapping by task ID: {str(e)}")
            raise
    
    def get_mapping_by_report_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get mapping by report ID"""
        try:
            return self.mapping_repo.get_mapping_by_report_id(report_id)
        except Exception as e:
            logger.error(f"Error getting mapping by report ID: {str(e)}")
            raise
    
    def get_user_mappings(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get task-report mappings for a user"""
        try:
            return self.mapping_repo.get_user_mappings(user_id, limit, offset)
        except Exception as e:
            logger.error(f"Error getting user mappings: {str(e)}")
            raise
    
    def delete_mapping(self, mapping_id: str) -> bool:
        """Delete task-report mapping"""
        try:
            return self.mapping_repo.delete_mapping(mapping_id)
        except Exception as e:
            logger.error(f"Error deleting mapping: {str(e)}")
            raise
    
    def delete_mapping_by_task_id(self, task_id: str) -> bool:
        """Delete mapping by task ID"""
        try:
            return self.mapping_repo.delete_mapping_by_task_id(task_id)
        except Exception as e:
            logger.error(f"Error deleting mapping by task ID: {str(e)}")
            raise
    
    def delete_mapping_by_report_id(self, report_id: str) -> bool:
        """Delete mapping by report ID"""
        try:
            return self.mapping_repo.delete_mapping_by_report_id(report_id)
        except Exception as e:
            logger.error(f"Error deleting mapping by report ID: {str(e)}")
            raise
    
    def cleanup_old_mappings(self, days_old: int = 30) -> int:
        """Clean up old mappings and return count of cleaned mappings"""
        try:
            return self.mapping_repo.cleanup_old_mappings(days_old)
        except Exception as e:
            logger.error(f"Error cleaning up old mappings: {str(e)}")
            raise
