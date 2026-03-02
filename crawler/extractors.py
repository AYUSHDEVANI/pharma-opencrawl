"""
Data extraction logic for pharma/health content
"""
import re
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime
import json

from config.settings import EXTRACTION_FIELDS, PROCESSED_DATA_DIR


class PharmaDataExtractor:
    """Extract structured data from crawled pharma/health content"""

    def __init__(self):
        self.extraction_fields = EXTRACTION_FIELDS
        self.processed_data_dir = PROCESSED_DATA_DIR

    def extract_from_text(self, text: str, metadata: Dict = None) -> List[Dict[str, Any]]:
        """
        Extract pharma data from text content

        Args:
            text: Raw text or markdown content
            metadata: Additional metadata from crawler

        Returns:
            List of extracted drug/approval records
        """
        extracted_records = []

        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        for para in paragraphs:
            # Try to extract drug information
            record = self._extract_drug_info(para)

            if record and record.get("drug_name"):
                # Add metadata
                record["source_url"] = metadata.get("url", "") if metadata else ""
                record["extracted_at"] = datetime.now().isoformat()
                extracted_records.append(record)

        logger.info(f"Extracted {len(extracted_records)} records from text")
        return extracted_records

    def _extract_drug_info(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract drug information from a text paragraph

        Uses pattern matching and heuristics to identify pharma data
        """
        record = {
            "drug_name": None,
            "approval_status": None,
            "disease_category": None,
            "region": None,
            "price": None,
            "approval_date": None,
            "manufacturer": None,
            "indication": None,
        }

        # Drug name patterns (capitalize words, often ends with trademark)
        drug_pattern = r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b(?:\s*(?:\(|\u2122|\u00ae))?'
        drug_matches = re.findall(drug_pattern, text)

        # Approval status keywords
        approval_keywords = {
            "approved": "Approved",
            "authorization": "Approved",
            "cleared": "Cleared",
            "pending": "Pending",
            "rejected": "Rejected",
            "withdrawn": "Withdrawn",
        }

        for keyword, status in approval_keywords.items():
            if keyword.lower() in text.lower():
                record["approval_status"] = status
                break

        # Disease/therapeutic categories
        disease_keywords = {
            "diabetes": "Antidiabetic",
            "cancer": "Oncology",
            "cardiovascular": "Cardiovascular",
            "hypertension": "Antihypertensive",
            "infection": "Antiinfective",
            "pain": "Analgesic",
            "depression": "Antidepressant",
            "asthma": "Respiratory",
        }

        for keyword, category in disease_keywords.items():
            if keyword.lower() in text.lower():
                record["disease_category"] = category
                break

        # Region/geography
        region_keywords = {
            "FDA": "United States",
            "EMA": "European Union",
            "CDSCO": "India",
            "India": "India",
            "US": "United States",
            "Europe": "European Union",
        }

        for keyword, region in region_keywords.items():
            if keyword in text:
                record["region"] = region
                break

        # Price patterns (e.g., $1,000, ₹50,000, €500)
        price_pattern = r'[$₹€£]\s*[\d,]+(?:\.\d{2})?'
        price_match = re.search(price_pattern, text)
        if price_match:
            record["price"] = price_match.group(0)

        # Date patterns (various formats)
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # 12/31/2024
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # 2024-12-31
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',  # January 15, 2024
        ]

        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                record["approval_date"] = date_match.group(0)
                break

        # Drug name (take first capitalized word near approval keywords)
        if drug_matches and record["approval_status"]:
            # Simple heuristic: first drug name found
            record["drug_name"] = drug_matches[0]

        # Indication (text around "for", "treat", "indicated")
        indication_pattern = r'(?:for|treat|treating|indicated for)\s+([a-z\s]+?)(?:\.|,|$)'
        indication_match = re.search(indication_pattern, text.lower())
        if indication_match:
            record["indication"] = indication_match.group(1).strip()

        return record

    def process_crawled_data(self, crawled_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process crawled data and extract structured records

        Args:
            crawled_data: Output from PharmaScraper

        Returns:
            List of structured drug records
        """
        if not crawled_data.get("success"):
            logger.warning(f"Skipping failed crawl: {crawled_data.get('url')}")
            return []

        # Extract from markdown (cleaner than HTML)
        markdown = crawled_data.get("markdown", "")

        metadata = {
            "url": crawled_data.get("url"),
            "title": crawled_data.get("title"),
            "crawled_at": crawled_data.get("crawled_at"),
        }

        records = self.extract_from_text(markdown, metadata)

        # Save processed data
        if records:
            self._save_processed_data(records, crawled_data.get("url"))

        return records

    def _save_processed_data(self, records: List[Dict], source_url: str) -> None:
        """Save processed/extracted data to disk"""
        try:
            # Create filename
            filename = source_url.replace("https://", "").replace("http://", "")
            filename = filename.replace("/", "_").replace(":", "_")
            filename = f"processed_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            filepath = self.processed_data_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved {len(records)} processed records to {filepath}")

        except Exception as e:
            logger.error(f"Failed to save processed data: {str(e)}")


# Example usage
if __name__ == "__main__":
    extractor = PharmaDataExtractor()

    # Test with sample text
    sample_text = """
    The FDA has approved Ozempic (semaglutide) for the treatment of type 2 diabetes.
    The drug, manufactured by Novo Nordisk, was approved on December 5, 2017.
    Ozempic is indicated for improving glycemic control in adults with type 2 diabetes.
    The list price is approximately $950 per month.
    """

    records = extractor.extract_from_text(sample_text)

    print(f"Extracted {len(records)} records:")
    for record in records:
        print(json.dumps(record, indent=2))
