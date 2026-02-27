"""
Optimized Observational Memory Web UI

Features:
- Bilingual support (English / Chinese)
- Icon-based navigation (no emoji)
- Smooth animations and transitions
- Modern UI design
"""

import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import pandas as pd
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))

from observational_memory.core import ObservationalMemoryManager
from observational_memory.vector import VectorSearchManager
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from i18n import I18n

# Page config
st.set_page_config(
    page_title="Observational Memory",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for animations and styling
st.markdown("""
<style>
    /* Smooth transitions */
    .stButton button {
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Card animations */
    .element-container {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Loading animation */
    .stSpinner > div {
        border-color: #1f77b4 transparent transparent transparent;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
</style>
""", unsafe_allow_html=True)

# Initialize managers
@st.cache_resource
def init_managers():
    workspace_dir = Path.cwd()
    obs_manager = ObservationalMemoryManager(workspace_dir)
    vector_manager = VectorSearchManager(workspace_dir)
    i18n = I18n(workspace_dir / "locales")
    return obs_manager, vector_manager, i18n

obs_manager, vector_manager, i18n = init_managers()

# Language selector in sidebar
with st.sidebar:
    st.markdown("### Language / 语言")
    lang = st.selectbox(
        i18n.t("language.select"),
        options=["zh", "en"],
        format_func=lambda x: "简体中文" if x == "zh" else "English",
        key="language"
    )
    i18n.set_locale(lang)
    
    st.markdown("---")
    
    # Navigation with icons
    from settings_page import render_settings_page
from tool_suggestions_page import render_tool_suggestions_page
from memory_optimization_page import render_memory_optimization_page

selected = option_menu(
        menu_title=i18n.t("app.title"),
        options=[
            i18n.t("dashboard.title"),
            i18n.t("sessions.title"),
            i18n.t("search.title"),
            i18n.t("analytics.title")
        ],
        icons=["speedometer2", "folder", "search", "bar-chart"],
        menu_icon="brain",
        default_index=0,
    )

# Dashboard Page
if selected == i18n.t("dashboard.title"):
    st.title(i18n.t("dashboard.title"))
    
    with st.spinner(i18n.t("dashboard.loading") if "dashboard.loading" in i18n.translations[lang] else i18n.t("common.loading")):
        observations_dir = Path.cwd() / "memory" / i18n.t("table.observations")
        
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
            
            # Animated metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(i18n.t("dashboard.total_sessions"), total_sessions)
            col2.metric(i18n.t("dashboard.total_observations"), total_observations)
            col3.metric(i18n.t("dashboard.total_tokens"), f"{total_tokens:,}")
            col4.metric(i18n.t("dashboard.vector_embeddings"), vector_stats["total_embeddings"])
            
            st.markdown("---")
            
            # Recent sessions
            st.subheader(i18n.t("dashboard.recent_sessions") if "dashboard.recent_sessions" in i18n.translations[lang] else "Recent Sessions")
            recent_sessions = sorted(session_files, key=lambda f: f.stat().st_mtime, reverse=True)[:10]
            
            session_data = []
            for file in recent_sessions:
                content = file.read_text(encoding="utf-8")
                lines = [l for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
                session_data.append({
                    i18n.t("table.session_id"): file.stem,
                    i18n.t("table.observations"): len(lines),
                    i18n.t("table.tokens"): len(content) // 2,
                    i18n.t("table.last_updated"): datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                })
            
            df = pd.DataFrame(session_data)
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.info(i18n.t("dashboard.no_data") if "dashboard.no_data" in i18n.translations[lang] else "No observations found.")

# Sessions Page
elif selected == i18n.t("sessions.title"):
    st.title(i18n.t("sessions.title"))
    
    observations_dir = Path.cwd() / "memory" / i18n.t("table.observations")
    
    if observations_dir.exists():
        session_files = sorted(
            observations_dir.glob("*.md"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        # Search filter
        search_query = st.text_input(i18n.t("sessions.search"), "", key="session_search")
        if search_query:
            session_files = [f for f in session_files if search_query.lower() in f.stem.lower()]
        
        # Pagination
        items_per_page = 10
        total_pages = (len(session_files) + items_per_page - 1) // items_per_page
        page_num = st.number_input(i18n.t("sessions.page"), min_value=1, max_value=max(1, total_pages), value=1)
        
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_files = session_files[start_idx:end_idx]
        
        # Display sessions with animation
        for file in page_files:
            with st.expander(f"{i18n.t('sessions.session_prefix')} {file.stem}"):
                content = file.read_text(encoding="utf-8")
                st.text(content)
                
                if st.button(i18n.t("sessions.delete"), key=f"del_{file.stem}"):
                    file.unlink()
                    vector_manager.delete_session(file.stem)
                    st.success(f"{i18n.t('sessions.deleted')} {file.stem}")
                    st.rerun()
    else:
        st.info(i18n.t("sessions.no_data") if "sessions.no_data" in i18n.translations[lang] else "No sessions found.")

# Search Page
elif selected == i18n.t("search.title"):
    st.title(i18n.t("search.title"))
    
    query = st.text_input(i18n.t("search.query"), "")
    
    col1, col2 = st.columns(2)
    with col1:
        top_k = st.slider(i18n.t("search.results"), 1, 20, 5)
    with col2:
        min_similarity = st.slider(i18n.t("search.similarity"), 0.0, 1.0, 0.3, 0.05)
    
    if st.button(i18n.t("search.button")) and query:
        with st.spinner(i18n.t("search.searching")):
            results = vector_manager.search(query, top_k=top_k, min_similarity=min_similarity)
            
            if results:
                st.success(i18n.t("search.found").format(count=len(results)))
                
                for i, result in enumerate(results, 1):
                    with st.container():
                        st.markdown(f"### Result {i}")
                        st.markdown(f"**Session:** `{result.session_id}`")
                        st.markdown(f"**Similarity:** {result.similarity:.3f}")
                        st.info(result.observation)
                        st.divider()
            else:
                st.warning(i18n.t("search.no_results"))

# Analytics Page
elif selected == i18n.t("analytics.title"):
    st.title(i18n.t("analytics.title"))
    
    observations_dir = Path.cwd() / "memory" / i18n.t("table.observations")
    
    if observations_dir.exists() and list(observations_dir.glob("*.md")):
        # Priority distribution
        st.subheader(i18n.t("analytics.priority_distribution"))
        
        priority_counts = {
            i18n.t("priority.high"): 0,
            i18n.t("priority.medium"): 0,
            i18n.t("priority.low"): 0
        }
        
        for file in observations_dir.glob("*.md"):
            content = file.read_text(encoding="utf-8")
            priority_counts[i18n.t("priority.high")] += content.count("🔴")
            priority_counts[i18n.t("priority.medium")] += content.count("🟡")
            priority_counts[i18n.t("priority.low")] += content.count("🟢")
        
        fig = px.pie(
            values=list(priority_counts.values()),
            names=list(priority_counts.keys()),
            title=i18n.t("analytics.priority_distribution")
        )
        st.plotly_chart(fig, width="stretch")
        
        # Timeline
        st.subheader(i18n.t("analytics.timeline"))
        
        session_files = list(observations_dir.glob("*.md"))
        timeline_data = []
        
        for file in session_files:
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            content = file.read_text(encoding="utf-8")
            lines = [l for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
            
            timeline_data.append({
                "Date": mtime.date(),
                i18n.t("table.observations"): len(lines)
            })
        
        df = pd.DataFrame(timeline_data)
        df = df.groupby("Date")[i18n.t("table.observations")].sum().reset_index()
        
        fig = px.line(df, x="Date", y=i18n.t("table.observations"), title=i18n.t("analytics.timeline"))
        st.plotly_chart(fig, width="stretch")
        
        # Token usage
        st.subheader(i18n.t("analytics.token_usage"))
        
        token_data = []
        for file in sorted(session_files, key=lambda f: f.stat().st_mtime, reverse=True)[:10]:
            content = file.read_text(encoding="utf-8")
            token_data.append({
                "Session": file.stem[:20] + "..." if len(file.stem) > 20 else file.stem,
                i18n.t("table.tokens"): len(content) // 2
            })
        
        df = pd.DataFrame(token_data)
        fig = px.bar(df, x="Session", y=i18n.t("table.tokens"), title=i18n.t("analytics.token_usage"))
        st.plotly_chart(fig, width="stretch")
    else:
        st.info(i18n.t("analytics.no_data"))

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Observational Memory v2.0**")
st.sidebar.markdown("Built with Streamlit")


