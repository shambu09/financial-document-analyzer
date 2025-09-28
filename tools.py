"""
Financial Document Analyzer Tools
================================

This module provides tools for financial document analysis, including PDF processing,
investment analysis, risk assessment, and financial metrics extraction.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv

from crewai_tools import tool
from crewai_tools.tools.serper_dev_tool import SerperDevTool
from langchain_community.document_loaders import PyPDFLoader

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create search tool
search_tool = SerperDevTool()


@tool("read_financial_document")
def read_financial_document(path: str = 'data/sample.pdf') -> str:
    """
    Reads and processes a financial document from a PDF file.
    
    Args:
        path (str): Path to the PDF file to read
        
    Returns:
        str: Cleaned and formatted text content from the financial document
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error processing the PDF
    """
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"PDF file not found: {path}")
            
        if not path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF document")
        
        logger.info(f"Processing PDF file: {path}")
        loader = PyPDFLoader(path)
        docs = loader.load()
        
        if not docs:
            return "No content found in the PDF document"
        
        full_report = ""
        for i, doc in enumerate(docs):
            content = doc.page_content.strip()
            
            # Enhanced text cleaning
            content = _clean_financial_text(content)
            
            # Add page separator for better readability
            if i > 0:
                full_report += f"\n\n--- Page {i + 1} ---\n\n"
            
            full_report += content + "\n"
        
        logger.info(f"Successfully processed {len(docs)} pages from {path}")
        return full_report.strip()
        
    except Exception as e:
        logger.error(f"Error processing PDF {path}: {str(e)}")
        raise Exception(f"Failed to process PDF document: {str(e)}")


@tool("analyze_investment_opportunities")
def analyze_investment_opportunities(financial_document_data: str) -> str:
    """
    Analyzes financial document data to identify investment opportunities and risks.
    
    Args:
        financial_document_data (str): Text content from financial documents
        
    Returns:
        str: Structured investment analysis with opportunities and recommendations
    """
    try:
        # Extract key financial metrics
        metrics = _extract_financial_metrics(financial_document_data)
        
        # Analyze financial health
        health_score = _calculate_financial_health_score(metrics)
        
        # Generate investment recommendations
        recommendations = _generate_investment_recommendations(metrics, health_score)
        
        analysis = f"""
## Investment Analysis Report

### Financial Health Score: {health_score}/10

### Key Financial Metrics:
{_format_metrics(metrics)}

### Investment Opportunities:
{recommendations['opportunities']}

### Risk Factors:
{recommendations['risks']}

### Recommendations:
{recommendations['recommendations']}

### Market Context:
{_get_market_context(metrics)}
"""
        
        return analysis.strip()
        
    except Exception as e:
        logger.error(f"Error in investment analysis: {str(e)}")
        return f"Investment analysis failed: {str(e)}"


@tool("assess_financial_risks")
def assess_financial_risks(financial_document_data: str) -> str:
    """
    Assesses financial risks based on document data.
    
    Args:
        financial_document_data (str): Text content from financial documents
        
    Returns:
        str: Comprehensive risk assessment report
    """
    try:
        # Extract financial metrics
        metrics = _extract_financial_metrics(financial_document_data)
        
        # Calculate risk scores
        risk_scores = _calculate_risk_scores(metrics)
        
        # Generate risk assessment
        risk_assessment = f"""
## Financial Risk Assessment Report

### Overall Risk Level: {risk_scores['overall_risk']}

### Risk Breakdown:
- **Liquidity Risk**: {risk_scores['liquidity_risk']} - {_get_risk_description('liquidity', risk_scores['liquidity_risk'])}
- **Credit Risk**: {risk_scores['credit_risk']} - {_get_risk_description('credit', risk_scores['credit_risk'])}
- **Market Risk**: {risk_scores['market_risk']} - {_get_risk_description('market', risk_scores['market_risk'])}
- **Operational Risk**: {risk_scores['operational_risk']} - {_get_risk_description('operational', risk_scores['operational_risk'])}

### Key Risk Indicators:
{_format_risk_indicators(metrics, risk_scores)}

### Risk Mitigation Strategies:
{_get_mitigation_strategies(risk_scores)}

### Scenario Analysis:
{_get_scenario_analysis(metrics, risk_scores)}
"""
        
        return risk_assessment.strip()
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {str(e)}")
        return f"Risk assessment failed: {str(e)}"


@tool("extract_financial_metrics")
def extract_financial_metrics(financial_document_data: str) -> str:
    """
    Extracts and calculates key financial metrics from document data.
    
    Args:
        financial_document_data (str): Text content from financial documents
        
    Returns:
        str: Formatted financial metrics and ratios
    """
    try:
        metrics = _extract_financial_metrics(financial_document_data)
        
        formatted_metrics = f"""
## Financial Metrics Summary

### Revenue Metrics:
- Total Revenue: {metrics.get('revenue', 'N/A')}
- Revenue Growth: {metrics.get('revenue_growth', 'N/A')}%

### Profitability Metrics:
- Net Income: {metrics.get('net_income', 'N/A')}
- Gross Profit Margin: {metrics.get('gross_margin', 'N/A')}%
- Net Profit Margin: {metrics.get('net_margin', 'N/A')}%
- ROE (Return on Equity): {metrics.get('roe', 'N/A')}%
- ROA (Return on Assets): {metrics.get('roa', 'N/A')}%

### Liquidity Metrics:
- Current Ratio: {metrics.get('current_ratio', 'N/A')}
- Quick Ratio: {metrics.get('quick_ratio', 'N/A')}
- Cash Position: {metrics.get('cash', 'N/A')}

### Leverage Metrics:
- Debt-to-Equity Ratio: {metrics.get('debt_to_equity', 'N/A')}
- Debt-to-Assets Ratio: {metrics.get('debt_to_assets', 'N/A')}
- Interest Coverage Ratio: {metrics.get('interest_coverage', 'N/A')}

### Efficiency Metrics:
- Asset Turnover: {metrics.get('asset_turnover', 'N/A')}
- Inventory Turnover: {metrics.get('inventory_turnover', 'N/A')}
- Days Sales Outstanding: {metrics.get('dso', 'N/A')} days
"""
        
        return formatted_metrics.strip()
        
    except Exception as e:
        logger.error(f"Error extracting financial metrics: {str(e)}")
        return f"Financial metrics extraction failed: {str(e)}"


# Legacy class-based tools for backward compatibility
class FinancialDocumentTool:
    """Legacy class wrapper for the read_financial_document tool."""
    
    @staticmethod
    def read_data_tool(path: str = 'data/sample.pdf') -> str:
        """Legacy method that calls the new tool function."""
        return read_financial_document(path)


class InvestmentTool:
    """Legacy class wrapper for investment analysis."""
    
    @staticmethod
    def analyze_investment_tool(financial_document_data: str) -> str:
        """Legacy method that calls the new tool function."""
        return analyze_investment_opportunities(financial_document_data)


class RiskTool:
    """Legacy class wrapper for risk assessment."""
    
    @staticmethod
    def create_risk_assessment_tool(financial_document_data: str) -> str:
        """Legacy method that calls the new tool function."""
        return assess_financial_risks(financial_document_data)


# Helper functions
def _clean_financial_text(text: str) -> str:
    """Clean and normalize financial text content."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize line breaks
    while '\n\n' in text:
        text = text.replace('\n\n', '\n')
    
    # Clean up common PDF artifacts
    text = re.sub(r'[^\w\s\.\,\;\:\-\+\$\%\(\)\[\]]', '', text)
    
    return text.strip()


def _extract_financial_metrics(text: str) -> Dict[str, Any]:
    """Extract financial metrics from text using regex patterns."""
    metrics = {}
    
    # Common financial patterns
    patterns = {
        'revenue': r'(?:revenue|sales|income)\s*:?\s*\$?([\d,\.]+)\s*(?:million|billion|thousand)?',
        'net_income': r'net\s+income\s*:?\s*\$?([\d,\.]+)\s*(?:million|billion|thousand)?',
        'total_assets': r'total\s+assets\s*:?\s*\$?([\d,\.]+)\s*(?:million|billion|thousand)?',
        'total_liabilities': r'total\s+liabilities\s*:?\s*\$?([\d,\.]+)\s*(?:million|billion|thousand)?',
        'cash': r'cash\s*(?:and\s*cash\s*equivalents)?\s*:?\s*\$?([\d,\.]+)\s*(?:million|billion|thousand)?',
        'debt': r'total\s+debt\s*:?\s*\$?([\d,\.]+)\s*(?:million|billion|thousand)?',
    }
    
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                # Convert to float, handling common suffixes
                value = matches[0].replace(',', '')
                if 'billion' in text.lower():
                    value = float(value) * 1000000000
                elif 'million' in text.lower():
                    value = float(value) * 1000000
                elif 'thousand' in text.lower():
                    value = float(value) * 1000
                else:
                    value = float(value)
                metrics[key] = value
            except (ValueError, InvalidOperation):
                continue
    
    # Calculate derived metrics
    if 'revenue' in metrics and 'net_income' in metrics and metrics['revenue'] > 0:
        metrics['net_margin'] = (metrics['net_income'] / metrics['revenue']) * 100
    
    if 'total_assets' in metrics and 'net_income' in metrics and metrics['total_assets'] > 0:
        metrics['roa'] = (metrics['net_income'] / metrics['total_assets']) * 100
    
    if 'total_liabilities' in metrics and 'total_assets' in metrics and metrics['total_assets'] > 0:
        metrics['debt_to_assets'] = metrics['total_liabilities'] / metrics['total_assets']
    
    return metrics


def _calculate_financial_health_score(metrics: Dict[str, Any]) -> int:
    """Calculate overall financial health score (1-10)."""
    score = 5  # Base score
    
    # Revenue growth
    if 'revenue_growth' in metrics:
        if metrics['revenue_growth'] > 10:
            score += 2
        elif metrics['revenue_growth'] > 5:
            score += 1
        elif metrics['revenue_growth'] < -5:
            score -= 2
    
    # Profitability
    if 'net_margin' in metrics:
        if metrics['net_margin'] > 15:
            score += 2
        elif metrics['net_margin'] > 5:
            score += 1
        elif metrics['net_margin'] < 0:
            score -= 2
    
    # Debt levels
    if 'debt_to_assets' in metrics:
        if metrics['debt_to_assets'] < 0.3:
            score += 1
        elif metrics['debt_to_assets'] > 0.7:
            score -= 1
    
    return max(1, min(10, score))


def _generate_investment_recommendations(metrics: Dict[str, Any], health_score: int) -> Dict[str, str]:
    """Generate investment recommendations based on metrics."""
    opportunities = []
    risks = []
    recommendations = []
    
    # Opportunities
    if health_score >= 8:
        opportunities.append("Strong financial health indicates good investment potential")
    if metrics.get('revenue_growth', 0) > 10:
        opportunities.append("High revenue growth suggests expanding market presence")
    if metrics.get('net_margin', 0) > 15:
        opportunities.append("High profit margins indicate efficient operations")
    
    # Risks
    if health_score <= 4:
        risks.append("Poor financial health suggests high investment risk")
    if metrics.get('debt_to_assets', 0) > 0.7:
        risks.append("High debt levels increase financial risk")
    if metrics.get('net_margin', 0) < 0:
        risks.append("Negative profit margins indicate operational challenges")
    
    # Recommendations
    if health_score >= 7:
        recommendations.append("Consider as a strong investment opportunity")
    elif health_score >= 5:
        recommendations.append("Moderate investment potential - monitor closely")
    else:
        recommendations.append("High risk investment - consider carefully")
    
    return {
        'opportunities': '\n'.join(f"- {opp}" for opp in opportunities) if opportunities else "- No significant opportunities identified",
        'risks': '\n'.join(f"- {risk}" for risk in risks) if risks else "- No significant risks identified",
        'recommendations': '\n'.join(f"- {rec}" for rec in recommendations)
    }


def _calculate_risk_scores(metrics: Dict[str, Any]) -> Dict[str, str]:
    """Calculate various risk scores."""
    scores = {}
    
    # Liquidity risk
    if 'current_ratio' in metrics:
        if metrics['current_ratio'] > 2:
            scores['liquidity_risk'] = 'Low'
        elif metrics['current_ratio'] > 1:
            scores['liquidity_risk'] = 'Medium'
        else:
            scores['liquidity_risk'] = 'High'
    else:
        scores['liquidity_risk'] = 'Unknown'
    
    # Credit risk
    if 'debt_to_assets' in metrics:
        if metrics['debt_to_assets'] < 0.3:
            scores['credit_risk'] = 'Low'
        elif metrics['debt_to_assets'] < 0.6:
            scores['credit_risk'] = 'Medium'
        else:
            scores['credit_risk'] = 'High'
    else:
        scores['credit_risk'] = 'Unknown'
    
    # Market risk (simplified)
    scores['market_risk'] = 'Medium'  # Would need market data for accurate assessment
    scores['operational_risk'] = 'Medium'  # Would need operational data
    
    # Overall risk
    high_risks = sum(1 for risk in scores.values() if risk == 'High')
    if high_risks >= 2:
        scores['overall_risk'] = 'High'
    elif high_risks == 1:
        scores['overall_risk'] = 'Medium'
    else:
        scores['overall_risk'] = 'Low'
    
    return scores


def _get_risk_description(risk_type: str, level: str) -> str:
    """Get description for risk level."""
    descriptions = {
        'liquidity': {
            'Low': 'Strong ability to meet short-term obligations',
            'Medium': 'Adequate liquidity but may face challenges in stress scenarios',
            'High': 'Potential difficulty meeting short-term obligations'
        },
        'credit': {
            'Low': 'Low debt levels relative to assets',
            'Medium': 'Moderate debt levels with manageable risk',
            'High': 'High debt levels increase financial vulnerability'
        },
        'market': {
            'Low': 'Stable market conditions with low volatility',
            'Medium': 'Normal market volatility with moderate risk',
            'High': 'High market volatility and uncertainty'
        },
        'operational': {
            'Low': 'Efficient operations with strong management',
            'Medium': 'Adequate operational efficiency',
            'High': 'Operational challenges may impact performance'
        }
    }
    
    return descriptions.get(risk_type, {}).get(level, 'Risk level not determined')


def _format_metrics(metrics: Dict[str, Any]) -> str:
    """Format metrics for display."""
    formatted = []
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            if 'ratio' in key.lower() or 'margin' in key.lower():
                formatted.append(f"- {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                formatted.append(f"- {key.replace('_', ' ').title()}: ${value:,.0f}")
        else:
            formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    return '\n'.join(formatted) if formatted else "No metrics available"


def _format_risk_indicators(metrics: Dict[str, Any], risk_scores: Dict[str, str]) -> str:
    """Format risk indicators for display."""
    indicators = []
    
    if 'debt_to_assets' in metrics:
        indicators.append(f"- Debt-to-Assets Ratio: {metrics['debt_to_assets']:.2f}")
    if 'current_ratio' in metrics:
        indicators.append(f"- Current Ratio: {metrics['current_ratio']:.2f}")
    if 'net_margin' in metrics:
        indicators.append(f"- Net Profit Margin: {metrics['net_margin']:.2f}%")
    
    return '\n'.join(indicators) if indicators else "Limited risk indicators available"


def _get_mitigation_strategies(risk_scores: Dict[str, str]) -> str:
    """Get risk mitigation strategies."""
    strategies = []
    
    if risk_scores.get('liquidity_risk') == 'High':
        strategies.append("- Improve cash management and working capital")
    if risk_scores.get('credit_risk') == 'High':
        strategies.append("- Reduce debt levels and improve debt structure")
    if risk_scores.get('operational_risk') == 'High':
        strategies.append("- Enhance operational efficiency and cost management")
    
    return '\n'.join(strategies) if strategies else "- Monitor current risk levels"


def _get_scenario_analysis(metrics: Dict[str, Any], risk_scores: Dict[str, str]) -> str:
    """Generate scenario analysis."""
    scenarios = []
    
    # Best case scenario
    if risk_scores.get('overall_risk') == 'Low':
        scenarios.append("- **Best Case**: Continued strong performance with growth opportunities")
    else:
        scenarios.append("- **Best Case**: Gradual improvement in financial metrics")
    
    # Worst case scenario
    if risk_scores.get('overall_risk') == 'High':
        scenarios.append("- **Worst Case**: Potential financial distress requiring immediate attention")
    else:
        scenarios.append("- **Worst Case**: Moderate challenges requiring strategic adjustments")
    
    return '\n'.join(scenarios)


def _get_market_context(metrics: Dict[str, Any]) -> str:
    """Get market context (placeholder for now)."""
    return "Market context analysis would require additional market data and industry benchmarks."