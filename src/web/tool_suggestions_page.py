"""
Tool Suggestions Page
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from observational_memory.tool_suggestion import ToolSuggestionEngine


def render_tool_suggestions_page(i18n, lang, obs_manager):
    """Render tool suggestions page"""
    
    st.title("工具建议" if lang == "zh" else "Tool Suggestions")
    
    engine = ToolSuggestionEngine()
    
    # Get all observations
    observations_dir = Path.cwd() / "memory" / "observations"
    
    if not observations_dir.exists():
        st.info("暂无观察数据" if lang == "zh" else "No observations yet")
        return
    
    all_observations = []
    for obs_file in observations_dir.glob("*.md"):
        content = obs_file.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
        all_observations.extend(lines)
    
    if not all_observations:
        st.info("暂无观察数据" if lang == "zh" else "No observations yet")
        return
    
    # Statistics
    st.subheader("工具使用统计" if lang == "zh" else "Tool Usage Statistics")
    
    stats = engine.get_tool_statistics(all_observations)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("总建议数" if lang == "zh" else "Total Suggestions", stats["total_suggestions"])
    col2.metric("平均置信度" if lang == "zh" else "Avg Confidence", f"{stats['avg_confidence']:.2f}")
    col3.metric("工具类型" if lang == "zh" else "Tool Types", len(stats["by_tool"]))
    
    # Tool distribution
    if stats["by_tool"]:
        st.markdown("### 工具分布" if lang == "zh" else "### Tool Distribution")
        
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(stats["by_tool"].keys()),
                y=list(stats["by_tool"].values()),
                marker_color="lightblue"
            )
        ])
        
        fig.update_layout(
            xaxis_title="工具" if lang == "zh" else "Tool",
            yaxis_title="建议次数" if lang == "zh" else "Suggestion Count",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recent suggestions
    st.subheader("最近建议" if lang == "zh" else "Recent Suggestions")
    
    recent_obs = all_observations[-20:]  # Last 20
    
    for i, obs in enumerate(reversed(recent_obs), 1):
        suggestions = engine.analyze_observation(obs)
        
        if suggestions:
            with st.expander(f"观察 {i}: {obs[:50]}..." if lang == "zh" else f"Observation {i}: {obs[:50]}..."):
                st.markdown(f"**完整内容**: {obs}" if lang == "zh" else f"**Full Content**: {obs}")
                
                st.markdown("**建议工具**:" if lang == "zh" else "**Suggested Tools**:")
                
                for suggestion in suggestions:
                    st.markdown(f"- **{suggestion.tool}** ({suggestion.confidence:.0%}): {suggestion.reason}")
                    if suggestion.context:
                        st.markdown(f"  *上下文*: {suggestion.context}" if lang == "zh" else f"  *Context*: {suggestion.context}")
