"""
Background Tasks for Analysis Processing
======================================

This module handles background processing of financial document analysis
to prevent blocking the main FastAPI application.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor

from crewai import Crew, Process
from app.domain.agents import financial_analyst, investment_advisor, risk_assessor, verifier
from app.domain.task import analyze_financial_document, investment_analysis, risk_assessment, verification
from app.models.factory import get_analysis_report_model
from app.models.schemas import ReportStatus

logger = logging.getLogger(__name__)


def _run_crew_sync(agents, tasks, query: str, file_path: str):
    """Run CrewAI crew synchronously in a thread pool"""
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
    )
    return crew.kickoff(inputs={"query": query, "file_path": file_path})


async def process_comprehensive_analysis(
    report_id: str,
    query: str,
    file_path: str,
    file_name: str,
    user_id: str,
    document_id: Optional[str] = None
) -> None:
    """Process comprehensive analysis in the background"""
    analysis_reports = get_analysis_report_model()
    
    try:
        # Update status to in_progress
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary="Analysis in progress...",
            status=ReportStatus.IN_PROGRESS.value
        )
        
        # Run crew analysis in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                _run_crew_sync,
                [financial_analyst],
                [analyze_financial_document],
                query,
                file_path
            )
        
        # Generate report file
        report_filename = f"comprehensive_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join("outputs", report_filename)
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        
        # Write report to file
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Comprehensive Analysis Report\n\n")
            f.write("---\n\n")
            f.write("## Report Information\n\n")
            f.write(f"**Query:** {query}\n\n")
            f.write(f"**Original File:** {file_name}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("---\n\n")
            f.write("## Analysis Results\n\n")
            f.write(str(result))
        
        # Update report with results
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=str(result),
            status=ReportStatus.COMPLETED.value,
            report_path=report_path
        )
        
        logger.info(f"Comprehensive analysis completed for report {report_id}")
        
    except Exception as e:
        logger.error(f"Error processing comprehensive analysis for report {report_id}: {str(e)}")
        
        # Update status to failed
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=f"Analysis failed: {str(e)}",
            status=ReportStatus.FAILED.value
        )


async def process_investment_analysis(
    report_id: str,
    query: str,
    file_path: str,
    file_name: str,
    user_id: str,
    document_id: Optional[str] = None
) -> None:
    """Process investment analysis in the background"""
    analysis_reports = get_analysis_report_model()
    
    try:
        # Update status to in_progress
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary="Investment analysis in progress...",
            status=ReportStatus.IN_PROGRESS.value
        )
        
        # Run crew analysis in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                _run_crew_sync,
                [investment_advisor],
                [investment_analysis],
                query,
                file_path
            )
        
        # Generate report file
        report_filename = f"investment_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join("outputs", report_filename)
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        
        # Write report to file
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Investment Analysis Report\n\n")
            f.write("---\n\n")
            f.write("## Report Information\n\n")
            f.write(f"**Query:** {query}\n\n")
            f.write(f"**Original File:** {file_name}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("---\n\n")
            f.write("## Investment Analysis Results\n\n")
            f.write(str(result))
        
        # Update report with results
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=str(result),
            status=ReportStatus.COMPLETED.value,
            report_path=report_path
        )
        
        logger.info(f"Investment analysis completed for report {report_id}")
        
    except Exception as e:
        logger.error(f"Error processing investment analysis for report {report_id}: {str(e)}")
        
        # Update status to failed
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=f"Investment analysis failed: {str(e)}",
            status=ReportStatus.FAILED.value
        )


async def process_risk_analysis(
    report_id: str,
    query: str,
    file_path: str,
    file_name: str,
    user_id: str,
    document_id: Optional[str] = None
) -> None:
    """Process risk analysis in the background"""
    analysis_reports = get_analysis_report_model()
    
    try:
        # Update status to in_progress
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary="Risk analysis in progress...",
            status=ReportStatus.IN_PROGRESS.value
        )
        
        # Run crew analysis in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                _run_crew_sync,
                [risk_assessor],
                [risk_assessment],
                query,
                file_path
            )
        
        # Generate report file
        report_filename = f"risk_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join("outputs", report_filename)
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        
        # Write report to file
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Risk Analysis Report\n\n")
            f.write("---\n\n")
            f.write("## Report Information\n\n")
            f.write(f"**Query:** {query}\n\n")
            f.write(f"**Original File:** {file_name}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("---\n\n")
            f.write("## Risk Analysis Results\n\n")
            f.write(str(result))
        
        # Update report with results
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=str(result),
            status=ReportStatus.COMPLETED.value,
            report_path=report_path
        )
        
        logger.info(f"Risk analysis completed for report {report_id}")
        
    except Exception as e:
        logger.error(f"Error processing risk analysis for report {report_id}: {str(e)}")
        
        # Update status to failed
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=f"Risk analysis failed: {str(e)}",
            status=ReportStatus.FAILED.value
        )


async def process_verification_analysis(
    report_id: str,
    query: str,
    file_path: str,
    file_name: str,
    user_id: str,
    document_id: Optional[str] = None
) -> None:
    """Process verification analysis in the background"""
    analysis_reports = get_analysis_report_model()
    
    try:
        # Update status to in_progress
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary="Verification analysis in progress...",
            status=ReportStatus.IN_PROGRESS.value
        )
        
        # Run crew analysis in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                _run_crew_sync,
                [verifier],
                [verification],
                query,
                file_path
            )
        
        # Generate report file
        report_filename = f"verification_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join("outputs", report_filename)
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        
        # Write report to file
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Verification Analysis Report\n\n")
            f.write("---\n\n")
            f.write("## Report Information\n\n")
            f.write(f"**Query:** {query}\n\n")
            f.write(f"**Original File:** {file_name}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("---\n\n")
            f.write("## Verification Analysis Results\n\n")
            f.write(str(result))
        
        # Update report with results
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=str(result),
            status=ReportStatus.COMPLETED.value,
            report_path=report_path
        )
        
        logger.info(f"Verification analysis completed for report {report_id}")
        
    except Exception as e:
        logger.error(f"Error processing verification analysis for report {report_id}: {str(e)}")
        
        # Update status to failed
        analysis_reports.update_report(
            report_id=report_id,
            user_id=user_id,
            summary=f"Verification analysis failed: {str(e)}",
            status=ReportStatus.FAILED.value
        )


def get_analysis_task(analysis_type: str):
    """Get the appropriate background task function for the analysis type"""
    task_map = {
        "comprehensive": process_comprehensive_analysis,
        "investment": process_investment_analysis,
        "risk": process_risk_analysis,
        "verification": process_verification_analysis,
    }
    
    if analysis_type not in task_map:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    return task_map[analysis_type]
