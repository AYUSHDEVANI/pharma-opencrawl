"""
Unit tests for configuration module
"""
import unittest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings


class TestConfiguration(unittest.TestCase):
    """Test configuration loading and validation"""

    def test_gemini_api_key_loaded(self):
        """Test that Gemini API key is loaded from environment"""
        # Should have a key (even if empty string)
        self.assertIsNotNone(settings.GEMINI_API_KEY)
        self.assertIsInstance(settings.GEMINI_API_KEY, str)

    def test_agent_model_configured(self):
        """Test that agent model is configured"""
        self.assertIsNotNone(settings.AGENT_MODEL)
        self.assertIn("gemini", settings.AGENT_MODEL.lower())

    def test_data_directories_exist(self):
        """Test that data directories are properly configured"""
        self.assertIsNotNone(settings.RAW_DATA_DIR)
        self.assertIsNotNone(settings.PROCESSED_DATA_DIR)
        self.assertIsNotNone(settings.VECTOR_DB_PATH)

    def test_log_level_valid(self):
        """Test that log level is valid"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.assertIn(settings.LOG_LEVEL, valid_levels)

    def test_agent_temperature_range(self):
        """Test that agent temperature is in valid range"""
        self.assertGreaterEqual(settings.AGENT_TEMPERATURE, 0.0)
        self.assertLessEqual(settings.AGENT_TEMPERATURE, 1.0)

    def test_target_urls_format(self):
        """Test that target URLs are properly formatted"""
        self.assertIsNotNone(settings.TARGET_URLS)
        self.assertIsInstance(settings.TARGET_URLS, list)
        for url in settings.TARGET_URLS:
            self.assertTrue(url.startswith("http"))


class TestEnvironmentVariables(unittest.TestCase):
    """Test environment variable handling"""

    def test_required_env_vars_present(self):
        """Test that required environment variables can be accessed"""
        # GEMINI_API_KEY should be accessible (even if empty)
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.assertIsInstance(gemini_key, str)

    def test_optional_env_vars_have_defaults(self):
        """Test that optional variables have sensible defaults"""
        # These should have defaults even if not in .env
        self.assertIsNotNone(settings.AGENT_TEMPERATURE)
        self.assertIsNotNone(settings.AGENT_MAX_TOKENS)
        self.assertIsNotNone(settings.LOG_LEVEL)


if __name__ == "__main__":
    unittest.main()
