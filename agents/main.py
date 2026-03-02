"""
Main agent orchestrator
Coordinates all 4 agents to process pharma intelligence
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.validator import ExtractionValidatorAgent
from agents.medical import MedicalInsightAgent
from agents.compliance import ComplianceAgent
from agents.executive import ExecutiveSummaryAgent
from config.settings import AGENT_MODEL, LOG_LEVEL, LOG_FILE
import os

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    logger.error("langchain-google-genai not installed. Install with: pip install langchain-google-genai")
    sys.exit(1)

# Configure logging
logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)
logger.add(LOG_FILE, rotation="1 day", retention="7 days", level=LOG_LEVEL)


class AgentOrchestrator:
    """Orchestrates all 4 pharma intelligence agents"""

    def __init__(self):
        """Initialize orchestrator"""
        logger.info("Initializing Agent Orchestrator...")

        # Initialize LLM (Gemini)
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.warning("GEMINI_API_KEY not set, agents will not work properly")

        # Extract model name from format gemini/model-name
        model_name = AGENT_MODEL.split("/")[-1] if "/" in AGENT_MODEL else AGENT_MODEL
        self.llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=gemini_api_key)

        # Initialize all agents
        self.validator = ExtractionValidatorAgent(self.llm)
        self.medical = MedicalInsightAgent(self.llm)
        self.compliance = ComplianceAgent(self.llm)
        self.executive = ExecutiveSummaryAgent(self.llm)

        logger.info("Agent Orchestrator initialized successfully")

    def process_record(self, drug_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single drug record through all agents

        Args:
            drug_record: Dictionary with drug information

        Returns:
            Complete analysis including all agent outputs
        """
        drug_name = drug_record.get("drug_name", "Unknown")
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {drug_name}")
        logger.info(f"{'='*60}")

        results = {
            "drug_record": drug_record,
            "validation": None,
            "medical_analysis": None,
            "compliance": None,
            "executive_summary": None,
        }

        # Step 1: Validation
        logger.info("\n[Step 1/4] Running Extraction Validator Agent...")
        try:
            validation = self.validator.validate_record(drug_record)
            results["validation"] = validation
            logger.info(f"Validation: {validation['validation_status']} "
                       f"(Score: {validation['quality_score']}/100)")

            # Skip further processing if validation fails badly
            if validation["quality_score"] < 30:
                logger.warning("Low quality score - skipping further processing")
                return results

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return results

        # Step 2: Medical Analysis
        logger.info("\n[Step 2/4] Running Medical Insight Agent...")
        try:
            medical_analysis = self.medical.analyze_drug(drug_record)
            results["medical_analysis"] = medical_analysis
            logger.info(f"Medical Analysis: Category={medical_analysis['therapeutic_category']}, "
                       f"Impact={medical_analysis['market_impact']}")

        except Exception as e:
            logger.error(f"Medical analysis failed: {str(e)}")

        # Step 3: Compliance Assessment
        logger.info("\n[Step 3/4] Running Risk & Compliance Agent...")
        try:
            compliance = self.compliance.assess_compliance(drug_record)
            results["compliance"] = compliance
            logger.info(f"Compliance: Risk={compliance['risk_level']}, "
                       f"Flags={len(compliance['compliance_flags'])}")

        except Exception as e:
            logger.error(f"Compliance assessment failed: {str(e)}")

        # Step 4: Executive Summary
        logger.info("\n[Step 4/4] Running Executive Summary Agent...")
        try:
            executive_summary = self.executive.generate_summary(
                drug_record,
                validation=results["validation"],
                medical_analysis=results["medical_analysis"],
                compliance=results["compliance"],
            )
            results["executive_summary"] = executive_summary
            logger.info("Executive summary generated")

        except Exception as e:
            logger.error(f"Executive summary generation failed: {str(e)}")

        # Store results
        self._store_results(results)

        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Processing complete for {drug_name}")
        logger.info(f"{'='*60}\n")

        return results

    def process_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple drug records

        Args:
            records: List of drug record dictionaries

        Returns:
            List of complete analysis results
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"MULTI-AGENT BATCH PROCESSING")
        logger.info(f"{'='*70}")
        logger.info(f"Total records to process: {len(records)}\n")

        all_results = []

        for i, record in enumerate(records, 1):
            logger.info(f"\n--- Processing Record {i}/{len(records)} ---")
            try:
                result = self.process_record(record)
                all_results.append(result)
            except Exception as e:
                logger.error(f"Failed to process record: {str(e)}")
                all_results.append({
                    "drug_record": record,
                    "error": str(e),
                })

        # Summary statistics
        self._print_batch_summary(all_results)

        return all_results

    def _store_results(self, results: Dict[str, Any]):
        """Store processing results in database and vector store"""

        # Store in PostgreSQL
        if self.use_database:
            try:
                record_id = self.db.insert_drug_record(results["drug_record"])
                logger.debug(f"Stored in database: ID={record_id}")
            except Exception as e:
                logger.error(f"Failed to store in database: {str(e)}")

        # Store in vector database
        if self.use_vector_store and results.get("executive_summary"):
            try:
                summary_text = self.executive.format_summary_text(
                    results["executive_summary"]
                )
                self.vector_store.add_documents(
                    [summary_text],
                    [{"drug_name": results["drug_record"].get("drug_name")}]
                )
                self.vector_store.save()
                logger.debug("Stored in vector database")
            except Exception as e:
                logger.error(f"Failed to store in vector database: {str(e)}")

    def _print_batch_summary(self, results: List[Dict[str, Any]]):
        """Print summary statistics for batch processing"""
        logger.info(f"\n{'='*70}")
        logger.info("BATCH PROCESSING SUMMARY")
        logger.info(f"{'='*70}")

        total = len(results)
        successful = sum(1 for r in results if "error" not in r)
        failed = total - successful

        logger.info(f"Total records processed: {total}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")

        if successful > 0:
            # Validation stats
            passed_validation = sum(
                1 for r in results
                if r.get("validation", {}).get("validation_status") == "PASS"
            )
            logger.info(f"\nValidation: {passed_validation}/{successful} passed")

            # Risk stats
            high_risk = sum(
                1 for r in results
                if r.get("compliance", {}).get("risk_level") == "High"
            )
            logger.info(f"High-risk drugs: {high_risk}")

            # Sample executive summaries
            logger.info(f"\nSample Executive Summaries:")
            for i, result in enumerate(results[:3], 1):
                if result.get("executive_summary"):
                    headline = result["executive_summary"].get("headline", "N/A")
                    logger.info(f"{i}. {headline}")

        logger.info(f"{'='*70}\n")


async def main():
    """Main entry point"""
    logger.info("Starting Pharma Intelligence - Multi-Agent System\n")

    # Initialize orchestrator
    orchestrator = AgentOrchestrator(use_database=False, use_vector_store=False)

    # Test with sample data
    sample_records = [
        {
            "drug_name": "Ozempic",
            "approval_status": "Approved",
            "disease_category": "Antidiabetic",
            "region": "United States",
            "price": "$950",
            "approval_date": "December 5, 2017",
            "manufacturer": "Novo Nordisk",
            "indication": "Type 2 diabetes",
            "source_url": "https://www.fda.gov",
        },
        {
            "drug_name": "Keytruda",
            "approval_status": "Approved",
            "disease_category": "Oncology",
            "region": "United States",
            "approval_date": "September 4, 2014",
            "manufacturer": "Merck",
            "indication": "Various cancers",
            "source_url": "https://www.fda.gov",
        },
    ]

    # Process records
    results = orchestrator.process_batch(sample_records)

    # Print detailed results for first record
    if results and results[0].get("executive_summary"):
        logger.info("\nDETAILED EXECUTIVE SUMMARY - FIRST RECORD:")
        summary_text = orchestrator.executive.format_summary_text(
            results[0]["executive_summary"]
        )
        print(summary_text)


if __name__ == "__main__":
    asyncio.run(main())
