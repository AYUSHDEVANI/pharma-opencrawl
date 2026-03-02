"""
Unit tests for data extraction module
"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawler.extractors import PharmaDataExtractor


class TestPharmaDataExtractor(unittest.TestCase):
    """Test pharmaceutical data extraction"""

    def setUp(self):
        """Set up test fixtures"""
        self.extractor = PharmaDataExtractor()

    def test_extractor_initialization(self):
        """Test that extractor initializes properly"""
        self.assertIsNotNone(self.extractor)

    def test_map_disease_category_diabetes(self):
        """Test disease category mapping for diabetes keywords"""
        category = self.extractor._map_disease_category(["diabetes", "blood sugar"])
        self.assertEqual(category, "Antidiabetic")

    def test_map_disease_category_cancer(self):
        """Test disease category mapping for cancer keywords"""
        category = self.extractor._map_disease_category(["cancer", "tumor"])
        self.assertEqual(category, "Oncology")

    def test_map_disease_category_heart(self):
        """Test disease category mapping for cardiovascular keywords"""
        category = self.extractor._map_disease_category(["heart", "cardiovascular"])
        self.assertEqual(category, "Cardiovascular")

    def test_map_disease_category_unknown(self):
        """Test disease category mapping for unknown keywords"""
        category = self.extractor._map_disease_category(["unknown", "xyz"])
        self.assertEqual(category, "Other")

    def test_extract_drug_info_with_sample_text(self):
        """Test drug information extraction from sample text"""
        sample_text = """
        FDA approves Ozempic (semaglutide) manufactured by Novo Nordisk
        for the treatment of Type 2 diabetes. The drug was approved on
        December 5, 2017. Price: $950 per month.
        """

        drug_info = self.extractor._extract_drug_info(sample_text)

        self.assertIsNotNone(drug_info)
        self.assertIn("drug_name", drug_info)
        self.assertIn("approval_status", drug_info)

    def test_extract_from_text_returns_list(self):
        """Test that extract_from_text returns a list"""
        sample_text = "FDA approves new drug"
        url = "https://www.fda.gov/drugs"

        records = self.extractor.extract_from_text(sample_text, url)

        self.assertIsInstance(records, list)

    def test_process_crawled_data_with_valid_input(self):
        """Test processing of crawled data"""
        crawled_data = {
            "success": True,
            "url": "https://www.fda.gov/drugs",
            "markdown": "FDA approves Keytruda for cancer treatment",
            "cleaned_html": "<p>FDA approves Keytruda</p>"
        }

        records = self.extractor.process_crawled_data(crawled_data)

        self.assertIsInstance(records, list)

    def test_process_crawled_data_with_failed_crawl(self):
        """Test processing of failed crawl"""
        crawled_data = {
            "success": False,
            "url": "https://example.com",
            "error": "Connection timeout"
        }

        records = self.extractor.process_crawled_data(crawled_data)

        # Should return empty list for failed crawls
        self.assertEqual(records, [])


class TestDiseaseMapping(unittest.TestCase):
    """Test disease category mapping logic"""

    def setUp(self):
        """Set up test fixtures"""
        self.extractor = PharmaDataExtractor()

    def test_multiple_keywords_priority(self):
        """Test that first matching category is returned"""
        # If both diabetes and cancer keywords present, should pick first match
        category = self.extractor._map_disease_category(["diabetes", "cancer"])
        self.assertIn(category, ["Antidiabetic", "Oncology"])

    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive"""
        category1 = self.extractor._map_disease_category(["DIABETES"])
        category2 = self.extractor._map_disease_category(["diabetes"])
        self.assertEqual(category1, category2)

    def test_empty_keywords_list(self):
        """Test handling of empty keywords list"""
        category = self.extractor._map_disease_category([])
        self.assertEqual(category, "Other")


if __name__ == "__main__":
    unittest.main()
