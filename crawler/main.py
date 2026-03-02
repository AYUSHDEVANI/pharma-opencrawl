"""
Main crawler orchestrator for Pharma Intelligence System
"""
import asyncio
from typing import List
from loguru import logger
import sys

from crawler.scraper import PharmaScraper
from crawler.extractors import PharmaDataExtractor
from config.settings import TARGET_URLS, LOG_LEVEL, LOG_FILE

# Configure logging
logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)
logger.add(LOG_FILE, rotation="1 day", retention="7 days", level=LOG_LEVEL)


class PharmaCrawler:
    """Main crawler orchestrator"""

    def __init__(self):
        self.scraper = PharmaScraper()
        self.extractor = PharmaDataExtractor()

    async def run(self, urls: List[str] = None):
        """
        Run the crawler pipeline

        Args:
            urls: List of URLs to crawl (defaults to TARGET_URLS from config)
        """
        urls = urls or TARGET_URLS

        logger.info(f"Starting pharma crawler for {len(urls)} URLs")

        # Step 1: Crawl websites
        logger.info("Step 1: Crawling websites...")
        crawled_data = await self.scraper.crawl_multiple(urls)

        successful_crawls = [d for d in crawled_data if d.get("success")]
        logger.info(f"Successfully crawled {len(successful_crawls)}/{len(urls)} URLs")

        # Step 2: Extract structured data
        logger.info("Step 2: Extracting structured data...")
        all_records = []

        for data in successful_crawls:
            records = self.extractor.process_crawled_data(data)
            all_records.extend(records)

        logger.info(f"Extracted {len(all_records)} drug/approval records")

        # Step 3: Summary
        logger.info("\n" + "="*60)
        logger.info("CRAWL SUMMARY")
        logger.info("="*60)
        logger.info(f"URLs processed: {len(urls)}")
        logger.info(f"Successful crawls: {len(successful_crawls)}")
        logger.info(f"Records extracted: {len(all_records)}")

        if all_records:
            logger.info("\nSample records:")
            for i, record in enumerate(all_records[:3], 1):
                logger.info(f"{i}. {record.get('drug_name', 'Unknown')} - "
                           f"{record.get('approval_status', 'N/A')} - "
                           f"{record.get('disease_category', 'N/A')}")

        logger.info("="*60)

        return all_records


async def main():
    """Main entry point"""
    crawler = PharmaCrawler()

    # Use default URLs from config
    records = await crawler.run()

    logger.info(f"Crawler finished. Total records: {len(records)}")


if __name__ == "__main__":
    asyncio.run(main())
