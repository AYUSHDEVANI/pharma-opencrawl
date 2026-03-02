"""
Pharma Intelligence System - Main Entry Point
Complete pipeline: Crawl → Extract → Analyze with AI Agents → Store
"""
import asyncio
import sys
from pathlib import Path
from loguru import logger

from crawler.main import PharmaCrawler
from agents.main import AgentOrchestrator
from config.settings import LOG_LEVEL, LOG_FILE, TARGET_URLS

# Configure logging
logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)
logger.add(LOG_FILE, rotation="1 day", retention="7 days", level=LOG_LEVEL)


async def run_full_pipeline(urls: list = None):
    """
    Run the complete pharma intelligence pipeline

    Args:
        urls: List of URLs to crawl (defaults to TARGET_URLS from config)
    """
    logger.info("\n" + "="*80)
    logger.info("PHARMA INTELLIGENCE SYSTEM - FULL PIPELINE")
    logger.info("="*80)

    urls = urls or TARGET_URLS

    # STEP 1: Crawl and Extract
    logger.info("\n" + "-"*80)
    logger.info("STEP 1: WEB CRAWLING & DATA EXTRACTION")
    logger.info("-"*80)

    crawler = PharmaCrawler()
    extracted_records = await crawler.run(urls)

    if not extracted_records:
        logger.error("No records extracted from crawling. Exiting.")
        return

    logger.info(f"\n✅ Crawling complete: {len(extracted_records)} records extracted")

    # STEP 2: AI Agent Processing
    logger.info("\n" + "-"*80)
    logger.info("STEP 2: MULTI-AGENT AI PROCESSING")
    logger.info("-"*80)

    orchestrator = AgentOrchestrator()

    agent_results = orchestrator.process_batch(extracted_records)

    logger.info(f"\n✅ Agent processing complete: {len(agent_results)} records analyzed")

    # STEP 3: Generate Reports
    logger.info("\n" + "-"*80)
    logger.info("STEP 3: EXECUTIVE REPORTS")
    logger.info("-"*80)

    # Print top 3 executive summaries
    for i, result in enumerate(agent_results[:3], 1):
        if result.get("executive_summary"):
            logger.info(f"\n--- Executive Summary #{i} ---")
            summary_text = orchestrator.executive.format_summary_text(
                result["executive_summary"]
            )
            print(summary_text)

    # Final Summary
    logger.info("\n" + "="*80)
    logger.info("PIPELINE COMPLETE")
    logger.info("="*80)
    logger.info(f"URLs Crawled: {len(urls)}")
    logger.info(f"Records Extracted: {len(extracted_records)}")
    logger.info(f"Records Analyzed: {len(agent_results)}")
    logger.info(f"Reports Generated: {sum(1 for r in agent_results if r.get('executive_summary'))}")
    logger.info("="*80 + "\n")


async def run_crawler_only():
    """Run crawler only (for testing)"""
    logger.info("Running crawler only...")
    crawler = PharmaCrawler()
    records = await crawler.run()
    logger.info(f"Extracted {len(records)} records")
    return records


async def run_agents_only(sample_data: bool = True):
    """Run agents only with sample or stored data"""
    logger.info("Running agents only...")

    if sample_data:
        # Use sample data for testing
        test_records = [
            {
                "drug_name": "Ozempic",
                "approval_status": "Approved",
                "disease_category": "Antidiabetic",
                "region": "United States",
                "price": "$950",
                "approval_date": "December 5, 2017",
                "manufacturer": "Novo Nordisk",
                "indication": "Type 2 diabetes",
            },
        ]
    else:
        # Load from database
        from storage.database import PharmaDatabase
        db = PharmaDatabase()
        records = db.get_drug_records(limit=10)
        test_records = [r.to_dict() for r in records]

    orchestrator = AgentOrchestrator()
    results = orchestrator.process_batch(test_records)

    return results


async def main():
    """Main entry point with menu"""
    import argparse

    parser = argparse.ArgumentParser(description="Pharma Intelligence System")
    parser.add_argument(
        "--mode",
        choices=["full", "crawler", "agents", "test"],
        default="test",
        help="Run mode: full pipeline, crawler only, agents only, or test mode"
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        help="Custom URLs to crawl (space-separated)"
    )

    args = parser.parse_args()

    if args.mode == "full":
        await run_full_pipeline(urls=args.urls)

    elif args.mode == "crawler":
        await run_crawler_only()

    elif args.mode == "agents":
        await run_agents_only(sample_data=True)

    elif args.mode == "test":
        logger.info("Running in TEST mode with sample data...")
        logger.info("This will demonstrate the full pipeline without actual web crawling\n")

        # Use sample data instead of real crawling
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

        logger.info(f"Processing {len(sample_records)} sample drug records...\n")

        orchestrator = AgentOrchestrator()
        results = orchestrator.process_batch(sample_records)

        # Print detailed results
        if results and results[0].get("executive_summary"):
            logger.info("\n" + "="*80)
            logger.info("SAMPLE EXECUTIVE SUMMARY")
            logger.info("="*80)
            summary_text = orchestrator.executive.format_summary_text(
                results[0]["executive_summary"]
            )
            print(summary_text)


if __name__ == "__main__":
    asyncio.run(main())
