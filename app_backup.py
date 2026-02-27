"""
Observational Memory Web UI

Streamlit application for managing and visualizing observational memory.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import pandas as pd
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from observational_memory import ObservationalMemoryManager
from observational_memory_vector import VectorSearchManager

# Page config
st.set_page_config(
    page_title="Observational Memory",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize managers
@st.cache_resource
def init_managers():
    workspace_dir = Path.cwd()
    obs_manager = ObservationalMemoryManager(workspace_dir)
    vector_manager = VectorSearchManager(workspace_dir)
    return obs_manager, vector_manager

obs_manager, vector_manager = init_managers()

# Sidebar
st.sidebar.title("🧠 Observational Memory")
page = st.sidebar.radio("Navigation", ["📊 Dashboard", "📝 Sessions", "🔍 Search", "📈 Analytics", "💾 Data Management"])

# Dashboard Page
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    # Statistics
    observations_dir = Path.cwd() / "memory" / "observations"
    
    if observations_dir.exists():
        session_files = list(observations_dir.glob("*.md"))
        total_sessions = len(session_files)
        
        total_observations = 0
        total_tokens = 0
        for file in session_files:
            content = file.read_text(encoding="utf-8")
            lines = [l for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
            total_observations += len(lines)
            total_tokens += len(content) // 2
        
        vector_stats = vector_manager.get_statistics()
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sessions", total_sessions)
        col2.metric("Total Observations", total_observations)
        col3.metric("Total Tokens", f"{total_tokens:,}")
        col4.metric("Vector Embeddings", vector_stats["total_embeddings"])
        
        # Recent sessions
        st.subheader("Recent Sessions")
        recent_sessions = sorted(session_files, key=lambda f: f.stat().st_mtime, reverse=True)[:10]
        
        session_data = []
        for file in recent_sessions:
            content = file.read_text(encoding="utf-8")
            lines = [l for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
            session_data.append({
                "Session ID": file.stem,
                "Observations": len(lines),
                "Tokens": len(content) // 2,
                "Last Updated": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })
        
        df = pd.DataFrame(session_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No observations found. Start by processing some sessions!")

# Sessions Page
elif page == "📝 Sessions":
    st.title("📝 Sessions")
    
    observations_dir = Path.cwd() / "memory" / "observations"
    
    if observations_dir.exists():
        session_files = sorted(
            observations_dir.glob("*.md"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        # Search filter
        search_query = st.text_input("🔍 Search sessions", "")
        if search_query:
            session_files = [f for f in session_files if search_query.lower() in f.stem.lower()]
        
        # Pagination
        items_per_page = 10
        total_pages = (len(session_files) + items_per_page - 1) // items_per_page
        page_num = st.number_input("Page", min_value=1, max_value=max(1, total_pages), value=1)
        
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_files = session_files[start_idx:end_idx]
        
        # Display sessions
        for file in page_files:
            with st.expander(f"📄 {file.stem}"):
                content = file.read_text(encoding="utf-8")
                st.text(content)
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ Delete", key=f"del_{file.stem}"):
                        file.unlink()
                        vector_manager.delete_session(file.stem)
                        st.success(f"Deleted {file.stem}")
                        st.rerun()
    else:
        st.info("No sessions found.")

# Search Page
elif page == "🔍 Search":
    st.title("🔍 Semantic Search")
    
    query = st.text_input("Enter search query", "")
    
    col1, col2 = st.columns(2)
    with col1:
        top_k = st.slider("Number of results", 1, 20, 5)
    with col2:
        min_similarity = st.slider("Minimum similarity", 0.0, 1.0, 0.3, 0.05)
    
    if st.button("Search") and query:
        with st.spinner("Searching..."):
            results = vector_manager.search(query, top_k=top_k, min_similarity=min_similarity)
            
            if results:
                st.success(f"Found {len(results)} results")
                
                for i, result in enumerate(results, 1):
                    with st.container():
                        st.markdown(f"### Result {i}")
                        st.markdown(f"**Session:** `{result.session_id}`")
                        st.markdown(f"**Similarity:** {result.similarity:.3f}")
                        st.markdown(f"**Observation:**")
                        st.info(result.observation)
                        st.divider()
            else:
                st.warning("No results found. Try adjusting the similarity threshold.")

# Analytics Page
elif page == "📈 Analytics":
    st.title("📈 Analytics")
    
    observations_dir = Path.cwd() / "memory" / "observations"
    
    if observations_dir.exists() and list(observations_dir.glob("*.md")):
        # Priority distribution
        st.subheader("Priority Distribution")
        
        priority_counts = {"🔴 High": 0, "🟡 Medium": 0, "🟢 Low": 0}
        
        for file in observations_dir.glob("*.md"):
            content = file.read_text(encoding="utf-8")
            priority_counts["🔴 High"] += content.count("🔴")
            priority_counts["🟡 Medium"] += content.count("🟡")
            priority_counts["🟢 Low"] += content.count("🟢")
        
        fig = px.pie(
            values=list(priority_counts.values()),
            names=list(priority_counts.keys()),
            title="Observation Priority Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Timeline
        st.subheader("Session Timeline")
        
        session_files = list(observations_dir.glob("*.md"))
        timeline_data = []
        
        for file in session_files:
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            content = file.read_text(encoding="utf-8")
            lines = [l for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
            
            timeline_data.append({
                "Date": mtime.date(),
                "Session": file.stem,
                "Observations": len(lines)
            })
        
        df = pd.DataFrame(timeline_data)
        df = df.groupby("Date")["Observations"].sum().reset_index()
        
        fig = px.line(df, x="Date", y="Observations", title="Observations Over Time")
        st.plotly_chart(fig, use_container_width=True)
        
        # Token usage
        st.subheader("Token Usage by Session")
        
        token_data = []
        for file in sorted(session_files, key=lambda f: f.stat().st_mtime, reverse=True)[:10]:
            content = file.read_text(encoding="utf-8")
            token_data.append({
                "Session": file.stem[:20] + "..." if len(file.stem) > 20 else file.stem,
                "Tokens": len(content) // 2
            })
        
        df = pd.DataFrame(token_data)
        fig = px.bar(df, x="Session", y="Tokens", title="Token Usage (Top 10 Recent Sessions)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for analytics.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Observational Memory v1.0**")
st.sidebar.markdown("Built with Streamlit")
