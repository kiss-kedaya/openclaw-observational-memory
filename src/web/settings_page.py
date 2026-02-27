"""
Settings and Management Page for Web UI
"""

import streamlit as st
from pathlib import Path
import json
import subprocess
import sys
import shutil
from datetime import datetime

def render_settings_page(i18n, lang, obs_manager, vector_manager, data_manager):
    """Render settings and management page"""
    
    st.title("设置与管理" if lang == "zh" else "Settings & Management")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "OpenClaw 集成" if lang == "zh" else "OpenClaw Integration",
        "数据管理" if lang == "zh" else "Data Management",
        "系统状态" if lang == "zh" else "System Status",
        "配置" if lang == "zh" else "Configuration"
    ])
    
    # Tab 1: OpenClaw Integration
    with tab1:
        st.subheader("OpenClaw 集成管理" if lang == "zh" else "OpenClaw Integration Management")
        
        # Check installation status
        openclaw_dir = Path.home() / ".openclaw"
        hook_file = openclaw_dir / "hooks" / "observational_memory_hook.py"
        config_file = openclaw_dir / "hooks" / "observational_memory_config.json"
        
        if hook_file.exists():
            st.success("✅ 已安装" if lang == "zh" else "✅ Installed")
            
            # Show config
            if config_file.exists():
                config = json.loads(config_file.read_text())
                
                st.markdown("**当前配置**" if lang == "zh" else "**Current Configuration**")
                
                col1, col2 = st.columns(2)
                with col1:
                    min_messages = st.number_input(
                        "最小消息数" if lang == "zh" else "Min Messages",
                        value=config.get("min_messages", 10),
                        min_value=1,
                        max_value=100
                    )
                    auto_backup = st.checkbox(
                        "自动备份" if lang == "zh" else "Auto Backup",
                        value=config.get("auto_backup", False)
                    )
                
                with col2:
                    backup_interval = st.number_input(
                        "备份间隔（小时）" if lang == "zh" else "Backup Interval (hours)",
                        value=config.get("backup_interval_hours", 24),
                        min_value=1,
                        max_value=168
                    )
                    enabled = st.checkbox(
                        "启用" if lang == "zh" else "Enabled",
                        value=config.get("enabled", True)
                    )
                
                if st.button("保存配置" if lang == "zh" else "Save Configuration"):
                    config["min_messages"] = min_messages
                    config["auto_backup"] = auto_backup
                    config["backup_interval_hours"] = backup_interval
                    config["enabled"] = enabled
                    
                    try:
                        config_file.write_text(json.dumps(config, indent=2))
                        st.success("配置已保存" if lang == "zh" else "Configuration saved")
                    except Exception as e:
                        st.error(f"保存失败: {e}" if lang == "zh" else f"Save failed: {e}")
            
            # Uninstall button
            if st.button("卸载" if lang == "zh" else "Uninstall", type="secondary"):
                try:
                    hook_file.unlink()
                    if config_file.exists():
                        config_file.unlink()
                    st.success("已卸载" if lang == "zh" else "Uninstalled")
                    st.rerun()
                except Exception as e:
                    st.error(f"卸载失败: {e}" if lang == "zh" else f"Uninstall failed: {e}")
        
        else:
            st.warning("⚠️ 未安装" if lang == "zh" else "⚠️ Not Installed")
            
            if st.button("一键安装" if lang == "zh" else "Install", type="primary"):
                with st.spinner("安装中..." if lang == "zh" else "Installing..."):
                    try:
                        # Create directories
                        hooks_dir = openclaw_dir / "hooks"
                        hooks_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Copy hook file
                        hook_src = Path(__file__).parent.parent.parent / "integrations" / "openclaw_hook.py"
                        shutil.copy2(hook_src, hook_file)
                        
                        # Create config
                        config = {
                            "min_messages": 10,
                            "auto_index": True,
                            "auto_backup": False,
                            "backup_interval_hours": 24,
                            "workspace_dir": str(openclaw_dir / "workspace"),
                            "enabled": True
                        }
                        config_file.write_text(json.dumps(config, indent=2))
                        
                        st.success("✅ 安装成功！请重启 OpenClaw Gateway" if lang == "zh" else "✅ Installed! Please restart OpenClaw Gateway")
                        st.rerun()
                    except Exception as e:
                        st.error(f"安装失败: {e}" if lang == "zh" else f"Installation failed: {e}")
    
    # Tab 2: Data Management
    with tab2:
        st.subheader("数据管理" if lang == "zh" else "Data Management")
        
        # Export
        st.markdown("### 导出数据" if lang == "zh" else "### Export Data")
        
        observations_dir = Path.cwd() / "memory" / "observations"
        if observations_dir.exists():
            session_files = list(observations_dir.glob("*.md"))
            session_ids = [f.stem for f in session_files]
            
            if session_ids:
                selected_session = st.selectbox(
                    "选择会话" if lang == "zh" else "Select Session",
                    session_ids
                )
                export_format = st.radio(
                    "格式" if lang == "zh" else "Format",
                    ["JSON", "CSV"]
                )
                
                if st.button("导出" if lang == "zh" else "Export"):
                    try:
                        if export_format == "JSON":
                            path = data_manager.export_session_json(selected_session)
                        else:
                            path = data_manager.export_session_csv(selected_session)
                        
                        # Provide download
                        with open(path, "rb") as f:
                            st.download_button(
                                "下载文件" if lang == "zh" else "Download File",
                                f,
                                file_name=path.name
                            )
                    except Exception as e:
                        st.error(f"导出失败: {e}" if lang == "zh" else f"Export failed: {e}")
        
        st.markdown("---")
        
        # Backup
        st.markdown("### 备份管理" if lang == "zh" else "### Backup Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**创建备份**" if lang == "zh" else "**Create Backup**")
            backup_name = st.text_input("备份名称（可选）" if lang == "zh" else "Backup Name (optional)")
            
            if st.button("创建备份" if lang == "zh" else "Create Backup"):
                try:
                    path = data_manager.create_backup(backup_name if backup_name else None)
                    st.success(f"备份已创建: {path.name}" if lang == "zh" else f"Backup created: {path.name}")
                except Exception as e:
                    st.error(f"备份失败: {e}" if lang == "zh" else f"Backup failed: {e}")
        
        with col2:
            st.markdown("**恢复备份**" if lang == "zh" else "**Restore Backup**")
            backups = data_manager.list_backups()
            
            if backups:
                backup_names = [b["name"] for b in backups]
                selected_backup = st.selectbox("选择备份" if lang == "zh" else "Select Backup", backup_names)
                
                if st.button("恢复" if lang == "zh" else "Restore"):
                    try:
                        backup_path = Path(backups[backup_names.index(selected_backup)]["path"])
                        data_manager.restore_backup(backup_path, overwrite=True)
                        st.success("备份已恢复" if lang == "zh" else "Backup restored")
                        st.rerun()
                    except Exception as e:
                        st.error(f"恢复失败: {e}" if lang == "zh" else f"Restore failed: {e}")
    
    # Tab 3: System Status
    with tab3:
        st.subheader("系统状态" if lang == "zh" else "System Status")
        
        # Statistics
        observations_dir = Path.cwd() / "memory" / "observations"
        
        if observations_dir.exists():
            session_files = list(observations_dir.glob("*.md"))
            total_sessions = len(session_files)
            
            total_observations = 0
            total_size = 0
            for file in session_files:
                content = file.read_text(encoding="utf-8")
                lines = [l for l in content.split("\n") if l.strip() and not l.startswith("Date:")]
                total_observations += len(lines)
                total_size += file.stat().st_size
            
            vector_stats = vector_manager.get_statistics()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("总会话数" if lang == "zh" else "Total Sessions", total_sessions)
            col2.metric("总观察数" if lang == "zh" else "Total Observations", total_observations)
            col3.metric("向量嵌入" if lang == "zh" else "Vector Embeddings", vector_stats["total_embeddings"])
            
            st.markdown("---")
            
            # Storage
            st.markdown("### 存储使用" if lang == "zh" else "### Storage Usage")
            
            col1, col2 = st.columns(2)
            col1.metric("观察数据" if lang == "zh" else "Observations Data", f"{total_size / 1024:.1f} KB")
            
            vector_db = Path.cwd() / "memory" / "observations" / "vector_search.db"
            if vector_db.exists():
                vector_size = vector_db.stat().st_size
                col2.metric("向量数据库" if lang == "zh" else "Vector Database", f"{vector_size / 1024:.1f} KB")
    
    # Tab 4: Configuration
    with tab4:
        st.subheader("配置" if lang == "zh" else "Configuration")
        
        st.markdown("### 界面设置" if lang == "zh" else "### Interface Settings")
        
        # Language already handled in sidebar
        st.info("语言设置在侧边栏" if lang == "zh" else "Language setting is in the sidebar")
        
        st.markdown("### 自动处理" if lang == "zh" else "### Auto Processing")
        
        auto_process = st.checkbox("启用自动处理" if lang == "zh" else "Enable Auto Processing", value=True)
        if auto_process:
            threshold = st.slider(
                "消息阈值" if lang == "zh" else "Message Threshold",
                min_value=5,
                max_value=50,
                value=10
            )
