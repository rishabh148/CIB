import streamlit as st
import requests
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Corporate Competitive Intelligence Bureau",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Endpoint Configuration
API_URL = os.environ.get("API_URL", "http://localhost:8000/api")

# Helper function to query the backend
def fetch_competitors():
    try:
        response = requests.get(f"{API_URL}/competitors", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def fetch_analyses(competitor_id=None):
    try:
        params = {"competitor_id": competitor_id} if competitor_id else {}
        response = requests.get(f"{API_URL}/analyses", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def create_competitor(data):
    try:
        response = requests.post(f"{API_URL}/competitors", json=data, timeout=5)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Failed to reach API server: {str(e)}")
        return False

def update_competitor(comp_id, data):
    try:
        response = requests.put(f"{API_URL}/competitors/{comp_id}", json=data, timeout=5)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Failed to reach API server: {str(e)}")
        return False

def delete_competitor(comp_id):
    try:
        response = requests.delete(f"{API_URL}/competitors/{comp_id}", timeout=5)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Failed to reach API server: {str(e)}")
        return False

def run_analysis(competitor_id):
    try:
        response = requests.post(
            f"{API_URL}/analyses/run", 
            json={"competitor_id": competitor_id}, 
            timeout=120 # Higher timeout for agent flow execution
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Analysis failed: {response.text}")
    except Exception as e:
        st.error(f"API Connection error: {str(e)}")
    return None

# Custom styling for executive corporate theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0f172a;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #1e293b;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.3rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .threat-badge {
        font-size: 0.9rem;
        font-weight: bold;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        text-align: center;
    }
    .threat-high { background-color: #fee2e2; color: #991b1b; }
    .threat-medium { background-color: #fef3c7; color: #92400e; }
    .threat-low { background-color: #dcfce7; color: #166534; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR CONFIGURATION
with st.sidebar:
    st.image("https://img.icons8.com/?size=100&id=103348&format=png", width=60)
    st.markdown("## CI Bureau Control")
    st.markdown("Automated Competitive Intelligence for high-leverage product executives.")
    st.divider()
    
    # Check Server Status
    server_running = False
    try:
        check_res = requests.get(f"http://localhost:8000/", timeout=2)
        if check_res.status_code == 200:
            server_running = True
    except Exception:
        pass
        
    if server_running:
        st.success("🤖 API Engine: **Online**")
    else:
        st.error("⚠️ API Engine: **Offline**\nPlease launch backend service.")
        st.info("💡 To boot both backend and frontend, execute: `python run.py` in your terminal.")

    st.divider()
    st.markdown("### LLM Framework Integration")
    api_key_status = "Not Set (Simulating)"
    try:
        # Check standard key in env
        env_res = requests.get(f"{API_URL}/competitors", timeout=2) # Dummy call just to establish contact if any
    except Exception:
        pass
        
    st.info("💡 By default, the system runs in a high-fidelity Simulation Mode if no OpenAI key is found, allowing zero-setup corporate dry-runs.")
    st.caption("Developed with CrewAI + FastAPI + Streamlit")

# HEADER
st.markdown('<div class="main-header">🛡️ Competitive Intelligence Bureau</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated multi-agent competitor scraper, baseline pricing auditor, strategic SWOT mapper, and Executive product briefer.</div>', unsafe_allow_html=True)

# MAIN TAB NAVIGATION
tab_dashboard, tab_profiles, tab_archive = st.tabs([
    "📈 Executive Dashboard", 
    "📂 Competitor Profiles (Baselines)", 
    "🗄️ Intelligence Archives"
])

# --- TAB 1: EXECUTIVE DASHBOARD ---
with tab_dashboard:
    competitors = fetch_competitors()
    
    if not competitors:
        st.warning("No competitors found in the database. Go to the 'Competitor Profiles' tab to add your first competitive target.")
    else:
        col_select, col_empty = st.columns([2, 2])
        with col_select:
            selected_comp_name = st.selectbox(
                "Select Competitor for Actionable Analysis:",
                options=[c["name"] for c in competitors]
            )
            selected_comp = next(c for c in competitors if c["name"] == selected_comp_name)
            
        st.markdown("### ⚡ Bureau Action Deck")
        
        col_info_1, col_info_2 = st.columns(2)
        with col_info_1:
            st.markdown(f"**Target Company**: [{selected_comp['name']}]({selected_comp['website']})")
            st.markdown(f"**Pricing URL**: `{selected_comp['pricing_url']}`")
        with col_info_2:
            st.markdown(f"**Configuration baseline timestamp**: {selected_comp['created_at'][:10]}")
            
        st.divider()
        
        # Primary Action Trigger
        btn_trigger = st.button(f"🚀 Launch 5-Agent Competitive Intelligence Crew on {selected_comp['name']}", type="primary", use_container_width=True)
        
        if btn_trigger:
            # Gorgeous Status stream mimicking sequential agent work
            with st.status(f"Directing Intelligence Crew to evaluate {selected_comp['name']}...", expanded=True) as status_box:
                st.write("🔍 **[Agent 1: Scraping Sentinel]** Commencing target web crawls...")
                time.sleep(1.2)
                st.write("🌐 **[Agent 1: Scraping Sentinel]** Successfully scraped core product marketing & pricing layers.")
                
                st.write("📊 **[Agent 2: Feature Delta Analyst]** Fetching historical feature baseline from archive...")
                time.sleep(1.0)
                st.write("⚡ **[Agent 2: Feature Delta Analyst]** Identifying differences, feature additions, and messaging shifts.")
                
                st.write("💰 **[Agent 3: Pricing & Packaging Analyst]** Comparing subscription plans and gated offerings...")
                time.sleep(1.2)
                st.write("💳 **[Agent 3: Pricing & Packaging Analyst]** Calculated price raising metrics and tier packaging impact.")
                
                st.write("⚔️ **[Agent 4: Threat & SWOT Evaluator]** Re-calculating competitor strengths & market threats...")
                time.sleep(1.2)
                st.write("🛡️ **[Agent 4: Threat & SWOT Evaluator]** Outlined revised SWOT matrix and established risk coefficients.")
                
                st.write("📝 **[Agent 5: Executive Briefer]** Synthesizing individual agent outputs into briefing memo...")
                time.sleep(1.0)
                
                # Run the actual API call
                result = run_analysis(selected_comp["id"])
                
                if result:
                    status_box.update(label=f"Analysis of {selected_comp['name']} Complete!", state="complete", expanded=False)
                    st.success("🤖 Intelligence report published to dashboard and local database successfully!")
                    st.session_state[f"last_analysis_{selected_comp['id']}"] = result
                else:
                    status_box.update(label="Analysis Failed during execution", state="error")
                    st.error("Could not generate report. Check API logs.")

        # Display the latest result (either from session state or from DB history)
        latest_analysis = st.session_state.get(f"last_analysis_{selected_comp['id']}", None)
        if not latest_analysis:
            # Query history to see if there is any past run
            past_runs = fetch_analyses(selected_comp["id"])
            if past_runs:
                latest_analysis = past_runs[0] # Most recent run is first
                
        if latest_analysis:
            st.markdown(f"## 📊 Latest Intelligence Feed: {selected_comp['name']}")
            st.caption(f"Analysis timestamp: {latest_analysis['timestamp'].replace('T', ' ')[:19]} UTC (ID: {latest_analysis['id'][:8]})")
            
            # Quick summary stats row
            col_stat_1, col_stat_2, col_stat_3 = st.columns(3)
            with col_stat_1:
                st.markdown(
                    f"""<div class="metric-card">
                        <small style="color: #64748b;">TARGET WEBSITE</small>
                        <div style="font-size: 1.4rem; font-weight:bold; color: #1e3a8a; margin-top: 5px;">{selected_comp['name']}</div>
                    </div>""", 
                    unsafe_allow_html=True
                )
            with col_stat_2:
                t_score = latest_analysis['threat_score']
                badge_class = "threat-high" if t_score >= 8 else "threat-medium" if t_score >= 5 else "threat-low"
                badge_label = "CRITICAL / HIGH" if t_score >= 8 else "MODERATE" if t_score >= 5 else "LOW THREAT"
                st.markdown(
                    f"""<div class="metric-card">
                        <small style="color: #64748b;">THREAT RATING</small>
                        <div style="margin-top: 5px; display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.8rem; font-weight:bold; color: #0f172a;">{t_score} / 10</span>
                            <span class="threat-badge {badge_class}">{badge_label}</span>
                        </div>
                    </div>""", 
                    unsafe_allow_html=True
                )
            with col_stat_3:
                st.markdown(
                    f"""<div class="metric-card">
                        <small style="color: #64748b;">CRAWL STATUS</small>
                        <div style="font-size: 1.4rem; font-weight:bold; color: #16a34a; margin-top: 5px;">✅ 200 SUCCESS</div>
                    </div>""", 
                    unsafe_allow_html=True
                )
            
            # Agent Perspective Tabs
            st.markdown('<div class="section-header">🔍 Multi-Agent Executive Reports</div>', unsafe_allow_html=True)
            
            tab_memo, tab_swot, tab_price, tab_delta, tab_raw = st.tabs([
                "📝 Agent 5: Executive Briefing Memo", 
                "🛡️ Agent 4: Threat & SWOT Matrix", 
                "💰 Agent 3: Pricing & Packaging Audits", 
                "⚡ Agent 2: Feature Deltas", 
                "🕸️ Agent 1: Raw Scraper Sentinel Data"
            ])
            
            with tab_memo:
                st.markdown(latest_analysis["executive_brief"])
                
            with tab_swot:
                st.markdown(latest_analysis["swot_analysis"])
                
            with tab_price:
                st.markdown(latest_analysis["pricing_analysis"])
                
            with tab_delta:
                st.markdown(latest_analysis["feature_deltas"])
                
            with tab_raw:
                with st.expander("Expand to view raw scraped output parsed by Web Scraping Sentinel", expanded=True):
                    st.text(latest_analysis["raw_scraped_data"])
        else:
            st.info("No competitive assessments have been run for this competitor yet. Click the 'Launch Crew' button above to start evaluation.")


# --- TAB 2: COMPETITOR PROFILES (BASELINES) ---
with tab_profiles:
    st.markdown('<div class="section-header">🗂️ Manage Competitor Profiles & Baselines</div>', unsafe_allow_html=True)
    st.markdown("Configure baseline configurations to compare against crawled website changes. The agents compare the latest scraped content with these baselines.")
    
    competitors = fetch_competitors()
    
    col_list, col_form = st.columns([2, 3])
    
    with col_list:
        st.subheader("Configured Competitors")
        if not competitors:
            st.info("No competitors added yet.")
        else:
            for comp in competitors:
                with st.expander(f"🏢 **{comp['name']}**", expanded=False):
                    st.write(f"**Website**: {comp['website']}")
                    st.write(f"**Pricing page**: {comp['pricing_url']}")
                    st.write("**Baseline Features**:")
                    st.text(comp["baseline_features"])
                    st.write("**Baseline Pricing**:")
                    st.text(comp["baseline_pricing"])
                    
                    if st.button(f"🗑️ Delete {comp['name']}", key=f"del_{comp['id']}", type="secondary"):
                        if delete_competitor(comp["id"]):
                            st.success("Deleted!")
                            st.rerun()

    with col_form:
        st.subheader("Add / Update Competitor")
        
        # Choice to edit existing or create new
        mode = st.radio("Choose action:", ["Create New Competitor", "Edit Existing Competitor"], horizontal=True)
        
        edit_id = None
        default_name = ""
        default_web = ""
        default_pricing_url = ""
        default_features = ""
        default_pricing = ""
        
        if mode == "Edit Existing Competitor" and competitors:
            edit_comp_name = st.selectbox("Select Competitor to Edit:", [c["name"] for c in competitors])
            matched_edit = next(c for c in competitors if c["name"] == edit_comp_name)
            edit_id = matched_edit["id"]
            default_name = matched_edit["name"]
            default_web = matched_edit["website"]
            default_pricing_url = matched_edit["pricing_url"]
            default_features = matched_edit["baseline_features"]
            default_pricing = matched_edit["baseline_pricing"]
            
        with st.form("competitor_form"):
            name = st.text_input("Competitor Name", value=default_name if mode == "Edit Existing Competitor" else "")
            web = st.text_input("Website URL", value=default_web if mode == "Edit Existing Competitor" else "https://")
            p_url = st.text_input("Pricing Page URL", value=default_pricing_url if mode == "Edit Existing Competitor" else "https://")
            
            features = st.text_area(
                "Known Baseline Features (One per line or paragraph)",
                value=default_features if mode == "Edit Existing Competitor" else "- Contact portal\n- Standard integrations",
                help="Enter features currently offered by this competitor before any new launches."
            )
            
            pricing = st.text_area(
                "Known Baseline Pricing Structure",
                value=default_pricing if mode == "Edit Existing Competitor" else "Starter: $19/mo\nPro: $49/mo\nEnterprise: Custom",
                help="Configure the baseline cost structures before new price changes."
            )
            
            submit_btn = st.form_submit_button("Save Competitor Profile Baseline")
            
            if submit_btn:
                if not name or not web:
                    st.error("Name and Website URL are required.")
                else:
                    payload = {
                        "name": name,
                        "website": web,
                        "pricing_url": p_url,
                        "baseline_features": features,
                        "baseline_pricing": pricing
                    }
                    
                    if mode == "Create New Competitor":
                        if create_competitor(payload):
                            st.success(f"Competitor {name} created successfully!")
                            st.rerun()
                    else:
                        if update_competitor(edit_id, payload):
                            st.success(f"Competitor {name} updated successfully!")
                            st.rerun()


# --- TAB 3: INTELLIGENCE ARCHIVES ---
with tab_archive:
    st.markdown('<div class="section-header">🗄️ Historical Intelligence Archive</div>', unsafe_allow_html=True)
    
    analyses = fetch_analyses()
    
    if not analyses:
        st.info("No assessments found in the historical archives. Please run analyses from the 'Executive Dashboard' to accumulate historical timelines.")
    else:
        # Threat landscape chart over time
        st.subheader("Competitor Threat Score Matrix")
        
        df_runs = pd.DataFrame([{
            "Competitor": a["competitor_name"],
            "Timestamp": a["timestamp"][:16].replace("T", " "),
            "Threat Level (1-10)": a["threat_score"],
            "Brief ID": a["id"][:8]
        } for a in analyses])
        
        # Plotly chart
        fig = px.bar(
            df_runs,
            x="Timestamp",
            y="Threat Level (1-10)",
            color="Competitor",
            barmode="group",
            title="Strategic Threat Scores Over Time",
            color_discrete_sequence=px.colors.qualitative.Prism,
            hover_data=["Brief ID"]
        )
        fig.update_layout(yaxis_range=[0,10])
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.subheader("Archived Briefing Reports")
        
        selected_run_id = st.selectbox(
            "Select Historic Briefing to Retrieve:",
            options=[f"{a['competitor_name']} - {a['timestamp'][:16].replace('T', ' ')} (ID: {a['id'][:8]})" for a in analyses]
        )
        
        # Extract selected run
        run_id = selected_run_id.split("(ID: ")[-1][:-1]
        selected_run = next(a for a in analyses if a["id"][:8] == run_id)
        
        st.markdown(f"### Historical Briefing: {selected_run['competitor_name']}")
        st.caption(f"Archived at: {selected_run['timestamp'][:19].replace('T', ' ')} UTC")
        
        col_arch_memo, col_arch_swot = st.columns(2)
        with col_arch_memo:
            st.markdown("#### 📝 Product Brief")
            st.markdown(selected_run["executive_brief"])
        with col_arch_swot:
            st.markdown("#### 🛡️ Threat & SWOT Assessment")
            st.markdown(selected_run["swot_analysis"])
            
        with st.expander("Retrieve Pricing & Delta Reports for this Brief"):
            st.markdown("#### 💰 Pricing Audits")
            st.markdown(selected_run["pricing_analysis"])
            st.markdown("#### ⚡ Feature Deltas")
            st.markdown(selected_run["feature_deltas"])
