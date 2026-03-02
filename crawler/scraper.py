"""
Web scraper using Crawl4AI for pharma/health websites
"""
import asyncio
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler
from loguru import logger
import json
from datetime import datetime
from pathlib import Path

from config.settings import RAW_DATA_DIR, USER_AGENT


class PharmaScraper:
    """Scraper for pharma and health websites"""

    def __init__(self):
        self.user_agent = USER_AGENT
        self.raw_data_dir = RAW_DATA_DIR

    async def crawl_url(self, url: str) -> Dict[str, Any]:
        """
        Crawl a single URL and extract content

        Args:
            url: URL to crawl

        Returns:
            Dict with crawled data
        """
        try:
            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    bypass_cache=True,
                )

                if result.success:
                    logger.info(f"Successfully crawled: {url}")

                    data = {
                        "url": url,
                        "title": result.metadata.get("title", ""),
                        "html": result.html,
                        "markdown": result.markdown,
                        "cleaned_html": result.cleaned_html,
                        "media": result.media,
                        "links": result.links,
                        "metadata": result.metadata,
                        "crawled_at": datetime.now().isoformat(),
                        "success": True,
                    }

                    # Save raw HTML
                    self._save_raw_data(url, data)

                    return data
                else:
                    logger.error(f"Failed to crawl {url}: {result.error_message}")
                    return {
                        "url": url,
                        "success": False,
                        "error": result.error_message,
                        "crawled_at": datetime.now().isoformat(),
                    }

        except Exception as e:
            logger.error(f"Exception crawling {url}: {str(e)}")
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "crawled_at": datetime.now().isoformat(),
            }

    async def crawl_multiple(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs concurrently

        Args:
            urls: List of URLs to crawl

        Returns:
            List of crawled data dicts
        """
        logger.info(f"Starting concurrent crawl of {len(urls)} URLs")

        tasks = [self.crawl_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Exception for URL {urls[i]}: {str(result)}")
                valid_results.append({
                    "url": urls[i],
                    "success": False,
                    "error": str(result),
                    "crawled_at": datetime.now().isoformat(),
                })
            else:
                valid_results.append(result)

        successful = sum(1 for r in valid_results if r.get("success"))
        logger.info(f"Crawl complete: {successful}/{len(urls)} successful")

        return valid_results

    def _save_raw_data(self, url: str, data: Dict[str, Any]) -> None:
        """Save raw crawled data to disk"""
        try:
            # Create filename from URL
            filename = url.replace("https://", "").replace("http://", "")
            filename = filename.replace("/", "_").replace(":", "_")
            filename = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            filepath = self.raw_data_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved raw data to {filepath}")

        except Exception as e:
            logger.error(f"Failed to save raw data: {str(e)}")


# Example usage
if __name__ == "__main__":
    async def test():
        scraper = PharmaScraper()

        # Test single URL
        test_url = "https://www.fda.gov/drugs/news-events-human-drugs/fda-approvals"
        result = await scraper.crawl_url(test_url)

        print(f"Crawl result: Success={result.get('success')}")
        if result.get('success'):
            print(f"Title: {result.get('title')}")
            print(f"Content length: {len(result.get('markdown', ''))}")

    asyncio.run(test())
