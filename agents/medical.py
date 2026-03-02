"""
Medical Insight Agent
Analyzes therapeutic categories, competitors, and market impact
"""
from crewai import Agent, Task
from loguru import logger
from typing import Dict, Any, List


class MedicalInsightAgent:
    """Agent to provide medical and market insights on drugs"""

    def __init__(self, llm):
        """
        Initialize medical insight agent

        Args:
            llm: Language model instance
        """
        self.llm = llm
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the medical insight agent"""
        return Agent(
            role="Pharmaceutical Medical Analyst",
            goal="Provide deep medical and therapeutic insights on pharmaceutical drugs, including competitor analysis and market impact",
            backstory="""You are a senior pharmaceutical analyst with expertise in drug development,
            therapeutic categories, and competitive market analysis. You understand drug mechanisms,
            indications, therapeutic areas, and can compare drugs within the same category. You
            provide insights on market positioning, competitive advantages, and potential impact
            of new drug approvals.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
        )

    def create_analysis_task(self, drug_record: Dict[str, Any]) -> Task:
        """
        Create an analysis task for a drug record

        Args:
            drug_record: Dictionary containing drug information

        Returns:
            CrewAI Task object
        """
        description = f"""
        Perform a comprehensive medical and market analysis for the following drug:

        Drug Information:
        - Drug Name: {drug_record.get('drug_name', 'N/A')}
        - Approval Status: {drug_record.get('approval_status', 'N/A')}
        - Disease Category: {drug_record.get('disease_category', 'N/A')}
        - Region: {drug_record.get('region', 'N/A')}
        - Indication: {drug_record.get('indication', 'N/A')}
        - Manufacturer: {drug_record.get('manufacturer', 'N/A')}

        Provide analysis on:
        1. Therapeutic Category: Confirm and elaborate on the therapeutic area
        2. Mechanism of Action: If known, describe how this drug works
        3. Competitive Landscape: Identify 3-5 competitor drugs in the same category
        4. Market Impact: Assess potential impact of this drug approval
        5. Clinical Significance: Why this drug matters (novelty, unmet need, etc.)
        6. Target Patient Population: Who benefits from this drug
        7. Market Opportunity: Estimated market size/opportunity if applicable

        Be specific and provide actionable insights for pharmaceutical executives.
        """

        expected_output = """
        A comprehensive medical insight report containing:
        1. Therapeutic Category: [Detailed classification]
        2. Mechanism of Action: [How it works]
        3. Key Competitors: [List of 3-5 competing drugs with brief comparison]
        4. Market Impact: [High/Medium/Low with rationale]
        5. Clinical Significance: [Why it matters]
        6. Target Population: [Patient demographics/characteristics]
        7. Market Opportunity: [Estimated size and growth]
        8. Strategic Recommendations: [2-3 actionable insights]
        """

        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
        )

    def analyze_drug(self, drug_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a drug record for medical and market insights using AI

        Args:
            drug_record: Dictionary with drug information

        Returns:
            Analysis results dictionary
        """
        logger.info(f"Analyzing drug: {drug_record.get('drug_name', 'Unknown')}")

        # Use LLM for real medical analysis
        try:
            prompt = f"""
You are a pharmaceutical market analyst. Analyze this drug:

Drug Name: {drug_record.get('drug_name', 'N/A')}
Disease Category: {drug_record.get('disease_category', 'N/A')}
Region: {drug_record.get('region', 'N/A')}
Indication: {drug_record.get('indication', 'N/A')}
Manufacturer: {drug_record.get('manufacturer', 'N/A')}
Approval Status: {drug_record.get('approval_status', 'N/A')}

Provide analysis in this format:

THERAPEUTIC_CATEGORY: [Detailed category]
MECHANISM: [How the drug works]
COMPETITORS: [List 3-5 competing drugs, separated by semicolons]
MARKET_IMPACT: [High/Medium/Low]
MARKET_SIZE: [Estimated market size]
TARGET_POPULATION: [Who uses this drug]
CLINICAL_SIGNIFICANCE: [Why it matters]
RECOMMENDATIONS: [2-3 strategic points, separated by semicolons]

Be specific about this actual drug. If it's an Indian drug, provide India-specific information.
"""

            response = self.llm.invoke(prompt)
            ai_response = response.content

            # Parse AI response
            analysis = {
                "drug_name": drug_record.get("drug_name"),
                "therapeutic_category": drug_record.get("disease_category", "Unknown"),
                "mechanism_of_action": "Analysis in progress",
                "competitors": [],
                "market_impact": "Medium",
                "clinical_significance": "",
                "target_population": "",
                "market_opportunity": "",
                "recommendations": [],
                "ai_analysis": ai_response
            }

            # Parse structured data
            lines = ai_response.split('\n')
            for line in lines:
                if 'THERAPEUTIC_CATEGORY:' in line:
                    analysis["therapeutic_category"] = line.split('THERAPEUTIC_CATEGORY:')[1].strip()
                elif 'MECHANISM:' in line:
                    analysis["mechanism_of_action"] = line.split('MECHANISM:')[1].strip()
                elif 'COMPETITORS:' in line:
                    comps = line.split('COMPETITORS:')[1].strip()
                    analysis["competitors"] = [c.strip() for c in comps.split(';') if c.strip()]
                elif 'MARKET_IMPACT:' in line:
                    impact = line.split('MARKET_IMPACT:')[1].strip()
                    if 'High' in impact:
                        analysis["market_impact"] = "High"
                    elif 'Low' in impact:
                        analysis["market_impact"] = "Low"
                    else:
                        analysis["market_impact"] = "Medium"
                elif 'MARKET_SIZE:' in line:
                    analysis["market_opportunity"] = line.split('MARKET_SIZE:')[1].strip()
                elif 'TARGET_POPULATION:' in line:
                    analysis["target_population"] = line.split('TARGET_POPULATION:')[1].strip()
                elif 'CLINICAL_SIGNIFICANCE:' in line:
                    analysis["clinical_significance"] = line.split('CLINICAL_SIGNIFICANCE:')[1].strip()
                elif 'RECOMMENDATIONS:' in line:
                    recs = line.split('RECOMMENDATIONS:')[1].strip()
                    analysis["recommendations"] = [r.strip() for r in recs.split(';') if r.strip()]

            logger.info(f"AI Analysis complete for {drug_record.get('drug_name')}")
            return analysis

        except Exception as e:
            logger.error(f"AI analysis failed, using fallback: {str(e)}")
            # Fallback to basic analysis

        # Basic analysis based on disease category
        analysis = {
            "drug_name": drug_record.get("drug_name"),
            "therapeutic_category": drug_record.get("disease_category", "Unknown"),
            "mechanism_of_action": "To be determined",
            "competitors": [],
            "market_impact": "Medium",
            "clinical_significance": "",
            "target_population": "",
            "market_opportunity": "To be assessed",
            "recommendations": [],
        }

        # Disease-specific insights
        disease_category = drug_record.get("disease_category", "").lower()

        if "diabetes" in disease_category or "antidiabetic" in disease_category:
            analysis["competitors"] = [
                "Metformin (first-line therapy)",
                "Insulin (various formulations)",
                "Ozempic/Wegovy (GLP-1 agonists)",
                "Jardiance (SGLT2 inhibitor)",
                "Januvia (DPP-4 inhibitor)",
            ]
            analysis["target_population"] = "Type 2 diabetes patients, especially those with cardiovascular risk"
            analysis["market_opportunity"] = "Global diabetes drug market: ~$60B annually"
            analysis["clinical_significance"] = "Diabetes remains a major global health challenge with growing prevalence"

        elif "oncology" in disease_category or "cancer" in disease_category:
            analysis["competitors"] = [
                "Keytruda (pembrolizumab)",
                "Opdivo (nivolumab)",
                "Tecentriq (atezolizumab)",
                "Chemotherapy regimens",
            ]
            analysis["target_population"] = "Cancer patients based on specific tumor type and biomarkers"
            analysis["market_opportunity"] = "Global oncology market: ~$200B annually"
            analysis["clinical_significance"] = "Oncology drugs address significant unmet medical need"
            analysis["market_impact"] = "High"

        elif "cardiovascular" in disease_category or "hypertension" in disease_category:
            analysis["competitors"] = [
                "Lisinopril (ACE inhibitor)",
                "Amlodipine (calcium channel blocker)",
                "Metoprolol (beta blocker)",
                "Losartan (ARB)",
            ]
            analysis["target_population"] = "Patients with hypertension, heart failure, or cardiovascular disease"
            analysis["market_opportunity"] = "Global cardiovascular drug market: ~$150B annually"

        elif "antiinfective" in disease_category or "antibiotic" in disease_category:
            analysis["competitors"] = [
                "Amoxicillin",
                "Azithromycin",
                "Ciprofloxacin",
                "Vancomycin",
            ]
            analysis["target_population"] = "Patients with bacterial infections"
            analysis["clinical_significance"] = "Important for combating antibiotic resistance"

        # General recommendations
        if drug_record.get("approval_status") == "Approved":
            analysis["recommendations"] = [
                "Monitor competitive response from existing players",
                "Assess pricing strategy relative to competitors",
                "Track real-world effectiveness and safety data",
            ]
        elif drug_record.get("approval_status") == "Pending":
            analysis["recommendations"] = [
                "Prepare market access strategy",
                "Identify key opinion leaders for launch",
                "Plan post-approval clinical studies",
            ]

        logger.info(f"Analysis complete for {drug_record.get('drug_name')}")

        return analysis

    def analyze_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple drug records

        Args:
            records: List of drug record dictionaries

        Returns:
            List of analysis results
        """
        logger.info(f"Analyzing batch of {len(records)} drugs")

        results = []
        for record in records:
            try:
                analysis = self.analyze_drug(record)
                results.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing record: {str(e)}")
                results.append({
                    "drug_name": record.get("drug_name", "Unknown"),
                    "error": str(e),
                })

        logger.info(f"Analysis complete for {len(results)} drugs")

        return results


# Example usage
if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    from config.settings import OPENAI_API_KEY, AGENT_MODEL

    # Initialize LLM
    llm = ChatOpenAI(model=AGENT_MODEL, api_key=OPENAI_API_KEY)

    # Create medical insight agent
    medical_agent = MedicalInsightAgent(llm)

    # Test with sample data
    test_record = {
        "drug_name": "Ozempic",
        "approval_status": "Approved",
        "disease_category": "Antidiabetic",
        "region": "United States",
        "indication": "Type 2 diabetes",
        "manufacturer": "Novo Nordisk",
    }

    result = medical_agent.analyze_drug(test_record)

    print("\nMedical Analysis Result:")
    print(f"Drug: {result['drug_name']}")
    print(f"Therapeutic Category: {result['therapeutic_category']}")
    print(f"\nKey Competitors:")
    for comp in result['competitors'][:3]:
        print(f"  - {comp}")
    print(f"\nMarket Impact: {result['market_impact']}")
    print(f"Market Opportunity: {result['market_opportunity']}")
    print(f"\nTarget Population: {result['target_population']}")
