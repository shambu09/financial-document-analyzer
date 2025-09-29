"""
Celery Task Definitions
======================

This module contains all Celery tasks for background processing of financial document analysis.
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from celery import current_task
from celery.exceptions import Retry

from app.celery_app import celery_app, TaskStatus
from app.domain.agents import financial_analyst, investment_advisor, risk_assessor, verifier
from app.domain.task import analyze_financial_document, investment_analysis, risk_assessment, verification
from app.models.factory import get_analysis_report_model
from app.models.schemas import ReportStatus

logger = logging.getLogger(__name__)


def _run_crew_sync(agents, tasks, query: str, file_path: str):
    """Run CrewAI crew synchronously"""
    from crewai import Crew, Process
    
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
    )
    return crew.kickoff(inputs={"query": query, "file_path": file_path})


def _update_task_progress(progress: int, message: str = ""):
    """Update task progress"""
    if current_task:
        current_task.update_state(
            state=TaskStatus.STARTED,
            meta={'progress': progress, 'message': message}
        )


def _generate_report_file(analysis_type: str, user_id: str, query: str, file_name: str, result: str) -> str:
    """Generate report file and return the path"""
    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)
    
    # Generate report filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"{analysis_type}_{user_id}_{timestamp}.md"
    report_path = os.path.join("outputs", report_filename)
    
    # Write report to file
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# {analysis_type.title()} Analysis Report\n\n")
        f.write("---\n\n")
        f.write("## Report Information\n\n")
        f.write(f"**Query:** {query}\n\n")
        f.write(f"**Original File:** {file_name}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        f.write("---\n\n")
        f.write(f"## {analysis_type.title()} Analysis Results\n\n")
        f.write(str(result))
    
    return report_path


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_comprehensive_analysis(self, report_id: str, query: str, file_path: str, file_name: str, user_id: str, document_id: Optional[str] = None):
    """Process comprehensive analysis in the background using Celery"""
    analysis_reports = get_analysis_report_model()
    
    try:
        _update_task_progress(10, "Starting comprehensive analysis...")
        
        # Update status to in_progress
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary="Analysis in progress...",
            status=ReportStatus.IN_PROGRESS.value
        )
        
        _update_task_progress(30, "Running AI analysis...")
        
        # Run crew analysis
        result = _run_crew_sync(
            [financial_analyst],
            [analyze_financial_document],
            query,
            file_path
        )
        
        _update_task_progress(70, "Generating report...")
        
        # Generate report file
        report_path = _generate_report_file(
            "comprehensive", user_id, query, file_name, str(result)
        )
        
        _update_task_progress(90, "Saving results...")
        
        # Update report with results
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=str(result),
            status=ReportStatus.COMPLETED.value,
            report_path=report_path
        )
        
        _update_task_progress(100, "Analysis completed successfully")
        
        logger.info(f"Comprehensive analysis completed for report {report_id}")
        
        return {
            "status": "success",
            "report_id": report_id,
            "result": str(result),
            "report_path": report_path
        }
        
    except Exception as exc:
        logger.error(f"Error processing comprehensive analysis for report {report_id}: {str(exc)}")
        
        # Update status to failed
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=f"Analysis failed: {str(exc)}",
            status=ReportStatus.FAILED.value
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_investment_analysis(self, report_id: str, query: str, file_path: str, file_name: str, user_id: str, document_id: Optional[str] = None):
    """Process investment analysis in the background using Celery"""
    analysis_reports = get_analysis_report_model()
    
    try:
        _update_task_progress(10, "Starting investment analysis...")
        
        # Update status to in_progress
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary="Investment analysis in progress...",
            status=ReportStatus.IN_PROGRESS.value
        )
        
        _update_task_progress(30, "Running AI analysis...")
        
        # Run crew analysis
        result = _run_crew_sync(
            [investment_advisor],
            [investment_analysis],
            query,
            file_path
        )
        
        _update_task_progress(70, "Generating report...")
        
        # Generate report file
        report_path = _generate_report_file(
            "investment", user_id, query, file_name, str(result)
        )
        
        _update_task_progress(90, "Saving results...")
        
        # Update report with results
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=str(result),
            status=ReportStatus.COMPLETED.value,
            report_path=report_path
        )
        
        _update_task_progress(100, "Investment analysis completed successfully")
        
        logger.info(f"Investment analysis completed for report {report_id}")
        
        return {
            "status": "success",
            "report_id": report_id,
            "result": str(result),
            "report_path": report_path
        }
        
    except Exception as exc:
        logger.error(f"Error processing investment analysis for report {report_id}: {str(exc)}")
        
        # Update status to failed
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=f"Investment analysis failed: {str(exc)}",
            status=ReportStatus.FAILED.value
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_risk_analysis(self, report_id: str, query: str, file_path: str, file_name: str, user_id: str, document_id: Optional[str] = None):
    """Process risk analysis in the background using Celery"""
    analysis_reports = get_analysis_report_model()
    
    try:
        _update_task_progress(10, "Starting risk analysis...")
        
        # Update status to in_progress
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary="Risk analysis in progress...",
            status=ReportStatus.IN_PROGRESS.value
        )
        
        _update_task_progress(30, "Running AI analysis...")
        
        # Run crew analysis
        result = _run_crew_sync(
            [risk_assessor],
            [risk_assessment],
            query,
            file_path
        )
        
        _update_task_progress(70, "Generating report...")
        
        # Generate report file
        report_path = _generate_report_file(
            "risk", user_id, query, file_name, str(result)
        )
        
        _update_task_progress(90, "Saving results...")
        
        # Update report with results
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=str(result),
            status=ReportStatus.COMPLETED.value,
            report_path=report_path
        )
        
        _update_task_progress(100, "Risk analysis completed successfully")
        
        logger.info(f"Risk analysis completed for report {report_id}")
        
        return {
            "status": "success",
            "report_id": report_id,
            "result": str(result),
            "report_path": report_path
        }
        
    except Exception as exc:
        logger.error(f"Error processing risk analysis for report {report_id}: {str(exc)}")
        
        # Update status to failed
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=f"Risk analysis failed: {str(exc)}",
            status=ReportStatus.FAILED.value
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_verification_analysis(self, report_id: str, query: str, file_path: str, file_name: str, user_id: str, document_id: Optional[str] = None):
    """Process verification analysis in the background using Celery"""
    analysis_reports = get_analysis_report_model()
    
    try:
        _update_task_progress(10, "Starting verification analysis...")
        
        # Update status to in_progress
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary="Verification analysis in progress...",
            status=ReportStatus.IN_PROGRESS.value
        )
        
        _update_task_progress(30, "Running AI analysis...")
        
        # Run crew analysis
        result = _run_crew_sync(
            [verifier],
            [verification],
            query,
            file_path
        )
        
        _update_task_progress(70, "Generating report...")
        
        # Generate report file
        report_path = _generate_report_file(
            "verification", user_id, query, file_name, str(result)
        )
        
        _update_task_progress(90, "Saving results...")
        
        # Update report with results
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=str(result),
            status=ReportStatus.COMPLETED.value,
            report_path=report_path
        )
        
        _update_task_progress(100, "Verification analysis completed successfully")
        
        logger.info(f"Verification analysis completed for report {report_id}")
        
        return {
            "status": "success",
            "report_id": report_id,
            "result": str(result),
            "report_path": report_path
        }
        
    except Exception as exc:
        logger.error(f"Error processing verification analysis for report {report_id}: {str(exc)}")
        
        # Update status to failed
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=f"Verification analysis failed: {str(exc)}",
            status=ReportStatus.FAILED.value
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# Task mapping for easy access
TASK_MAP = {
    "comprehensive": process_comprehensive_analysis,
    "investment": process_investment_analysis,
    "risk": process_risk_analysis,
    "verification": process_verification_analysis,
}


def get_celery_task(analysis_type: str):
    """Get the appropriate Celery task for the analysis type"""
    if analysis_type not in TASK_MAP:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    return TASK_MAP[analysis_type]
