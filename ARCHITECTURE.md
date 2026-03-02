# 🏗️ Architecture Documentation

## System Overview

The Pharma Intelligence System is a streamlined AI-powered platform that provides comprehensive pharmaceutical drug analysis through a single unified interface combining web crawling and four specialized AI agents.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    USER INTERFACE                         │
│                 (Streamlit Dashboard)                      │
│           Home Page  |  Quick Search Page                 │
└──────────────────────┬───────────────────────────────────┘
                       │
              ┌────────▼─────────┐
              │   Drug Name      │
              │   Input          │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │  AI URL Finder   │
              │  (Gemini AI)     │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │  Web Crawler     │
              │  (Crawl4AI)      │
              │  FDA/CDSCO/EMA   │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │  Data Extractor  │
              │  → drug_record   │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │  Agent           │
              │  Orchestrator    │
              └────────┬─────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼────┐  ┌──────▼─────┐  ┌─────▼────────┐
│Validation │  │  Medical   │  │  Compliance  │
│  Agent    │  │  Agent     │  │   Agent      │
└──────┬────┘  └──────┬─────┘  └─────┬────────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
              ┌────────▼─────────┐
              │   Executive      │
              │   Summary Agent  │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │  Analysis        │
              │  Results         │
              │  (Tabbed View +  │
              │   JSON Export)   │
              └──────────────────┘
```

## Component Architecture

### 1. **User Interface Layer**

#### Streamlit Dashboard (`dashboard/app.py`)
- **Purpose**: Simple, focused web interface for drug analysis
- **Technology**: Streamlit framework
- **Pages**:
  - **🏠 Home**: System overview and quick start guide
  - **🔎 Quick Search**: Single unified drug analysis interface
- **Features**:
  - Real-time progress tracking with visual indicators
  - Live data source badges (Crawled vs AI Knowledge)
  - Tabbed results display (4 tabs: Validation, Medical, Compliance, Executive)
  - One-click JSON export
  - Session-based state management

#### Unified Quick Search Flow:

```python
User Input: "Bisotab 2.5"
    ↓
Step 1: AI URL Discovery
    ├─ Gemini AI generates search prompt
    ├─ AI identifies likely FDA/CDSCO/EMA URLs
    └─ Returns 3 most relevant drug-specific URLs
    ↓
Step 2: Web Crawling (Crawl4AI + Playwright)
    ├─ PharmaScraper crawls returned URLs
    ├─ JavaScript-enabled browser automation
    ├─ HTML extraction and parsing
    └─ PharmaDataExtractor extracts drug info
    ↓
Step 3: Data Assembly
    ├─ If crawling succeeds: use fresh data
    ├─ If crawling fails: AI generates data
    └─ Creates drug_record dictionary
    ↓
Step 4: Multi-Agent Analysis
    ├─ Validation Agent (quality check)
    ├─ Medical Agent (competitors, market)
    ├─ Compliance Agent (regulatory, risk)
    └─ Executive Agent (strategic summary)
    ↓
Step 5: Display Results
    └─ 4 tabbed views + JSON export option
```

---

### 2. **Data Acquisition Layer**

#### Quick Search (`dashboard/app.py:174-290`)
```python
Class: N/A (inline implementation)
Input: drug_name (string)
Process:
  1. Generate AI search prompt
  2. Call Gemini AI via llm.invoke()
  3. Parse structured response
  4. Extract fields into drug_record
Output: drug_record dictionary
```

#### Web Crawler (`crawler/`)

**PharmaScraper** (`crawler/scraper.py`)
```python
Class: PharmaScraper
Methods:
  - crawl_url(url) → Dict[success, html, markdown, metadata]
  - crawl_multiple(urls) → List[Dict]
  - _save_raw_data(url, data)

Technology: Crawl4AI (AsyncWebCrawler)
Process:
  1. Async HTTP request
  2. JavaScript rendering (if needed)
  3. HTML extraction
  4. Metadata collection
  5. Save to data/raw/
```

**PharmaDataExtractor** (`crawler/extractors.py`)
```python
Class: PharmaDataExtractor
Methods:
  - extract_from_text(text, url) → List[drug_records]
  - _extract_drug_info(text) → Dict
  - _map_disease_category(keywords) → str
  - process_crawled_data(data) → List[drug_records]

Process:
  1. Pattern matching (regex)
  2. Keyword extraction
  3. Disease category mapping
  4. Structured data generation
```

---

### 3. **AI Agent Layer**

#### Agent Orchestrator (`agents/main.py`)
```python
Class: AgentOrchestrator
LLM: Google Gemini 2.5 Flash (via LangChain)

Initialization:
  - ChatGoogleGenerativeAI(model="gemini-2.5-flash")
  - Creates 4 specialized agents

Methods:
  - process_record(drug_record) → complete_analysis
  - process_batch(records[]) → analyses[]
```

#### Agent 1: Validation Agent (`agents/validator.py`)
```python
Class: ExtractionValidatorAgent

Purpose: Validate data quality and accuracy

Process:
  1. Receive drug_record
  2. Generate validation prompt
  3. Call Gemini AI
  4. Parse response for:
     - QUALITY_SCORE (0-100)
     - STATUS (PASS/FAIL/NEEDS_REVIEW)
     - ISSUES (list)
     - CONFIDENCE (High/Medium/Low)

Output:
{
  "quality_score": 95,
  "validation_status": "PASS",
  "issues": [],
  "confidence": "High",
  "ai_analysis": "..."
}
```

#### Agent 2: Medical Insight Agent (`agents/medical.py`)
```python
Class: MedicalInsightAgent

Purpose: Analyze therapeutic category, competitors, market

Process:
  1. Receive drug_record
  2. Generate medical analysis prompt
  3. Call Gemini AI
  4. Parse response for:
     - THERAPEUTIC_CATEGORY
     - MECHANISM (how it works)
     - COMPETITORS (3-5 drugs)
     - MARKET_IMPACT (High/Medium/Low)
     - MARKET_SIZE
     - TARGET_POPULATION
     - RECOMMENDATIONS

Output:
{
  "therapeutic_category": "Cardiovascular - Beta Blocker",
  "mechanism_of_action": "Selectively blocks beta-1 receptors...",
  "competitors": ["Metoprolol", "Atenolol", ...],
  "market_impact": "Medium",
  "market_opportunity": "$10B annually",
  "recommendations": [...]
}
```

#### Agent 3: Compliance Agent (`agents/compliance.py`)
```python
Class: ComplianceAgent

Purpose: Assess regulatory requirements and risks

Process:
  1. Receive drug_record
  2. Generate compliance prompt
  3. Call Gemini AI
  4. Parse response for:
     - REGULATORY_BODY (FDA/EMA/CDSCO)
     - RISK_LEVEL (High/Medium/Low)
     - COMPLIANCE_REQUIREMENTS
     - SAFETY_CONCERNS
     - POST_MARKET activities
     - RECOMMENDATIONS

Output:
{
  "regulatory_body": "CDSCO (India)",
  "risk_level": "Medium",
  "compliance_requirements": [...],
  "safety_concerns": [...],
  "post_market_obligations": [...],
  "recommendations": [...]
}
```

#### Agent 4: Executive Summary Agent (`agents/executive.py`)
```python
Class: ExecutiveSummaryAgent

Purpose: Synthesize insights into executive summary

Process:
  1. Receive drug_record + all 3 agent outputs
  2. Use Python logic (NOT AI) to synthesize
  3. Generate structured summary

Output:
{
  "headline": "One-line summary",
  "key_facts": ["fact1", "fact2", ...],
  "strategic_implications": [...],
  "competitive_impact": [...],
  "risk_factors": [...],
  "recommended_actions": [...],
  "decision_points": [...]
}

Note: This agent uses rule-based logic, not AI calls
```

---

### 4. **Configuration Layer**

#### Settings (`config/settings.py`)
```python
Environment Variables:
  - GEMINI_API_KEY
  - AGENT_MODEL
  - AGENT_TEMPERATURE
  - LOG_LEVEL
  - DATABASE_URL (optional)
  - VECTOR_DB_PATH

Configuration:
  - Data directories
  - Log settings
  - Target URLs for crawling
```

---

## Data Flow

### Complete Quick Search Flow (Hybrid: Web Crawling + AI)

```
User enters "Bisotab 2.5"
    ↓
[PHASE 1: URL DISCOVERY]
Dashboard creates AI URL finder prompt
    ↓
Gemini AI analyzes drug name
    ↓
Returns 3 likely URLs:
  - https://www.fda.gov/drugs/...
  - https://cdsco.gov.in/...
  - https://www.ema.europa.eu/...
    ↓
[PHASE 2: WEB CRAWLING]
PharmaCrawler.run(discovered_urls)
    ↓
PharmaScraper.crawl_multiple() → HTML data (Playwright browser)
    ↓
PharmaDataExtractor.extract_from_text() → drug_record
    ↓
[FALLBACK: If crawling fails or extracts nothing]
Gemini AI generates drug_record from knowledge base
    ↓
Dashboard shows badge: "Fresh Crawled Data" or "AI Knowledge"
    ↓
[PHASE 3: MULTI-AGENT ANALYSIS]
AgentOrchestrator.process_record(drug_record)
    ↓
Agent 1 (Validation):
  - Quality score: 95/100
  - Status: PASS
  - Issues: None
    ↓
Agent 2 (Medical):
  - Therapeutic category: Cardiovascular - Beta Blocker
  - Competitors: [Metoprolol, Atenolol, Carvedilol]
  - Market impact: Medium
    ↓
Agent 3 (Compliance):
  - Regulatory body: CDSCO (India)
  - Risk level: Medium
  - Safety concerns: [Standard monitoring]
    ↓
Agent 4 (Executive):
  - Headline: Strategic summary
  - Key facts: [5 bullet points]
  - Recommendations: [3-5 actions]
    ↓
[PHASE 4: DISPLAY RESULTS]
4 tabbed views rendered:
  ✅ Validation | 🏥 Medical | ⚖️ Compliance | 📋 Executive
    ↓
User clicks "Download JSON" → Complete analysis exported
```

**Key Points:**
- **Hybrid Approach**: Tries web crawling first, falls back to AI
- **Single Unified Flow**: No separate modes for user to choose
- **Transparent Source**: Always shows where data came from
- **Fast Execution**: ~15 seconds end-to-end
- **High Success Rate**: AI fallback ensures 100% completion

---

## Technology Stack

### Core Technologies
- **Language**: Python 3.10+
- **LLM**: Google Gemini 2.5 Flash
- **AI Framework**: LangChain + CrewAI
- **Web Framework**: Streamlit
- **Web Scraping**: Crawl4AI, BeautifulSoup
- **Async**: asyncio for concurrent operations

### Key Libraries
```python
langchain-google-genai  # Gemini integration
crewai                  # Multi-agent framework
crawl4ai                # Web scraping
streamlit               # Dashboard
loguru                  # Logging
pydantic                # Data validation
beautifulsoup4          # HTML parsing
```

---

## Design Patterns

### 1. **Agent Pattern**
Each AI agent is a separate class with:
- Single responsibility (validation, medical, compliance, executive)
- Independent prompt engineering
- Consistent input/output interface
- Stateless operation (no shared state between agents)

### 2. **Orchestrator Pattern**
AgentOrchestrator coordinates all agents:
- Manages single shared LLM instance
- Sequential agent execution with progress tracking
- Result aggregation into unified structure
- Error handling with fallback responses

### 3. **Fallback Pattern**
Graceful degradation when web crawling fails:
- **Primary**: Attempt web crawling from discovered URLs
- **Fallback**: Use AI knowledge if crawling returns no data
- **Transparent**: Always indicate data source to user
- **Reliable**: Ensures 100% completion rate

### 4. **Pipeline Pattern**
Linear data processing flow:
- URL Discovery → Web Crawling → Data Extraction → AI Analysis → Display
- Each stage depends on previous stage
- Clear separation of concerns
- Easy to debug and monitor

---

## Scalability Considerations

### Current Architecture Characteristics
- **Sequential Processing**: Clean, predictable execution flow
- **Single LLM Instance**: Shared Gemini connection across all agents
- **Session-based Storage**: No database overhead
- **Synchronous Crawling**: One drug at a time
- **Stateless Design**: Each request is independent

### Current Performance
- **Single Drug Analysis**: ~15 seconds
  - URL Discovery: 3-5s
  - Web Crawling: 2-4s (or instant fallback)
  - Agent Analysis: 8-10s (4 agents × 2-2.5s each)
  - UI Rendering: 1s
- **Success Rate**: 100% (with AI fallback)
- **Crawling Success**: ~10-20% (HTML parsing challenges)

### Scaling Strategies (When Needed)

**For Higher Throughput:**
1. **Parallel Agent Execution**: Run 4 agents concurrently (4x faster)
2. **Batch Processing**: Analyze multiple drugs in parallel
3. **Caching Layer**: Redis for recently analyzed drugs
4. **Load Balancing**: Multiple Streamlit instances behind load balancer

**For Cost Optimization:**
5. **Smart Fallback**: Skip crawling for frequently-searched drugs
6. **Result Caching**: Store analysis for 24 hours
7. **Model Selection**: Use Haiku for simpler analyses

**Current Bottlenecks:**
- **LLM API Calls**: 5 Gemini calls per drug (URL finder + 4 agents)
- **Web Crawling**: Playwright browser startup overhead
- **Sequential Agents**: Could be parallelized for 4x speedup

---

## Security Considerations

### Current Implementation
✅ **API Key Protection**:
- Keys in `.env` file (not committed)
- Environment variable access only

✅ **Input Validation**:
- Form validation in Streamlit
- URL validation for crawler

⚠️ **Areas to Improve**:
- No authentication/authorization
- No rate limiting
- No input sanitization for SQL (DB disabled)
- API keys exposed in server memory

### Recommendations for Production
1. Add user authentication (OAuth2)
2. Implement rate limiting per user
3. Add input sanitization
4. Use secrets management (AWS Secrets Manager, etc.)
5. Enable HTTPS
6. Add audit logging

---

## Performance Metrics

### End-to-End Response Time: ~15 seconds

**Phase Breakdown:**
1. **URL Discovery** (AI): 3-5s
   - Single Gemini API call
   - Generates 3 likely URLs
2. **Web Crawling** (Playwright): 2-4s
   - Parallel crawling of 3 URLs
   - HTML extraction
   - Falls back instantly if no results
3. **Data Extraction**: 1-2s
   - Pattern matching on HTML
   - Dictionary assembly
4. **AI Agent Analysis**: 8-10s (sequential)
   - Agent 1 (Validation): 2-2.5s
   - Agent 2 (Medical): 2-2.5s
   - Agent 3 (Compliance): 2-2.5s
   - Agent 4 (Executive): 1s (rule-based, no AI)
5. **UI Rendering**: ~1s
   - Tab layout rendering
   - JSON preparation

**Fallback Path (No Crawling):** ~12 seconds
- Skips web crawling phase (phases 2-3)
- AI generates full drug_record directly
- Proceeds to agent analysis

### Resource Usage
- **Memory**: ~300MB (Streamlit + Playwright)
- **CPU**: Low (mostly I/O bound - API calls)
- **Network**: ~5MB per analysis (5 API calls + web crawling)
- **Storage**: ~15KB per analysis (drug_record + 4 agent results)
- **Browser Cache**: ~50MB (Playwright Chromium)

---

## Error Handling

### Retry Logic
- No automatic retries currently
- AI failures fall back to default values

### Fallback Mechanisms
```python
# Example from validator.py
try:
    ai_response = llm.invoke(prompt)
    # Parse AI response
except Exception as e:
    logger.error(f"AI failed: {e}")
    # Return fallback result
    return {
        "quality_score": 70,
        "validation_status": "NEEDS_REVIEW",
        "issues": ["Could not perform AI validation"]
    }
```

---

## Monitoring & Logging

### Logging Framework
```python
from loguru import logger

# Configured in each module
logger.add("logs/pharma_intel.log", rotation="1 day")
```

### Log Levels
- **INFO**: Agent processing, API calls
- **ERROR**: Failures, exceptions
- **DEBUG**: Detailed execution flow (not enabled)

### Key Metrics Logged
- Agent execution time
- API call success/failure
- Data extraction results
- User actions

---

## Deployment Architecture

### Current: Local Development
```
User's Machine
  ├─ Streamlit Server (port 8501)
  ├─ Python venv
  └─ Logs (local files)
```

### Recommended: Production
```
Cloud Infrastructure (AWS/GCP/Azure)
  ├─ Load Balancer
  ├─ Streamlit Containers (Docker)
  ├─ Redis Cache
  ├─ S3/Cloud Storage (logs, data, exports)
  └─ Secrets Manager
```

---

## API Integration

### Gemini AI API
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)

response = llm.invoke("prompt here")
```

### Rate Limits (Gemini Free Tier)
- 60 requests per minute
- 1,500 requests per day
- Recommend implementing queuing for production

---

## Testing Strategy

### Unit Tests (Planned)
- Agent output parsing
- Data extraction logic
- Configuration loading

### Integration Tests (Planned)
- End-to-end agent flow
- Database operations
- Crawler functionality

### Manual Testing (Current)
- UI testing via dashboard
- Sample drug analysis
- Error scenarios

---

## Maintenance & Operations

### Monitoring Checklist
- [ ] API key expiration
- [ ] Gemini API rate limits
- [ ] Log file rotation
- [ ] Disk space (data/logs)
- [ ] Error rates

### Regular Tasks
- Review logs weekly
- Update dependencies monthly
- Backup analysis history
- Monitor API costs

---

## Future Enhancements

### Phase 1 (Q2 2026)
- Add authentication
- Enable database integration
- Implement caching
- Add REST API

### Phase 2 (Q3 2026)
- Scheduled crawling
- Email notifications
- Advanced analytics
- Multi-language support

### Phase 3 (Q4 2026)
- Mobile app
- Slack/Teams integration
- Custom agent creation
- White-label solution

---

**Document Version**: 1.0.0
**Last Updated**: March 2026
**Maintained By**: Mahendra Gajera
