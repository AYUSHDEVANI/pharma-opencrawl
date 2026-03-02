"""
Pharma Intelligence System - Interactive Dashboard
Streamlit UI for drug analysis with AI agents
"""
import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.main import AgentOrchestrator
from crawler.main import PharmaCrawler
import asyncio

# Page config
st.set_page_config(
    page_title="Pharma Intelligence System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Sidebar
st.sidebar.markdown("## 💊 Pharma Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🔎 Quick Search"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("""
**Multi-Agent AI System** for pharmaceutical intelligence:
- ✅ Data Validation
- 🏥 Medical Insights
- ⚖️ Compliance Assessment
- 📋 Executive Summaries
""")

# Main content
if page == "🏠 Home":
    st.markdown('<div class="main-header">💊 Pharma Intelligence System</div>', unsafe_allow_html=True)

    st.markdown("""
    ### Welcome to the AI-Powered Pharmaceutical Intelligence Platform

    This system uses **4 specialized AI agents** to provide comprehensive drug analysis:
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 🤖 AI Agents

        1. **Extraction Validator Agent**
           - Validates data quality
           - Quality scoring (0-100)
           - Identifies missing information

        2. **Medical Insight Agent**
           - Therapeutic category analysis
           - Competitor identification
           - Market impact assessment
        """)

    with col2:
        st.markdown("""
        #### 🎯 Features

        3. **Risk & Compliance Agent**
           - Regulatory assessment
           - Safety concerns identification
           - Compliance requirements

        4. **Executive Summary Agent**
           - Strategic implications
           - Recommended actions
           - Decision points
        """)

    st.markdown("---")

    # Quick start
    st.markdown("### 🚀 Quick Start")
    st.info("""
    **🔎 Quick Search - The Complete Solution:**

    Just enter a drug name and we will automatically:
    - 🕷️ **Crawl official websites** (FDA, CDSCO, EMA) for latest data
    - 📋 **Extract real-time information** from regulatory sources
    - 🤖 **Run AI analysis** with 4 specialized agents
    - 📊 **Generate comprehensive report** with insights and recommendations

    💡 **Uses live web crawling** for the most accurate, up-to-date information!
    """)

    # Sample data
    with st.expander("📋 View Sample Analysis"):
        st.json({
            "drug_name": "Ozempic",
            "approval_status": "Approved",
            "disease_category": "Antidiabetic",
            "validation_score": 100,
            "market_impact": "High",
            "risk_level": "Medium"
        })

elif page == "🔎 Quick Search":
    st.markdown('<div class="main-header">🔎 Quick Drug Search</div>', unsafe_allow_html=True)

    st.markdown("""
    ### Just Enter the Drug Name - We'll Find Everything!

    Simply type the drug name and we'll automatically:
    - 🕷️ **Crawl official websites** (FDA, CDSCO, EMA) for latest data
    - 📋 Extract real-time approval status, manufacturer, indications
    - 🌍 Get current regulatory details from official sources
    - 🤖 Run complete AI agent analysis on fresh data

    ⚡ **Note:** This searches live websites for the most accurate, up-to-date information!
    """)

    st.markdown("---")

    # Drug name input
    col1, col2 = st.columns([3, 1])

    with col1:
        drug_name = st.text_input(
            "Drug Name",
            placeholder="e.g., Bisotab 2.5, Ozempic, Keytruda, Metformin",
            help="Enter the drug name (brand or generic)"
        )

    with col2:
        st.markdown("**Examples:**")
        st.markdown("- Bisotab 2.5")
        st.markdown("- Ozempic")
        st.markdown("- Keytruda")

    search_button = st.button("🔍 Search & Analyze", type="primary", use_container_width=True)

    if search_button:
        if not drug_name.strip():
            st.error("⚠️ Please enter a drug name")
        else:
            # Initialize orchestrator if needed
            if st.session_state.orchestrator is None:
                with st.spinner("Initializing AI agents..."):
                    try:
                        st.session_state.orchestrator = AgentOrchestrator()
                    except Exception as e:
                        st.error(f"❌ Failed to initialize agents: {str(e)}")
                        st.stop()

            # Step 1: Crawl official websites for drug information
            st.markdown("---")
            st.markdown("### 🕷️ Step 1: Crawling Official Websites")

            drug_info = None
            crawl_success = False

            with st.spinner(f"Searching for '{drug_name}' on official websites..."):
                try:
                    # Step 1a: Ask AI for likely URLs
                    url_finder_prompt = f"""
Find the most likely official FDA, CDSCO, or EMA webpage URLs for this drug: {drug_name}

Provide ONLY direct URLs to drug approval pages (not search pages). Format:

URL1: [Full URL to FDA/CDSCO/EMA drug page]
URL2: [Another URL if available]
URL3: [Another URL if available]

If you don't know specific URLs, write "UNKNOWN"
"""
                    url_response = st.session_state.orchestrator.llm.invoke(url_finder_prompt)
                    url_text = url_response.content

                    # Extract URLs from AI response
                    import re
                    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                    potential_urls = re.findall(url_pattern, url_text)

                    if potential_urls and len(potential_urls) > 0:
                        st.info(f"🌐 Found {len(potential_urls)} potential URL(s). Crawling...")

                        # Create and run crawler
                        from crawler.main import PharmaCrawler
                        crawler = PharmaCrawler()

                        # Run async crawler
                        extracted_records = asyncio.run(crawler.run(potential_urls[:3]))  # Limit to 3 URLs
                    else:
                        # No URLs found
                        extracted_records = []
                        st.warning("⚠️ AI couldn't find specific drug page URLs. Using AI knowledge...")

                    if extracted_records and len(extracted_records) > 0:
                        # Found data from crawling!
                        drug_info = extracted_records[0]  # Use first found record
                        crawl_success = True

                        st.success(f"✅ Found {len(extracted_records)} record(s) from official sources!")

                        with st.expander("📋 View Crawled Information", expanded=True):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown(f"**Drug Name:** {drug_info.get('drug_name', 'N/A')}")
                                st.markdown(f"**Approval Status:** {drug_info.get('approval_status', 'Unknown')}")
                                st.markdown(f"**Disease Category:** {drug_info.get('disease_category', 'Other')}")
                                st.markdown(f"**Region:** {drug_info.get('region', 'Global')}")

                            with col2:
                                st.markdown(f"**Manufacturer:** {drug_info.get('manufacturer', 'Unknown')}")
                                st.markdown(f"**Indication:** {drug_info.get('indication', 'N/A')}")
                                st.markdown(f"**Price:** {drug_info.get('price', 'N/A')}")
                                st.markdown(f"**Source:** {drug_info.get('source_url', 'Official Website')}")

                            st.markdown("**📊 Data Source:** Live data from official regulatory websites")

                    else:
                        # No data found from crawling - fallback to AI
                        st.warning("⚠️ No data found on official websites. Using AI knowledge as fallback...")

                        search_prompt = f"""
You are a pharmaceutical database expert. Find comprehensive information about the following drug:

Drug Name: {drug_name}

Provide detailed, accurate information in this exact format:

DRUG_NAME: [Official/brand name]
APPROVAL_STATUS: [Approved/Pending/Withdrawn/Rejected]
MANUFACTURER: [Company name]
DISEASE_CATEGORY: [Antidiabetic/Oncology/Cardiovascular/Antiinfective/Respiratory/Neurological/Immunology/Other]
INDICATION: [What it treats]
REGION: [Primary approval region - United States/European Union/India/China/Japan/Global]
APPROVAL_DATE: [Date if known]
PRICE: [Approximate price if known]

Be specific and accurate. If this is an Indian drug, provide India-specific information.
If some information is not available, write "Not Available" for that field.
"""

                        response = st.session_state.orchestrator.llm.invoke(search_prompt)
                        ai_response = response.content

                        # Parse AI response
                        drug_info = {
                            "drug_name": drug_name,
                            "approval_status": "Unknown",
                            "disease_category": "Other",
                            "region": "Global",
                            "manufacturer": "Unknown",
                            "indication": "",
                            "price": "",
                            "approval_date": "",
                            "source_url": "AI Knowledge (Not Verified)"
                        }

                        lines = ai_response.split('\n')
                        for line in lines:
                            line = line.strip()
                            if 'DRUG_NAME:' in line:
                                name = line.split('DRUG_NAME:')[1].strip()
                                if name and name != "Not Available":
                                    drug_info["drug_name"] = name
                            elif 'APPROVAL_STATUS:' in line:
                                status = line.split('APPROVAL_STATUS:')[1].strip()
                                if status and status != "Not Available":
                                    drug_info["approval_status"] = status
                            elif 'MANUFACTURER:' in line:
                                mfr = line.split('MANUFACTURER:')[1].strip()
                                if mfr and mfr != "Not Available":
                                    drug_info["manufacturer"] = mfr
                            elif 'DISEASE_CATEGORY:' in line:
                                cat = line.split('DISEASE_CATEGORY:')[1].strip()
                                if cat and cat != "Not Available":
                                    drug_info["disease_category"] = cat
                            elif 'INDICATION:' in line:
                                ind = line.split('INDICATION:')[1].strip()
                                if ind and ind != "Not Available":
                                    drug_info["indication"] = ind
                            elif 'REGION:' in line:
                                reg = line.split('REGION:')[1].strip()
                                if reg and reg != "Not Available":
                                    drug_info["region"] = reg
                            elif 'APPROVAL_DATE:' in line:
                                date = line.split('APPROVAL_DATE:')[1].strip()
                                if date and date != "Not Available":
                                    drug_info["approval_date"] = date
                            elif 'PRICE:' in line:
                                price = line.split('PRICE:')[1].strip()
                                if price and price != "Not Available":
                                    drug_info["price"] = price

                        with st.expander("📋 View AI Knowledge", expanded=True):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown(f"**Drug Name:** {drug_info['drug_name']}")
                                st.markdown(f"**Approval Status:** {drug_info['approval_status']}")
                                st.markdown(f"**Disease Category:** {drug_info['disease_category']}")
                                st.markdown(f"**Region:** {drug_info['region']}")

                            with col2:
                                st.markdown(f"**Manufacturer:** {drug_info['manufacturer']}")
                                st.markdown(f"**Indication:** {drug_info['indication']}")
                                st.markdown(f"**Price:** {drug_info.get('price', 'N/A')}")
                                st.markdown(f"**Approval Date:** {drug_info.get('approval_date', 'N/A')}")

                            st.warning("⚠️ **Note:** Information based on AI knowledge (may be outdated). For accurate data, try using Web Crawler with specific URLs.")

                except Exception as e:
                    st.error(f"❌ Error during search: {str(e)}")
                    st.exception(e)
                    st.stop()

            # Step 2: AI Agent Analysis
            st.markdown("---")
            if crawl_success:
                st.markdown("### 🤖 Step 2: AI Agent Analysis (Using Fresh Crawled Data)")
            else:
                st.markdown("### 🤖 Step 2: AI Agent Analysis (Using AI Knowledge)")

            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Step 2.1: Validation
                status_text.text("Agent 1/4: Validating data quality...")
                progress_bar.progress(25)
                validation = st.session_state.orchestrator.validator.validate_record(drug_info)

                # Step 2.2: Medical Analysis
                status_text.text("Agent 2/4: Medical insight analysis...")
                progress_bar.progress(50)
                medical_analysis = st.session_state.orchestrator.medical.analyze_drug(drug_info)

                # Step 2.3: Compliance
                status_text.text("Agent 3/4: Compliance assessment...")
                progress_bar.progress(75)
                compliance = st.session_state.orchestrator.compliance.assess_compliance(drug_info)

                # Step 2.4: Executive Summary
                status_text.text("Agent 4/4: Generating executive summary...")
                progress_bar.progress(100)
                executive_summary = st.session_state.orchestrator.executive.generate_summary(
                    drug_info, validation, medical_analysis, compliance
                )

                status_text.text("✅ Analysis complete!")

                # Store results
                result = {
                    "drug_record": drug_info,
                    "validation": validation,
                    "medical_analysis": medical_analysis,
                    "compliance": compliance,
                    "executive_summary": executive_summary,
                    "timestamp": datetime.now().isoformat()
                }

                st.session_state.analysis_results = result
                st.session_state.analysis_history.append(result)

                # Display results
                st.markdown("---")
                st.markdown("### 📊 Analysis Results")

                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    quality_score = validation.get("quality_score", 0)
                    st.metric("Quality Score", f"{quality_score}/100")

                with col2:
                    status = validation.get("validation_status", "UNKNOWN")
                    st.metric("Validation", status)

                with col3:
                    risk = compliance.get("risk_level", "Unknown")
                    color = "🔴" if risk == "High" else "🟡" if risk == "Medium" else "🟢"
                    st.metric("Risk Level", f"{color} {risk}")

                with col4:
                    impact = medical_analysis.get("market_impact", "Unknown")
                    st.metric("Market Impact", impact)

                # Detailed results in tabs
                tab1, tab2, tab3, tab4 = st.tabs(["✅ Validation", "🏥 Medical", "⚖️ Compliance", "📋 Executive"])

                with tab1:
                    st.markdown("### Validation Results")
                    st.markdown(f"**Status:** {validation.get('validation_status', 'Unknown')}")
                    st.markdown(f"**Quality Score:** {validation.get('quality_score', 0)}/100")
                    st.markdown(f"**Confidence:** {validation.get('confidence', 'Unknown')}")

                    if validation.get('issues'):
                        st.markdown("**Issues Found:**")
                        for issue in validation['issues']:
                            st.markdown(f"- {issue}")
                    else:
                        st.success("✅ No issues found")

                with tab2:
                    st.markdown("### Medical Insight Analysis")
                    st.markdown(f"**Therapeutic Category:** {medical_analysis.get('therapeutic_category', 'Unknown')}")
                    st.markdown(f"**Mechanism of Action:** {medical_analysis.get('mechanism_of_action', 'N/A')}")
                    st.markdown(f"**Market Impact:** {medical_analysis.get('market_impact', 'Unknown')}")

                    if medical_analysis.get('competitors'):
                        st.markdown("**Key Competitors:**")
                        for comp in medical_analysis['competitors'][:5]:
                            st.markdown(f"- {comp}")

                    if medical_analysis.get('recommendations'):
                        st.markdown("**Recommendations:**")
                        for rec in medical_analysis['recommendations']:
                            st.markdown(f"- {rec}")

                with tab3:
                    st.markdown("### Compliance Assessment")
                    st.markdown(f"**Regulatory Body:** {compliance.get('regulatory_body', 'Unknown')}")
                    st.markdown(f"**Risk Level:** {compliance.get('risk_level', 'Unknown')}")

                    if compliance.get('safety_concerns'):
                        st.markdown("**Safety Concerns:**")
                        for concern in compliance['safety_concerns']:
                            st.markdown(f"- {concern}")

                    if compliance.get('compliance_requirements'):
                        st.markdown("**Compliance Requirements:**")
                        for req in compliance['compliance_requirements'][:5]:
                            st.markdown(f"- {req}")

                with tab4:
                    st.markdown("### Executive Summary")
                    st.markdown(f"**Headline:** {executive_summary.get('headline', 'N/A')}")

                    if executive_summary.get('key_facts'):
                        st.markdown("**Key Facts:**")
                        for fact in executive_summary['key_facts']:
                            st.markdown(f"- {fact}")

                    if executive_summary.get('recommended_actions'):
                        st.markdown("**Recommended Actions:**")
                        for action in executive_summary['recommended_actions']:
                            st.markdown(f"- {action}")

                # Download option
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    json_data = json.dumps(result, indent=2)
                    st.download_button(
                        "📥 Download Full Report (JSON)",
                        json_data,
                        f"{drug_info['drug_name']}_analysis.json",
                        "application/json",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💊 Pharma Intelligence System | Powered by Multi-Agent AI</p>
    <p>Built with CrewAI, LangChain, Google Gemini</p>
</div>
""", unsafe_allow_html=True)
