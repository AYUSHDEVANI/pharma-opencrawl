"""
Extraction Validator Agent
Validates and cleanses scraped pharma data
"""
from crewai import Agent, Task
from loguru import logger
from typing import Dict, Any, List


class ExtractionValidatorAgent:
    """Agent to validate extracted pharma data"""

    def __init__(self, llm):
        """
        Initialize validator agent

        Args:
            llm: Language model instance
        """
        self.llm = llm
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the extraction validator agent"""
        return Agent(
            role="Pharma Data Extraction Validator",
            goal="Validate and cleanse extracted pharmaceutical data for accuracy and completeness",
            backstory="""You are an expert data quality analyst specializing in pharmaceutical
            information. Your role is to validate drug names, approval statuses, pricing, and
            other critical data fields. You identify missing information, inconsistencies, and
            potential data quality issues. You ensure all extracted data meets quality standards
            before it's processed by other agents.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
        )

    def create_validation_task(self, drug_record: Dict[str, Any]) -> Task:
        """
        Create a validation task for a drug record

        Args:
            drug_record: Dictionary containing drug information

        Returns:
            CrewAI Task object
        """
        description = f"""
        Validate the following pharmaceutical drug record for accuracy and completeness:

        Drug Record:
        - Drug Name: {drug_record.get('drug_name', 'N/A')}
        - Approval Status: {drug_record.get('approval_status', 'N/A')}
        - Disease Category: {drug_record.get('disease_category', 'N/A')}
        - Region: {drug_record.get('region', 'N/A')}
        - Price: {drug_record.get('price', 'N/A')}
        - Approval Date: {drug_record.get('approval_date', 'N/A')}
        - Manufacturer: {drug_record.get('manufacturer', 'N/A')}
        - Indication: {drug_record.get('indication', 'N/A')}

        Your validation should check:
        1. Is the drug name valid and properly formatted?
        2. Is the approval status legitimate (Approved, Pending, Rejected, etc.)?
        3. Does the disease category make sense for this drug?
        4. Is the region/regulatory body correct?
        5. Is the price format reasonable?
        6. Are there any missing critical fields?
        7. Are there any obvious inconsistencies?

        Provide a validation report with:
        - Overall Quality Score (0-100)
        - Issues Found (list any problems)
        - Suggested Corrections (if applicable)
        - Confidence Level (High/Medium/Low)
        """

        expected_output = """
        A structured validation report containing:
        1. Quality Score: [0-100]
        2. Validation Status: [PASS/FAIL/NEEDS_REVIEW]
        3. Issues: [List of issues found, or 'None' if clean]
        4. Corrections: [Suggested fixes if needed]
        5. Confidence: [High/Medium/Low]
        6. Comments: [Any additional observations]
        """

        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
        )

    def validate_record(self, drug_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single drug record using AI

        Args:
            drug_record: Dictionary with drug information

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating record: {drug_record.get('drug_name', 'Unknown')}")

        # Use LLM for intelligent validation
        try:
            prompt = f"""
You are a pharmaceutical data quality expert. Validate the following drug information:

Drug Name: {drug_record.get('drug_name', 'N/A')}
Approval Status: {drug_record.get('approval_status', 'N/A')}
Disease Category: {drug_record.get('disease_category', 'N/A')}
Region: {drug_record.get('region', 'N/A')}
Manufacturer: {drug_record.get('manufacturer', 'N/A')}
Indication: {drug_record.get('indication', 'N/A')}
Price: {drug_record.get('price', 'N/A')}

Provide validation in this exact format:
QUALITY_SCORE: [0-100]
STATUS: [PASS/NEEDS_REVIEW/FAIL]
ISSUES: [List issues separated by semicolons, or "None"]
CONFIDENCE: [High/Medium/Low]
COMMENTS: [Brief analysis]

Validate:
1. Is this a real/known drug?
2. Does the information look accurate?
3. Are there any inconsistencies?
4. Any missing critical information?
"""

            response = self.llm.invoke(prompt)
            ai_response = response.content

            # Parse AI response
            validation_result = {
                "drug_name": drug_record.get("drug_name"),
                "quality_score": 80,
                "validation_status": "PASS",
                "issues": [],
                "confidence": "Medium",
                "ai_analysis": ai_response
            }

            # Extract structured data from AI response
            lines = ai_response.split('\n')
            for line in lines:
                if 'QUALITY_SCORE:' in line:
                    try:
                        score = int(''.join(filter(str.isdigit, line)))
                        validation_result["quality_score"] = score
                    except:
                        pass
                elif 'STATUS:' in line:
                    if 'PASS' in line:
                        validation_result["validation_status"] = "PASS"
                    elif 'FAIL' in line:
                        validation_result["validation_status"] = "FAIL"
                    else:
                        validation_result["validation_status"] = "NEEDS_REVIEW"
                elif 'ISSUES:' in line:
                    issues_text = line.split('ISSUES:')[1].strip()
                    if issues_text.lower() != 'none':
                        validation_result["issues"] = [i.strip() for i in issues_text.split(';') if i.strip()]
                elif 'CONFIDENCE:' in line:
                    if 'High' in line:
                        validation_result["confidence"] = "High"
                    elif 'Low' in line:
                        validation_result["confidence"] = "Low"
                    else:
                        validation_result["confidence"] = "Medium"

            logger.info(f"AI Validation complete: {validation_result['validation_status']} "
                       f"(Score: {validation_result['quality_score']})")

            return validation_result

        except Exception as e:
            logger.error(f"AI validation failed, using fallback: {str(e)}")
            # Fallback to basic validation
            return {
                "drug_name": drug_record.get("drug_name"),
                "quality_score": 70,
                "validation_status": "NEEDS_REVIEW",
                "issues": ["Could not perform AI validation"],
                "confidence": "Low",
            }

    def validate_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate multiple drug records

        Args:
            records: List of drug record dictionaries

        Returns:
            List of validation results
        """
        logger.info(f"Validating batch of {len(records)} records")

        results = []
        for record in records:
            try:
                validation = self.validate_record(record)
                results.append(validation)
            except Exception as e:
                logger.error(f"Error validating record: {str(e)}")
                results.append({
                    "drug_name": record.get("drug_name", "Unknown"),
                    "quality_score": 0,
                    "validation_status": "ERROR",
                    "issues": [str(e)],
                    "confidence": "Low",
                })

        # Summary
        passed = sum(1 for r in results if r["validation_status"] == "PASS")
        failed = sum(1 for r in results if r["validation_status"] == "FAIL")
        needs_review = sum(1 for r in results if r["validation_status"] == "NEEDS_REVIEW")

        logger.info(f"Validation summary: {passed} passed, {needs_review} need review, {failed} failed")

        return results


# Example usage
if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    from config.settings import OPENAI_API_KEY, AGENT_MODEL

    # Initialize LLM
    llm = ChatOpenAI(model=AGENT_MODEL, api_key=OPENAI_API_KEY)

    # Create validator agent
    validator = ExtractionValidatorAgent(llm)

    # Test with sample data
    test_record = {
        "drug_name": "Ozempic",
        "approval_status": "Approved",
        "disease_category": "Antidiabetic",
        "region": "United States",
        "price": "$950",
        "approval_date": "December 5, 2017",
        "manufacturer": "Novo Nordisk",
        "indication": "Type 2 diabetes",
    }

    result = validator.validate_record(test_record)

    print("\nValidation Result:")
    print(f"Status: {result['validation_status']}")
    print(f"Quality Score: {result['quality_score']}")
    print(f"Issues: {result['issues'] if result['issues'] else 'None'}")
    print(f"Confidence: {result['confidence']}")
