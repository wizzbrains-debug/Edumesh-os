import streamlit as st
import sys
import os
import json
import pandas as pd

# Add project root to path so we can import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.gemini_client import EduMeshGemini
from backend.graph.neo4j_client import Neo4jClient
from backend.gap_detector import GapDetector
# from backend.offline_gap_detector import OfflineGapDetector
from backend.offline_gap_detector import detect_skill_gaps
from backend.lead_selector import LeadSelector
from data.mock_data_generator import generate_mock_data

def split_nodes_by_type(nodes):
    """
    Convert raw graph nodes into structured DataFrames
    for clean UI rendering.
    """
    people = []
    skills = []

    for node_id, data in nodes:
        label = data.get("labels")

        if label == "Person":
            people.append({
                "ID": data.get("id"),
                "Name": data.get("name"),
                "Age": data.get("age")
            })

        elif label == "Skill":
            skills.append({
                "Skill Name": data.get("name")
            })

    return pd.DataFrame(people), pd.DataFrame(skills)

def section_divider(title: str):
    st.markdown(f"### {title}")
    st.markdown("---")

def render_community_tables(nodes):
    """
    Render People and Skills tables in a judge-friendly format.
    """
    people_df, skills_df = split_nodes_by_type(nodes)

    st.subheader("👥 Community Members")
    if not people_df.empty:
        st.dataframe(people_df.reset_index(drop=True), use_container_width=True)
        st.caption("People currently mapped in the community graph.")
    else:
        st.info("No community members found.")

    st.subheader("🛠️ Community Skills")
    if not skills_df.empty:
        st.dataframe(skills_df.reset_index(drop=True), use_container_width=True)
        st.caption("Skills available within the community.")
    else:
        st.info("No skills found.")

def extract_relationships(mock_graph):
    """
    Convert mock graph edges into a table.
    """
    rows = []

    for source, target, data in mock_graph.edges(data=True):
        rows.append({
            "From": source,
            "Relationship": data.get("type"),
            "To": target
        })

    return pd.DataFrame(rows)

def render_relationships_table(db):
    """
    Render relationships if running in mock mode.
    """
    if not db.use_mock:
        st.info("Relationship view available in mock mode only.")
        return

    rel_df = extract_relationships(db.mock_graph)

    st.subheader("🔗 Who Can Do What")
    if not rel_df.empty:
        st.dataframe(rel_df.reset_index(drop=True), use_container_width=True)
        st.caption("Relationships linking people to their skills.")
    else:
        st.info("No relationships found.")

# Page Config
st.set_page_config(page_title="EduMesh OS", layout="wide")

st.title("EduMesh OS (Gemini 3 Pro + Neo4j)")
st.markdown("**Autonomous Community Intelligence System**")

# Initialize Backend
@st.cache_resource
def get_backend():
    gemini = EduMeshGemini()
    db = Neo4jClient()

    # Auto-seed mock graph once per session
    if db.use_mock and "mock_seeded" not in st.session_state:
        generate_mock_data(db)
        st.session_state["mock_seeded"] = True

    return gemini, db

try:
    gemini_client, neo4j_client = get_backend()
    st.sidebar.success("System Online: Gemini + Neo4j (or Mock)")
except Exception as e:
    st.error(f"System Offline: {e}")
    st.stop()

# --- DEMO SAFETY TOGGLE ---
use_ai = st.sidebar.checkbox("Use Gemini AI", value=False)
if use_ai:
    st.sidebar.warning("⚡ AI Enabled: Quota will be consumed.")
else:
    st.sidebar.info("🛡️ AI Disabled (Safe Mode)")
# --------------------------

# Tabs
tab1, tab2, tab3 = st.tabs(["Community Graph", "Skill Gaps (Arbitrage)", "Lead Selection"])

with tab1:
    st.header("Live Community Graph")
    if st.button("Refresh Graph Data"):
        # Here we would typically re-query Neo4j
        pass
    
    # Simple Visualizer for Demo (Mocking the visual aspect if GraphView is complex)
    # real implementation would pull from neo4j_client.get_all_nodes()
    # For hackathon demo, let's show stats or raw data if visualizer acts up
    nodes = neo4j_client.get_all_nodes()
    st.metric("Total Nodes", len(nodes))
    if neo4j_client.use_mock:
        st.info("Running in Mock Graph/Memory Mode")
        
    section_divider("Community Overview")
    
    # Calculate stats for summary
    people_df, skills_df = split_nodes_by_type(nodes)
    rel_count = 0
    if neo4j_client.use_mock:
        rel_df = extract_relationships(neo4j_client.mock_graph)
        rel_count = len(rel_df)
        
    st.success(
        f"{len(people_df)} members • {len(skills_df)} skills • {rel_count} relationships"
    )
    
    render_community_tables(nodes)
    render_relationships_table(neo4j_client)

with tab2:
    st.header("Strategic Gap Analysis (Gemini + Thinking)")
    
    # Load mock data for Gemini context
    mock_data = [] 
    if os.path.exists("data/mock_community.json"):
        with open("data/mock_community.json", "r") as f:
            mock_data = json.load(f)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Offline Detector (Deterministic)")
        
        # Re-fetch nodes for this tab
        nodes = neo4j_client.get_all_nodes()
        offline_gaps = detect_skill_gaps(nodes)

        st.subheader("📉 Detected Skill Gaps (Offline Intelligence)")

        if offline_gaps:
            df = pd.DataFrame(offline_gaps)
            st.dataframe(df.reset_index(drop=True), use_container_width=True)
            st.caption("Detected gaps are derived from community skill topology.")
        else:
            st.info("No critical skill gaps detected.")
        
    with col2:
        st.subheader("Gemini 3 Pro Agent")
        if st.button("Run AI Gap Analysis"):
            if not use_ai:
                st.warning("⚠️ AI disabled. Toggle 'Use Gemini AI' in sidebar to run this agent.")
            else:
                gap_detector_agent = GapDetector(gemini_client)
                # Create a string representation of the graph for the AI
                graph_summary = json.dumps(mock_data) 
                with st.spinner("Gemini is thinking (High Reasoning)..."):
                    try:
                        ai_gaps = gap_detector_agent.detect_gaps(graph_summary)
                        
                        # Ensure list format
                        if isinstance(ai_gaps, dict):
                            ai_gaps = [ai_gaps]
                            
                        # Convert to DataFrame for strategic view
                        ai_df = pd.DataFrame(ai_gaps)
                        
                        st.subheader("🧠 AI-Identified Strategic Opportunities")
                        
                        # Check if columns exist before filtering to avoid errors if AI hallucinates schema
                        cols_to_show = ["title", "severity", "suggested_intervention"]
                        existing_cols = [c for c in cols_to_show if c in ai_df.columns]
                        
                        if existing_cols:
                            st.dataframe(
                                ai_df[existing_cols],
                                use_container_width=True
                            )
                        else:
                            st.dataframe(ai_df, use_container_width=True)

                        with st.expander("🔍 View Raw Gemini Reasoning (JSON)"):
                            st.json(ai_gaps)

                    except Exception as e:
                        st.warning(
                            "Gemini reasoning is optional. The system is currently operating in offline intelligence mode."
                        )
                        st.error(f"AI Error: {e}")
                
                # Reframed Thought Signature
                if gemini_client.thought_signature:
                    st.success("🧠 Reasoning continuity active")
                    st.caption(
                        "Persistent thought signature maintained across Gemini calls."
                    )

                with st.expander("View Thought Signature (Debug)"):
                    st.json(gemini_client.thought_signature)

with tab3:
    st.header("Lead Selector Agent")
    if st.button("Identify Leaders"):
        if not use_ai:
            st.warning("⚠️ AI disabled. Toggle 'Use Gemini AI' in sidebar to run this agent.")
        else:
            selector = LeadSelector(gemini_client)
            with st.spinner("Analyzing candidates..."):
                mock_candidates = []
                if os.path.exists("data/mock_community.json"):
                    with open("data/mock_community.json", "r") as f:
                        mock_candidates = json.load(f)
                
                try:
                    leads = selector.select_leads(mock_candidates)
                    for lead in leads:
                        st.success(f"Selected: {lead.get('name')}")
                        st.caption(lead.get('reason'))
                except Exception as e:
                    st.error(f"AI Error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")
st.sidebar.markdown(f"**Gemini Model:** {gemini_client.model}")
st.sidebar.markdown(f"**Graph Mode:** {'MOCK' if neo4j_client.use_mock else 'NEO4J'}")
