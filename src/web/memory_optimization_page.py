"""
Memory Optimization Page
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from observational_memory.memory_optimizer import MemoryOptimizer


def render_memory_optimization_page(i18n, lang):
    """Render memory optimization page"""
    
    st.title("记忆优化" if lang == "zh" else "Memory Optimization")
    
    optimizer = MemoryOptimizer(Path.cwd())
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "压缩" if lang == "zh" else "Compress",
        "主题聚类" if lang == "zh" else "Topic Clustering",
        "高级搜索" if lang == "zh" else "Advanced Search",
        "导出" if lang == "zh" else "Export"
    ])
    
    # Tab 1: Compression
    with tab1:
        st.subheader("观察压缩" if lang == "zh" else "Observation Compression")
        
        observations_dir = Path.cwd() / "memory" / "observations"
        
        if observations_dir.exists():
            session_files = list(observations_dir.glob("*.md"))
            session_ids = [f.stem for f in session_files]
            
            if session_ids:
                selected_session = st.selectbox(
                    "选择会话" if lang == "zh" else "Select Session",
                    session_ids,
                    key="compress_session"
                )
                
                if st.button("压缩" if lang == "zh" else "Compress"):
                    with st.spinner("压缩中..." if lang == "zh" else "Compressing..."):
                        result = optimizer.compress_observations(selected_session)
                        
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success("压缩完成！" if lang == "zh" else "Compression complete!")
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric("原始数量" if lang == "zh" else "Original", result["original_count"])
                            col2.metric("压缩后" if lang == "zh" else "Compressed", result["compressed_count"])
                            col3.metric("移除" if lang == "zh" else "Removed", result["removed"])
                            
                            st.metric("压缩率" if lang == "zh" else "Compression Ratio", f"{result['compression_ratio']:.1%}")
    
    # Tab 2: Topic Clustering
    with tab2:
        st.subheader("主题聚类" if lang == "zh" else "Topic Clustering")
        
        if observations_dir.exists():
            all_observations = []
            for obs_file in observations_dir.glob("*.md"):
                content = obs_file.read_text(encoding="utf-8")
                lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
                all_observations.extend(lines)
            
            if all_observations:
                clusters = optimizer.cluster_by_topic(all_observations)
                
                st.markdown(f"**发现 {len(clusters)} 个主题**" if lang == "zh" else f"**Found {len(clusters)} topics**")
                
                for topic, observations in clusters.items():
                    with st.expander(f"{topic} ({len(observations)} 条)" if lang == "zh" else f"{topic} ({len(observations)} items)"):
                        for obs in observations[:10]:  # Show first 10
                            st.markdown(f"- {obs}")
                        
                        if len(observations) > 10:
                            st.markdown(f"*...还有 {len(observations) - 10} 条*" if lang == "zh" else f"*...and {len(observations) - 10} more*")
    
    # Tab 3: Advanced Search
    with tab3:
        st.subheader("高级搜索" if lang == "zh" else "Advanced Search")
        
        query = st.text_input("搜索关键词" if lang == "zh" else "Search Query")
        
        col1, col2 = st.columns(2)
        with col1:
            use_regex = st.checkbox("使用正则表达式" if lang == "zh" else "Use Regex")
        with col2:
            priority = st.selectbox(
                "优先级过滤" if lang == "zh" else "Priority Filter",
                ["全部", "HIGH", "MEDIUM", "LOW"] if lang == "zh" else ["All", "HIGH", "MEDIUM", "LOW"]
            )
        
        if st.button("搜索" if lang == "zh" else "Search"):
            if query:
                priority_filter = None if priority in ["全部", "All"] else priority
                results = optimizer.advanced_search(query, priority=priority_filter, regex=use_regex)
                
                st.markdown(f"**找到 {len(results)} 条结果**" if lang == "zh" else f"**Found {len(results)} results**")
                
                for result in results[:50]:  # Show first 50
                    st.markdown(f"- **{result['session_id']}**: {result['observation']}")
    
    # Tab 4: Export
    with tab4:
        st.subheader("导出" if lang == "zh" else "Export")
        
        if observations_dir.exists():
            session_files = list(observations_dir.glob("*.md"))
            session_ids = [f.stem for f in session_files]
            
            if session_ids:
                selected_session = st.selectbox(
                    "选择会话" if lang == "zh" else "Select Session",
                    session_ids,
                    key="export_session"
                )
                
                export_format = st.radio(
                    "导出格式" if lang == "zh" else "Export Format",
                    ["Markdown", "知识图谱 (JSON-LD)"] if lang == "zh" else ["Markdown", "Knowledge Graph (JSON-LD)"]
                )
                
                if st.button("导出" if lang == "zh" else "Export"):
                    try:
                        if "Markdown" in export_format:
                            path = optimizer.export_as_markdown(selected_session)
                        else:
                            path = optimizer.export_as_knowledge_graph(selected_session)
                        
                        st.success(f"导出成功: {path.name}" if lang == "zh" else f"Exported: {path.name}")
                        
                        with open(path, "rb") as f:
                            st.download_button(
                                "下载文件" if lang == "zh" else "Download File",
                                f,
                                file_name=path.name
                            )
                    except Exception as e:
                        st.error(f"导出失败: {e}" if lang == "zh" else f"Export failed: {e}")
