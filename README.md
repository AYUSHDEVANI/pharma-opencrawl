# 💊 Pharma Intelligence System

AI-powered pharmaceutical intelligence platform that provides comprehensive drug analysis using multi-agent AI systems. Get instant insights on drugs by simply entering the drug name.

## 🌟 Overview

**🔎 Quick Search - The Complete Solution:**

Simply enter a drug name (e.g., "Bisotab 2.5", "Ozempic") and the system will:
- 🕷️ **Auto-crawl official websites** (FDA, CDSCO, EMA) for latest data
- 📋 **Extract real-time information** from regulatory sources
- 🤖 **Run AI analysis** with 4 specialized agents
- 📊 **Generate comprehensive report** with insights and recommendations
- Complete analysis in ~15 seconds

**AI Analysis Pipeline:**
- ✅ **Data Validation** - Quality scoring and issue detection
- 🏥 **Medical Insights** - Therapeutic analysis and competitor identification
- ⚖️ **Compliance Assessment** - Regulatory requirements and risk evaluation
- 📋 **Executive Summary** - Strategic recommendations for leadership

## Architecture

```
User Input (Drug Name)
     ↓
AI-Powered URL Discovery
     ↓
Web Crawler (FDA/CDSCO/EMA)
     ↓
Data Extraction & Parsing
     ↓
Multi-Agent AI Analysis (CrewAI + Gemini)
  ├─ Extraction Validator Agent
  ├─ Medical Insight Agent
  ├─ Risk & Compliance Agent
  └─ Executive Summary Agent
     ↓
Comprehensive Analysis Report
```

## Features

**Intelligent Web Crawling (Crawl4AI + Playwright)**
- AI-powered URL discovery for specific drugs
- Auto-crawls FDA, EMA, and CDSCO official portals
- JavaScript-enabled browser automation
- Real-time data extraction from regulatory sources
- Fallback to AI knowledge if web data unavailable

**Multi-Agent AI Analysis (CrewAI + Google Gemini)**
- **Extraction Validator**: Validates and scores data quality (0-100)
- **Medical Insight Agent**: Therapeutic analysis and competitor identification
- **Risk & Compliance Agent**: Regulatory assessment and safety concerns
- **Executive Summary Agent**: Strategic insights for decision-makers

**Streamlined Dashboard**
- Single-page Quick Search interface
- Real-time progress tracking
- Tabbed results display (Validation, Medical, Compliance, Executive)
- JSON export for all analysis results
- Session-based analysis with live data indicators

## Quick Start

### Prerequisites

- Python 3.10+
- Google Gemini API key (free at [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone and setup**
```bash
git clone <your-repo-url>
cd pharma-opencrawl
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers** (required for web crawling)
```bash
playwright install chromium
```

5. **Configure API Key**
```bash
# Edit .env file and add your Gemini API key:
GEMINI_API_KEY=your_api_key_here
AGENT_MODEL=gemini-2.5-flash
```

**Get Free Gemini API Key:**
- Visit: https://makersuite.google.com/app/apikey
- Sign in with Google account
- Create API key
- Paste in `.env` file

**Note:** The web crawler uses Playwright for browser automation. The `playwright install chromium` command downloads the Chromium browser (~280MB).

### Run the System

**Launch Dashboard**
```bash
streamlit run dashboard/app.py
```

Then open your browser to: `http://localhost:8501`

**Dashboard Features:**
- **🏠 Home**: System overview and quick start guide
- **🔎 Quick Search**: Complete drug analysis solution
  - Enter drug name
  - Auto-crawl official websites
  - Get instant AI-powered analysis
  - Download JSON reports

---

**Command Line Options** (Advanced)

Test mode with sample data:
```bash
python main.py --mode test
```

Full pipeline (crawl + analyze):
```bash
python main.py --mode full --urls https://www.fda.gov/drugs
```

Crawler only:
```bash
python main.py --mode crawler
```

Agents only:
```bash
python main.py --mode agents
```

## Project Structure

```
pharma-opencrawl/
├── crawler/              # Web crawling module
│   ├── __init__.py
│   ├── main.py          # Main crawler orchestrator
│   ├── scraper.py       # Crawl4AI implementation
│   └── extractors.py    # Data extraction logic
├── agents/              # Multi-agent AI module
│   ├── __init__.py
│   ├── main.py          # Agent orchestrator
│   ├── validator.py     # Extraction validator agent
│   ├── medical.py       # Medical insight agent
│   ├── compliance.py    # Risk & compliance agent
│   └── executive.py     # Executive summary agent
├── storage/             # Data storage module
│   └── __init__.py
├── config/              # Configuration
│   ├── __init__.py
│   └── settings.py      # Settings and environment
├── dashboard/           # Web dashboard (Streamlit)
│   └── app.py
├── data/                # Data storage
│   ├── raw/            # Raw HTML
│   ├── processed/      # Cleaned JSON
│   └── vectors/        # Vector embeddings
├── logs/                # Application logs
├── scripts/             # Utility scripts
│   └── init_db.py
├── .env.example         # Environment template
├── .gitignore
├── requirements.txt
├── main.py             # Main entry point
├── usecase.txt         # Original use case
└── README.md
```

## 📖 Usage Examples

### Example 1: Quick Search for Indian Drug
```
1. Open dashboard → Click "🔎 Quick Search"
2. Enter: "Bisotab 2.5"
3. Click "🔍 Search & Analyze"
4. System automatically:
   - AI finds specific drug URLs on FDA/CDSCO/EMA
   - Crawls official regulatory websites
   - Extracts real-time data from HTML
5. Get comprehensive results:
   - Drug Name: Bisotab 2.5
   - Generic: Bisoprolol
   - Category: Cardiovascular (Beta-blocker)
   - Manufacturer: Torrent Pharmaceuticals (from CDSCO)
   - Region: India
   - Source: Official CDSCO website (live data)
   - Quality Score: 95/100
   - Risk Level: Medium
```

**⚡ Time:** ~15 seconds (includes AI-powered crawling)

### Example 2: Full Analysis Pipeline

**Input**: User searches "Ozempic"

**Web Crawling** (Step 1):
1. **Auto-crawl official websites**:
   - Crawls FDA.gov for "Ozempic"
   - Crawls CDSCO.gov.in
   - Crawls EMA.europa.eu
   - Extracts from HTML: Manufacturer, approval date, indications
   - Result: Fresh data from official sources

**AI Processing** (Step 2):
1. **Validation Agent** checks crawled data:
   - Validates extracted information

2. **Medical Insight Agent** analyzes crawled data:
   - Competitors: Metformin, Insulin, Trulicity, Mounjaro
   - Market Impact: High
   - Market Size: $60B global diabetes market

4. **Compliance Agent** assesses:
   - Regulatory Body: FDA (USA)
   - Risk Level: Medium
   - Safety Concerns: Standard monitoring required

5. **Executive Summary** generates:
   - Headline: "Ozempic - Blockbuster GLP-1 drug dominating diabetes market"
   - Key Facts: 3-5 bullet points
   - Strategic Implications
   - Recommended Actions

**Output**: Complete analysis with downloadable JSON report

## ⚙️ Configuration

Key settings in `.env`:

```env
# LLM Configuration (REQUIRED)
GEMINI_API_KEY=your_gemini_api_key_here
AGENT_MODEL=gemini-2.5-flash
AGENT_TEMPERATURE=0.3
AGENT_MAX_TOKENS=2000

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/pharma_intel.log

# Crawler Configuration
CRAWL_FREQUENCY_HOURS=24
TARGET_URLS=https://www.fda.gov/drugs,https://www.ema.europa.eu,https://cdsco.gov.in
```

**Note**: The system works with just the Gemini API key - no additional setup required.

## Use Cases

**Pharma Companies**
- Track competitor drug approvals
- Monitor regulatory changes
- Identify market opportunities

**Healthcare Organizations**
- Stay updated on new treatments
- Track drug pricing trends
- Compliance monitoring

**Research Institutions**
- Literature monitoring
- Drug development tracking
- Clinical trial updates

**Regulatory Bodies**
- Market surveillance
- Compliance monitoring
- Trend analysis

## 🛠️ Tech Stack

- **LLM**: Google Gemini 2.5 Flash (via LangChain)
- **Multi-Agent AI**: CrewAI Framework
- **Web Crawling**: Crawl4AI, BeautifulSoup
- **Dashboard**: Streamlit
- **Languages**: Python 3.10+
- **Key Libraries**: LangChain, loguru, asyncio

## ✅ Features Status

**✅ Core Features (Completed):**
- [x] **Quick Search with Auto-Crawling** - AI-powered URL discovery + web scraping
- [x] **4 Specialized AI Agents** - Validator, Medical, Compliance, Executive
- [x] **Streamlined Dashboard** - Simple, focused Streamlit UI
- [x] **Data Export** - Download comprehensive JSON reports
- [x] **Live Data Indicators** - Shows whether data is from crawling or AI
- [x] **Real-time Progress Tracking** - Visual feedback during analysis
- [x] **Fallback Intelligence** - Uses AI knowledge if web data unavailable

**🚧 Future Enhancements:**
- [ ] API Endpoints - REST API for programmatic access
- [ ] Scheduled Crawling - Automated daily monitoring
- [ ] Persistent Database - Long-term analysis storage
- [ ] Batch Processing - Analyze multiple drugs simultaneously
- [ ] Email Alerts - Notifications for new drug approvals

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License

## Contact

Mahendra Gajera
- Email: mahendra.gajera@gmail.com
- GitHub: [github.com/mahendra-gajera](https://github.com/mahendra-gajera)

## 🎥 Demo

### Quick Search Demo
```
1. Enter drug name: "Ozempic"
2. AI automatically finds:
   ✅ Manufacturer: Novo Nordisk
   ✅ Category: Antidiabetic (GLP-1 agonist)
   ✅ Approval: FDA (United States)
   ✅ Indication: Type 2 diabetes
3. Complete analysis in 15 seconds
```

### Dashboard Overview

**🏠 Home Page:**
- Clean, focused interface
- Overview of 4 AI agents
- Quick start guide with examples
- System architecture diagram

**🔎 Quick Search Page:**
- Single drug name input field
- Real-time progress indicators
- Live data source badges (crawled vs AI)
- 4 tabbed result sections:
  - ✅ Validation (quality score, issues)
  - 🏥 Medical Insights (competitors, market impact)
  - ⚖️ Compliance (regulatory body, risk level)
  - 📋 Executive Summary (strategic recommendations)
- One-click JSON export

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Roadmap

**Phase 1: Core Enhancements**
- [ ] Add batch processing (analyze multiple drugs)
- [ ] Implement persistent database storage
- [ ] Add user authentication

**Phase 2: Integration & Automation**
- [ ] REST API endpoints for programmatic access
- [ ] Scheduled automatic crawling
- [ ] Email/Slack notifications for new approvals

**Phase 3: Advanced Features**
- [ ] PDF report generation
- [ ] Multi-language support (Spanish, Chinese)
- [ ] Advanced search filters (by category, region, risk level)
- [ ] Historical trend analysis

## 🐛 Known Issues & Limitations

- **Web Crawling Success Rate**: ~10-20% (HTML parsing is complex)
  - System automatically falls back to AI knowledge when crawling fails
- **No Persistent Storage**: Analysis results are session-based only
  - Use JSON export to save results manually
- **Rate Limits**: Gemini free tier has 60 requests/min, 1,500/day
- **Playwright Browser**: First-time setup requires ~280MB download

## ❓ FAQ

**Q: Do I need a paid API key?**
A: No! Google Gemini offers a generous free tier.

**Q: Can I use this offline?**
A: No, it requires internet for AI analysis and web crawling.

**Q: What drugs can I search for?**
A: Any drug with public information (approved, clinical trials, etc.)

**Q: Can I analyze my company's internal drugs?**
A: Currently the system searches public sources (FDA/CDSCO/EMA). For proprietary drugs, the system will use AI knowledge which may have limited information about unpublished drugs.

**Q: How accurate is the AI analysis?**
A: Gemini AI is trained on vast pharmaceutical data, but always verify critical information with official sources.

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 👤 Contact & Support

**Mahendra Gajera**
- 📧 Email: mahendra.gajera@gmail.com
- 💼 LinkedIn: [linkedin.com/in/mahendra-gajera](https://linkedin.com/in/mahendra-gajera)
- 🐙 GitHub: [@mahendra-gajera](https://github.com/mahendra-gajera)

**Found a bug?** Open an issue on GitHub
**Need help?** Check the documentation or create a discussion

---

⭐ **If you find this project useful, please give it a star!** ⭐

**Status**: ✅ Production Ready
**Last Updated**: March 2026
**Version**: 1.0.0
