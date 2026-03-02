"""
Executive Summary Agent
Generates concise leadership summaries from analysis
"""
from crewai import Agent, Task
from loguru import logger
from typing import Dict, Any, List
from datetime import datetime


class ExecutiveSummaryAgent:
    """Agent to generate executive summaries"""

    def __init__(self, llm):
        """
        Initialize executive summary agent

        Args:
            llm: Language model instance
        """
        self.llm = llm
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the executive summary agent"""
        return Agent(
            role="Pharmaceutical Executive Communications Specialist",
            goal="Create concise, actionable executive summaries for C-level pharmaceutical executives",
            backstory="""You are a senior pharmaceutical strategist who communicates complex
            medical, regulatory, and market information to C-level executives. You synthesize
            information from multiple sources into clear, actionable 1-page summaries. You focus
            on strategic implications, competitive impact, and decision points. Your summaries
            enable executives to make quick, informed decisions.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
        )

    def create_summary_task(
        self,
        drug_record: Dict[str, Any],
        validation: Dict[str, Any],
        medical_analysis: Dict[str, Any],
        compliance: Dict[str, Any],
    ) -> Task:
        """
        Create an executive summary task

        Args:
            drug_record: Original drug information
            validation: Validation results
            medical_analysis: Medical insight results
            compliance: Compliance assessment results

        Returns:
            CrewAI Task object
        """
        description = f"""
        Create a concise executive summary for the following pharmaceutical intelligence:

        DRUG INFORMATION:
        {drug_record}

        VALIDATION RESULTS:
        {validation}

        MEDICAL ANALYSIS:
        {medical_analysis}

        COMPLIANCE ASSESSMENT:
        {compliance}

        Create a 1-page executive summary that includes:
        1. Headline: One-sentence summary of significance
        2. Key Facts: 3-5 bullet points of critical information
        3. Strategic Implications: Why this matters to our business
        4. Competitive Impact: How this affects our market position
        5. Risk Factors: Key risks to be aware of
        6. Recommended Actions: 2-3 specific next steps
        7. Decision Points: Any immediate decisions required

        Keep it concise, strategic, and action-oriented. Focus on "so what?" not just "what?"
        """

        expected_output = """
        A concise executive summary (max 1 page) containing:
        1. HEADLINE: [One-sentence summary]
        2. KEY FACTS: [3-5 critical bullet points]
        3. STRATEGIC IMPLICATIONS: [Why this matters]
        4. COMPETITIVE IMPACT: [Market positioning effects]
        5. RISK FACTORS: [Key risks]
        6. RECOMMENDED ACTIONS: [2-3 specific next steps]
        7. DECISION POINTS: [Immediate decisions needed]
        """

        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
        )

    def generate_summary(
        self,
        drug_record: Dict[str, Any],
        validation: Dict[str, Any] = None,
        medical_analysis: Dict[str, Any] = None,
        compliance: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate executive summary from agent outputs

        Args:
            drug_record: Original drug information
            validation: Validation results (optional)
            medical_analysis: Medical analysis results (optional)
            compliance: Compliance assessment (optional)

        Returns:
            Executive summary dictionary
        """
        logger.info(f"Generating executive summary for: {drug_record.get('drug_name', 'Unknown')}")

        drug_name = drug_record.get("drug_name", "Unknown Drug")
        approval_status = drug_record.get("approval_status", "Unknown")
        region = drug_record.get("region", "Unknown Region")

        # Generate headline
        headline = f"{drug_name} {approval_status} in {region}"

        # Extract key facts
        key_facts = [
            f"Drug: {drug_name} ({drug_record.get('disease_category', 'Unknown category')})",
            f"Status: {approval_status} - {region}",
            f"Manufacturer: {drug_record.get('manufacturer', 'Unknown')}",
        ]

        if drug_record.get("approval_date"):
            key_facts.append(f"Approval Date: {drug_record.get('approval_date')}")

        if drug_record.get("indication"):
            key_facts.append(f"Indication: {drug_record.get('indication')}")

        # Strategic implications
        strategic_implications = []

        if approval_status == "Approved":
            strategic_implications.append("New market entrant - assess competitive threat")
            if medical_analysis:
                market_impact = medical_analysis.get("market_impact", "Medium")
                strategic_implications.append(f"Market impact assessed as: {market_impact}")

        elif approval_status == "Pending":
            strategic_implications.append("Pending approval - monitor closely for market entry")

        elif approval_status == "Rejected":
            strategic_implications.append("Competitor setback - potential market opportunity")

        # Competitive impact
        competitive_impact = []

        if medical_analysis and medical_analysis.get("competitors"):
            num_competitors = len(medical_analysis.get("competitors", []))
            competitive_impact.append(f"Competes with {num_competitors} existing therapies")

            if medical_analysis.get("market_opportunity"):
                competitive_impact.append(
                    f"Market size: {medical_analysis.get('market_opportunity')}"
                )

        # Risk factors
        risk_factors = []

        if validation:
            quality_score = validation.get("quality_score", 0)
            if quality_score < 70:
                risk_factors.append(f"Data quality concern (score: {quality_score}/100)")

        if compliance:
            risk_level = compliance.get("risk_level", "Unknown")
            risk_factors.append(f"Regulatory risk level: {risk_level}")

            if compliance.get("compliance_flags"):
                risk_factors.extend(compliance.get("compliance_flags", []))

        if not risk_factors:
            risk_factors.append("No significant risks identified")

        # Recommended actions
        recommended_actions = []

        if approval_status == "Approved":
            recommended_actions.extend([
                "Update competitive intelligence briefing",
                "Assess pricing and market access strategy",
                "Monitor early adoption and real-world outcomes",
            ])
        elif approval_status == "Pending":
            recommended_actions.extend([
                "Track regulatory decision timeline",
                "Prepare competitive response plan",
            ])

        if compliance and compliance.get("recommendations"):
            recommended_actions.extend(compliance.get("recommendations", [])[:2])

        # Decision points
        decision_points = []

        if validation and validation.get("validation_status") == "NEEDS_REVIEW":
            decision_points.append("DECISION: Review and validate data quality before further analysis")

        if compliance and compliance.get("risk_level") == "High":
            decision_points.append("DECISION: Require executive approval for high-risk engagement")

        if not decision_points:
            decision_points.append("No immediate decisions required - continue monitoring")

        # Compile summary
        summary = {
            "drug_name": drug_name,
            "generated_at": datetime.now().isoformat(),
            "headline": headline,
            "key_facts": key_facts,
            "strategic_implications": strategic_implications,
            "competitive_impact": competitive_impact,
            "risk_factors": risk_factors,
            "recommended_actions": recommended_actions[:3],  # Limit to top 3
            "decision_points": decision_points,
        }

        logger.info(f"Executive summary generated for {drug_name}")

        return summary

    def format_summary_text(self, summary: Dict[str, Any]) -> str:
        """
        Format summary as readable text

        Args:
            summary: Summary dictionary

        Returns:
            Formatted text string
        """
        text = f"""
{'='*70}
EXECUTIVE SUMMARY: {summary['headline']}
{'='*70}
Generated: {summary['generated_at']}

KEY FACTS:
{self._format_bullets(summary['key_facts'])}

STRATEGIC IMPLICATIONS:
{self._format_bullets(summary['strategic_implications'])}

COMPETITIVE IMPACT:
{self._format_bullets(summary['competitive_impact'])}

RISK FACTORS:
{self._format_bullets(summary['risk_factors'])}

RECOMMENDED ACTIONS:
{self._format_bullets(summary['recommended_actions'], numbered=True)}

DECISION POINTS:
{self._format_bullets(summary['decision_points'])}

{'='*70}
"""
        return text

    def _format_bullets(self, items: List[str], numbered: bool = False) -> str:
        """Format list as bullet points"""
        if not items:
            return "  - None"

        formatted = []
        for i, item in enumerate(items, 1):
            if numbered:
                formatted.append(f"  {i}. {item}")
            else:
                formatted.append(f"  - {item}")

        return "\n".join(formatted)


# Example usage
if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    from config.settings import OPENAI_API_KEY, AGENT_MODEL

    # Initialize LLM
    llm = ChatOpenAI(model=AGENT_MODEL, api_key=OPENAI_API_KEY)

    # Create executive summary agent
    exec_agent = ExecutiveSummaryAgent(llm)

    # Test data
    drug_record = {
        "drug_name": "Ozempic",
        "approval_status": "Approved",
        "disease_category": "Antidiabetic",
        "region": "United States",
        "approval_date": "December 5, 2017",
        "manufacturer": "Novo Nordisk",
        "indication": "Type 2 diabetes",
    }

    validation = {
        "quality_score": 95,
        "validation_status": "PASS",
    }

    medical_analysis = {
        "market_impact": "High",
        "competitors": ["Metformin", "Insulin", "Jardiance"],
        "market_opportunity": "$60B diabetes market",
    }

    compliance = {
        "risk_level": "Medium",
        "compliance_flags": [],
        "recommendations": ["Monitor cardiovascular outcomes", "Track real-world safety"],
    }

    # Generate summary
    summary = exec_agent.generate_summary(
        drug_record, validation, medical_analysis, compliance
    )

    # Print formatted summary
    print(exec_agent.format_summary_text(summary))
