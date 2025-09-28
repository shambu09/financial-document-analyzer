from crewai import Task

from app.domain.agents import financial_analyst, verifier, investment_advisor, risk_assessor
from app.services.tools import (
    search_tool,  # Free DuckDuckGo search tool
    FinancialDocumentTool,
    read_financial_document,
    analyze_investment_opportunities,
    assess_financial_risks,
    extract_financial_metrics
)

## Task: Analyze a financial document
analyze_financial_document = Task(
    description=(
        "Analyze the provided financial document in detail using the file path: {file_path}. "
        "Address the user's query: {query}. "
        "First, extract and calculate key financial metrics from the document. "
        "Then provide a comprehensive analysis including quantitative metrics, trends, and qualitative insights. "
        "Use external sources to add market context and industry benchmarks when relevant. "
        "Focus on actionable insights and clear recommendations."
    ),
    expected_output=(
        "A comprehensive financial analysis report including:\n"
        "- Executive summary of key findings\n"
        "- Detailed financial metrics and ratios analysis\n"
        "- Financial health score and assessment\n"
        "- Strengths, weaknesses, and performance indicators\n"
        "- Key risks and opportunities identified\n"
        "- Market context and industry comparisons\n"
        "- Clear, actionable recommendations\n"
        "- Areas of uncertainty and limitations"
    ),
    agent=financial_analyst,
    tools=[
        read_financial_document, 
        extract_financial_metrics,
        search_tool  # Free DuckDuckGo search
    ],
    async_execution=False,
)

## Task: Provide investment analysis
investment_analysis = Task(
    description=(
        "Conduct a comprehensive investment analysis using the financial document at: {file_path}. "
        "Address the user's query: {query}. "
        "First, extract financial metrics and calculate investment-relevant ratios. "
        "Then analyze investment opportunities, risks, and provide specific recommendations. "
        "Use market research to validate and contextualize your analysis. "
        "Focus on practical, actionable investment strategies with clear reasoning."
    ),
    expected_output=(
        "A detailed investment analysis report including:\n"
        "- Investment opportunity assessment with health score\n"
        "- 5-7 specific investment recommendations with detailed reasoning\n"
        "- Financial metrics analysis supporting recommendations\n"
        "- Risk-return analysis and scenario planning\n"
        "- Market context and competitive positioning\n"
        "- Short-term and long-term investment outlook\n"
        "- Compliance considerations and regulatory notes\n"
        "- Clear action items and next steps"
    ),
    agent=investment_advisor,
    tools=[
        read_financial_document,
        analyze_investment_opportunities,
        extract_financial_metrics,
        search_tool  # Free DuckDuckGo search
    ],
    async_execution=False,
)

## Task: Assess risks
risk_assessment = Task(
    description=(
        "Conduct a comprehensive risk assessment using the financial document at: {file_path}. "
        "Address the user's query: {query}. "
        "First, extract financial metrics and calculate risk-relevant ratios. "
        "Then perform a detailed risk analysis across multiple dimensions including liquidity, credit, market, and operational risks. "
        "Provide both quantitative risk scores and qualitative risk descriptions. "
        "Include scenario analysis and mitigation strategies."
    ),
    expected_output=(
        "A comprehensive risk assessment report including:\n"
        "- Overall risk level assessment with scoring\n"
        "- Detailed breakdown of risk categories (liquidity, credit, market, operational)\n"
        "- Risk indicators and key metrics analysis\n"
        "- Scenario analysis (best case, base case, worst case)\n"
        "- Risk mitigation strategies and recommendations\n"
        "- Early warning indicators to monitor\n"
        "- Risk tolerance recommendations\n"
        "- Regulatory and compliance risk considerations"
    ),
    agent=risk_assessor,
    tools=[
        read_financial_document,
        assess_financial_risks,
        extract_financial_metrics
    ],
    async_execution=False,
)

## Task: Verify financial document
verification = Task(
    description=(
        "Verify whether the provided document at: {file_path} is a valid financial record. "
        "Carefully examine the document structure, financial terminology, data consistency, and formatting. "
        "Look for standard financial statement elements, accounting terminology, and numerical data patterns. "
        "Do not assume—provide evidence-based verification. "
        "Flag any inconsistencies, missing elements, or non-financial content."
    ),
    expected_output=(
        "A detailed verification report including:\n"
        "- Clear yes/no determination of financial document validity\n"
        "- Supporting evidence and reasoning for the decision\n"
        "- Document structure analysis and completeness check\n"
        "- Financial terminology and data consistency assessment\n"
        "- Identified inconsistencies or missing information\n"
        "- Compliance and regulatory considerations\n"
        "- Recommendations for document improvement (if applicable)\n"
        "- Confidence level in the verification assessment"
    ),
    agent=verifier,
    tools=[
        read_financial_document,
        extract_financial_metrics
    ],
    async_execution=False,
)
