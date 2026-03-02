"""
Risk & Compliance Agent
Checks regulatory impact and compliance implications
"""
from crewai import Agent, Task
from loguru import logger
from typing import Dict, Any, List


class ComplianceAgent:
    """Agent to assess regulatory risk and compliance"""

    def __init__(self, llm):
        """
        Initialize compliance agent

        Args:
            llm: Language model instance
        """
        self.llm = llm
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the risk & compliance agent"""
        return Agent(
            role="Pharmaceutical Regulatory & Compliance Officer",
            goal="Assess regulatory requirements, compliance implications, and risks associated with pharmaceutical drugs",
            backstory="""You are a regulatory affairs expert with deep knowledge of FDA, EMA, and
            global pharmaceutical regulations. You assess compliance requirements, identify potential
            regulatory risks, flag safety concerns, and provide guidance on regulatory pathways.
            You understand approval processes, post-market surveillance requirements, and regulatory
            strategy.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
        )

    def create_compliance_task(self, drug_record: Dict[str, Any]) -> Task:
        """
        Create a compliance assessment task

        Args:
            drug_record: Dictionary containing drug information

        Returns:
            CrewAI Task object
        """
        description = f"""
        Perform a regulatory and compliance assessment for the following drug:

        Drug Information:
        - Drug Name: {drug_record.get('drug_name', 'N/A')}
        - Approval Status: {drug_record.get('approval_status', 'N/A')}
        - Disease Category: {drug_record.get('disease_category', 'N/A')}
        - Region: {drug_record.get('region', 'N/A')}
        - Approval Date: {drug_record.get('approval_date', 'N/A')}
        - Manufacturer: {drug_record.get('manufacturer', 'N/A')}

        Assess the following:
        1. Regulatory Authority: Which regulatory body approved/reviewed this drug?
        2. Approval Pathway: Standard, fast track, breakthrough therapy, etc.?
        3. Compliance Requirements: What ongoing requirements exist?
        4. Risk Assessment: Identify potential safety, efficacy, or manufacturing risks
        5. Post-Market Surveillance: What monitoring is required?
        6. Global Regulatory Impact: How might this affect other regions?
        7. Compliance Flags: Any red flags or concerns?

        Provide actionable regulatory guidance.
        """

        expected_output = """
        A comprehensive compliance assessment containing:
        1. Regulatory Body: [FDA/EMA/CDSCO/Other]
        2. Approval Pathway: [Standard/Expedited/Conditional/etc.]
        3. Compliance Requirements: [List of ongoing requirements]
        4. Risk Level: [Low/Medium/High with rationale]
        5. Safety Concerns: [Any identified concerns or 'None noted']
        6. Post-Market Obligations: [Required studies, surveillance, etc.]
        7. Compliance Flags: [Any red flags or 'Clear']
        8. Recommendations: [2-3 actionable compliance recommendations]
        """

        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
        )

    def assess_compliance(self, drug_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess regulatory compliance for a drug record using AI

        Args:
            drug_record: Dictionary with drug information

        Returns:
            Compliance assessment dictionary
        """
        logger.info(f"Assessing compliance for: {drug_record.get('drug_name', 'Unknown')}")

        # Use LLM for real compliance analysis
        try:
            prompt = f"""
You are a pharmaceutical regulatory compliance expert. Assess this drug:

Drug Name: {drug_record.get('drug_name', 'N/A')}
Disease Category: {drug_record.get('disease_category', 'N/A')}
Region: {drug_record.get('region', 'N/A')}
Approval Status: {drug_record.get('approval_status', 'N/A')}
Manufacturer: {drug_record.get('manufacturer', 'N/A')}

Provide compliance assessment in this format:

REGULATORY_BODY: [Which authority - FDA/EMA/CDSCO/etc]
RISK_LEVEL: [High/Medium/Low]
COMPLIANCE_REQUIREMENTS: [List key requirements, separated by semicolons]
SAFETY_CONCERNS: [List concerns, separated by semicolons, or "None noted"]
POST_MARKET: [Required post-market activities]
RECOMMENDATIONS: [2-3 compliance recommendations, separated by semicolons]

Be specific about the actual regulatory requirements for this drug in this region.
"""

            response = self.llm.invoke(prompt)
            ai_response = response.content

            assessment = {
                "drug_name": drug_record.get("drug_name"),
                "regulatory_body": "Unknown",
                "approval_pathway": "Standard",
                "compliance_requirements": [],
                "risk_level": "Medium",
                "safety_concerns": [],
                "post_market_obligations": [],
                "compliance_flags": [],
                "recommendations": [],
                "ai_analysis": ai_response
            }

            # Parse AI response
            lines = ai_response.split('\n')
            for line in lines:
                if 'REGULATORY_BODY:' in line:
                    assessment["regulatory_body"] = line.split('REGULATORY_BODY:')[1].strip()
                elif 'RISK_LEVEL:' in line:
                    risk = line.split('RISK_LEVEL:')[1].strip()
                    if 'High' in risk:
                        assessment["risk_level"] = "High"
                    elif 'Low' in risk:
                        assessment["risk_level"] = "Low"
                    else:
                        assessment["risk_level"] = "Medium"
                elif 'COMPLIANCE_REQUIREMENTS:' in line:
                    reqs = line.split('COMPLIANCE_REQUIREMENTS:')[1].strip()
                    assessment["compliance_requirements"] = [r.strip() for r in reqs.split(';') if r.strip()]
                elif 'SAFETY_CONCERNS:' in line:
                    concerns = line.split('SAFETY_CONCERNS:')[1].strip()
                    if concerns.lower() != 'none noted':
                        assessment["safety_concerns"] = [c.strip() for c in concerns.split(';') if c.strip()]
                elif 'POST_MARKET:' in line:
                    pm = line.split('POST_MARKET:')[1].strip()
                    assessment["post_market_obligations"] = [pm] if pm else []
                elif 'RECOMMENDATIONS:' in line:
                    recs = line.split('RECOMMENDATIONS:')[1].strip()
                    assessment["recommendations"] = [r.strip() for r in recs.split(';') if r.strip()]

            logger.info(f"AI Compliance assessment complete: Risk Level = {assessment['risk_level']}")
            return assessment

        except Exception as e:
            logger.error(f"AI compliance assessment failed, using fallback: {str(e)}")
            # Fallback to basic assessment

        assessment = {
            "drug_name": drug_record.get("drug_name"),
            "regulatory_body": "Unknown",
            "approval_pathway": "Standard",
            "compliance_requirements": [],
            "risk_level": "Medium",
            "safety_concerns": [],
            "post_market_obligations": [],
            "compliance_flags": [],
            "recommendations": [],
        }

        # Determine regulatory body based on region
        region = drug_record.get("region", "").lower()

        if "united states" in region or "us" in region or "fda" in region:
            assessment["regulatory_body"] = "FDA (United States)"
            assessment["compliance_requirements"] = [
                "Annual drug product reporting",
                "Adverse event reporting (15-day and periodic)",
                "Manufacturing quality standards (cGMP)",
                "Labeling updates as required",
            ]
        elif "european" in region or "eu" in region or "ema" in region:
            assessment["regulatory_body"] = "EMA (European Union)"
            assessment["compliance_requirements"] = [
                "Periodic Safety Update Reports (PSURs)",
                "Risk Management Plan updates",
                "cGMP compliance",
                "Variations to Marketing Authorization",
            ]
        elif "india" in region or "cdsco" in region:
            assessment["regulatory_body"] = "CDSCO (India)"
            assessment["compliance_requirements"] = [
                "Periodic safety updates",
                "Good Manufacturing Practices compliance",
                "Post-marketing surveillance",
                "Labeling compliance",
            ]

        # Assess risk level based on disease category
        disease_category = drug_record.get("disease_category", "").lower()

        if "oncology" in disease_category or "cancer" in disease_category:
            assessment["risk_level"] = "High"
            assessment["safety_concerns"] = [
                "Serious adverse events common in oncology drugs",
                "Drug interactions with other cancer therapies",
                "Long-term safety monitoring required",
            ]
            assessment["post_market_obligations"] = [
                "Phase 4 safety studies",
                "Long-term efficacy monitoring",
                "Real-world evidence collection",
            ]

        elif "cardiovascular" in disease_category:
            assessment["risk_level"] = "High"
            assessment["safety_concerns"] = [
                "Cardiovascular events monitoring",
                "Drug-drug interactions",
                "Dose-dependent effects",
            ]

        elif "diabetes" in disease_category or "antidiabetic" in disease_category:
            assessment["risk_level"] = "Medium"
            assessment["safety_concerns"] = [
                "Hypoglycemia risk",
                "Cardiovascular outcomes monitoring",
                "Kidney function monitoring",
            ]
            assessment["post_market_obligations"] = [
                "Cardiovascular outcomes trial (CVOT)",
                "Real-world safety monitoring",
            ]

        else:
            assessment["risk_level"] = "Medium"
            assessment["safety_concerns"] = ["Standard safety monitoring required"]

        # Check for compliance flags
        approval_status = drug_record.get("approval_status", "")

        if approval_status == "Pending":
            assessment["compliance_flags"].append(
                "Approval pending - ensure all pre-market requirements met"
            )

        if approval_status == "Rejected":
            assessment["compliance_flags"].append(
                "Previous rejection - requires careful review of rejection rationale"
            )

        if approval_status == "Withdrawn":
            assessment["compliance_flags"].append(
                "WARNING: Previously withdrawn - investigate reasons for withdrawal"
            )

        # Generate recommendations
        assessment["recommendations"] = [
            f"Ensure {assessment['regulatory_body']} compliance requirements are met",
            f"Given {assessment['risk_level']} risk level, implement robust pharmacovigilance",
            "Establish post-market surveillance program",
        ]

        if assessment["post_market_obligations"]:
            assessment["recommendations"].append(
                "Complete all post-market obligations on schedule"
            )

        logger.info(f"Compliance assessment complete: Risk Level = {assessment['risk_level']}")

        return assessment

    def assess_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assess compliance for multiple drug records

        Args:
            records: List of drug record dictionaries

        Returns:
            List of compliance assessments
        """
        logger.info(f"Assessing compliance for batch of {len(records)} drugs")

        results = []
        for record in records:
            try:
                assessment = self.assess_compliance(record)
                results.append(assessment)
            except Exception as e:
                logger.error(f"Error assessing compliance: {str(e)}")
                results.append({
                    "drug_name": record.get("drug_name", "Unknown"),
                    "error": str(e),
                })

        # Summary
        high_risk = sum(1 for r in results if r.get("risk_level") == "High")
        flagged = sum(1 for r in results if r.get("compliance_flags"))

        logger.info(f"Compliance summary: {high_risk} high-risk drugs, {flagged} with compliance flags")

        return results


# Example usage
if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    from config.settings import OPENAI_API_KEY, AGENT_MODEL

    # Initialize LLM
    llm = ChatOpenAI(model=AGENT_MODEL, api_key=OPENAI_API_KEY)

    # Create compliance agent
    compliance_agent = ComplianceAgent(llm)

    # Test with sample data
    test_record = {
        "drug_name": "Keytruda",
        "approval_status": "Approved",
        "disease_category": "Oncology",
        "region": "United States",
        "approval_date": "September 4, 2014",
        "manufacturer": "Merck",
    }

    result = compliance_agent.assess_compliance(test_record)

    print("\nCompliance Assessment Result:")
    print(f"Drug: {result['drug_name']}")
    print(f"Regulatory Body: {result['regulatory_body']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"\nSafety Concerns:")
    for concern in result['safety_concerns']:
        print(f"  - {concern}")
    print(f"\nCompliance Requirements:")
    for req in result['compliance_requirements'][:3]:
        print(f"  - {req}")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
