import os
import hashlib
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from app.models.database import DocumentRepository, AnalysisReportRepository

logger = logging.getLogger(__name__)


class Document:
    """Document model for file management"""
    
    def __init__(self, document_repo: DocumentRepository):
        self.document_repo = document_repo
    
    def create_document(self, user_id: int, original_name: str, file_content: bytes, 
                       upload_path: str = "data/") -> Dict[str, Any]:
        """Create a new document record and save file"""
        try:
            # Ensure upload directory exists
            os.makedirs(upload_path, exist_ok=True)
            
            # Sanitize filename
            sanitized_name = self._sanitize_filename(original_name)
            
            # Generate unique filename to prevent conflicts
            base_name, ext = os.path.splitext(sanitized_name)
            stored_name = f"{base_name}_{user_id}_{hashlib.md5(file_content).hexdigest()[:8]}{ext}"
            
            # Full file path
            file_path = os.path.join(upload_path, stored_name)
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Calculate checksum
            checksum = hashlib.sha256(file_content).hexdigest()
            
            # Create database record
            document_id = self.document_repo.create_document(
                user_id=user_id,
                original_name=original_name,
                stored_name=stored_name,
                path=file_path,
                size_bytes=len(file_content),
                checksum=checksum
            )
            
            # Fetch the created document to get full data including timestamps
            created_doc = self.document_repo.get_document(document_id, user_id)
            if created_doc:
                return created_doc
            else:
                # Fallback if get_document fails
                return {
                    "id": document_id,
                    "user_id": user_id,
                    "original_name": original_name,
                    "stored_name": stored_name,
                    "path": file_path,
                    "size_bytes": len(file_content),
                    "checksum": checksum,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    def get_document(self, document_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get document by ID for a user"""
        try:
            return self.document_repo.get_document(document_id, user_id)
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise
    
    def get_user_documents(self, user_id: int, search_query: Optional[str] = None,
                          limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get documents for a user with optional search"""
        try:
            return self.document_repo.get_user_documents(user_id, search_query, limit, offset)
        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            raise
    
    def delete_document(self, document_id: int, user_id: int) -> bool:
        """Delete document and its file"""
        try:
            # Get document data first
            document_data = self.document_repo.get_document(document_id, user_id)
            if not document_data:
                return False
            
            # Delete file if it exists
            if os.path.exists(document_data['path']):
                try:
                    os.remove(document_data['path'])
                except Exception as e:
                    logger.warning(f"Could not delete file {document_data['path']}: {str(e)}")
            
            # Delete from database
            return self.document_repo.delete_document(document_id, user_id)
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def get_documents_count(self, user_id: int) -> int:
        """Get total count of documents for a user"""
        try:
            return self.document_repo.get_documents_count(user_id)
        except Exception as e:
            logger.error(f"Error getting documents count: {str(e)}")
            raise
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent security issues"""
        # Remove or replace dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed_file"
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        return filename


class AnalysisReport:
    """Analysis report model for managing analysis results"""
    
    def __init__(self, report_repo: AnalysisReportRepository):
        self.report_repo = report_repo
    
    def create_report(self, user_id: int, analysis_type: str, query: str, file_name: str,
                     analysis_result: str, document_id: Optional[int] = None,
                     output_dir: str = "outputs") -> Dict[str, Any]:
        """Create a new analysis report and save to filesystem"""
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate unique report filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"{analysis_type}_{user_id}_{timestamp}.md"
            report_path = os.path.join(output_dir, report_filename)
            
            # Save analysis result to file as Markdown
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"# {analysis_type.title()} Analysis Report\n\n")
                f.write(f"**Query:** {query}\n\n")
                f.write(f"**Original File:** {file_name}\n\n")
                f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")
                f.write(str(analysis_result))
            
            # Create summary (first 200 characters)
            summary = str(analysis_result)[:200] + "..." if len(str(analysis_result)) > 200 else str(analysis_result)
            
            # Save to database
            report_id = self.report_repo.create_report(
                user_id=user_id,
                analysis_type=analysis_type,
                query=query,
                file_name=file_name,
                report_path=report_path,
                document_id=document_id,
                summary=summary,
                status="completed"
            )
            
            # Fetch the complete report data from database to get all fields
            report_data = self.report_repo.get_report(report_id, user_id)
            if report_data:
                return report_data
            else:
                # Fallback if get_report fails
                return {
                    "id": report_id,
                    "user_id": user_id,
                    "analysis_type": analysis_type,
                    "query": query,
                    "file_name": file_name,
                    "report_path": report_path,
                    "document_id": document_id,
                    "summary": summary,
                    "status": "completed",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error creating analysis report: {str(e)}")
            raise
    
    def get_report(self, report_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get analysis report by ID for a user"""
        try:
            return self.report_repo.get_report(report_id, user_id)
        except Exception as e:
            logger.error(f"Error getting analysis report: {str(e)}")
            raise
    
    def get_user_reports(self, user_id: int, analysis_type: Optional[str] = None,
                        search_query: Optional[str] = None, limit: int = 50,
                        offset: int = 0) -> List[Dict[str, Any]]:
        """Get analysis reports for a user with filtering"""
        try:
            return self.report_repo.get_user_reports(user_id, analysis_type, search_query, limit, offset)
        except Exception as e:
            logger.error(f"Error getting user analysis reports: {str(e)}")
            raise
    
    def update_report(self, report_id: int, user_id: int, **kwargs) -> bool:
        """Update analysis report"""
        try:
            return self.report_repo.update_report(report_id, user_id, **kwargs)
        except Exception as e:
            logger.error(f"Error updating analysis report: {str(e)}")
            raise
    
    def delete_report(self, report_id: int, user_id: int) -> bool:
        """Delete analysis report and its file"""
        try:
            # Get report data first
            report_data = self.report_repo.get_report(report_id, user_id)
            if not report_data:
                return False
            
            # Delete file if it exists
            if os.path.exists(report_data['report_path']):
                try:
                    os.remove(report_data['report_path'])
                except Exception as e:
                    logger.warning(f"Could not delete file {report_data['report_path']}: {str(e)}")
            
            # Delete from database
            return self.report_repo.delete_report(report_id, user_id)
        except Exception as e:
            logger.error(f"Error deleting analysis report: {str(e)}")
            raise
    
    def get_reports_count(self, user_id: int, analysis_type: Optional[str] = None) -> int:
        """Get total count of reports for a user"""
        try:
            return self.report_repo.get_reports_count(user_id, analysis_type)
        except Exception as e:
            logger.error(f"Error getting analysis reports count: {str(e)}")
            raise
