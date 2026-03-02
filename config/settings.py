"""
Configuration settings for Pharma Intelligence System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini/gemini-2.0-flash-exp")
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.3"))
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "2000"))

# Crawler Configuration
CRAWL_FREQUENCY_HOURS = int(os.getenv("CRAWL_FREQUENCY_HOURS", "24"))
MAX_CONCURRENT_CRAWLS = int(os.getenv("MAX_CONCURRENT_CRAWLS", "5"))
USER_AGENT = os.getenv("USER_AGENT", "PharmaIntelBot/1.0")

# Target URLs
TARGET_URLS = os.getenv("TARGET_URLS", "").split(",")
if not TARGET_URLS or TARGET_URLS == [""]:
    TARGET_URLS = [
        "https://www.fda.gov/drugs",
        "https://www.ema.europa.eu/en/medicines",
        "https://cdsco.gov.in",
    ]

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "pharma_intel.log"))

# Data extraction patterns
EXTRACTION_FIELDS = [
    "drug_name",
    "approval_status",
    "disease_category",
    "region",
    "price",
    "approval_date",
    "manufacturer",
    "indication",
]
