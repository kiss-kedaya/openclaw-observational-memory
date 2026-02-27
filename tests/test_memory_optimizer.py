"""
Tests for Memory Optimizer
"""

import pytest
from pathlib import Path
from observational_memory.memory_optimizer import MemoryOptimizer


def test_compression(tmp_path):
    optimizer = MemoryOptimizer(tmp_path)
    
    # Create test observations
    obs_dir = tmp_path / "memory" / "observations"
    obs_dir.mkdir(parents=True)
    
    obs_file = obs_dir / "test_session.md"
    obs_file.write_text("Date: 2026-02-27\n\n观察1\n观察1\n观察2\n观察3", encoding="utf-8")
    
    result = optimizer.compress_observations("test_session")
    
    assert result["original_count"] == 4
    assert result["compressed_count"] == 3
    assert result["removed"] == 1


def test_clustering():
    optimizer = MemoryOptimizer()
    
    observations = [
        "安装了工具",
        "代码报错了",
        "配置文件修改",
        "UI 设计完成",
        "数据导出成功"
    ]
    
    clusters = optimizer.cluster_by_topic(observations)
    
    assert len(clusters) > 0
    assert "工具" in clusters or "错误" in clusters or "配置" in clusters


def test_markdown_export(tmp_path):
    optimizer = MemoryOptimizer(tmp_path)
    
    obs_dir = tmp_path / "memory" / "observations"
    obs_dir.mkdir(parents=True)
    
    obs_file = obs_dir / "test_session.md"
    obs_file.write_text("Date: 2026-02-27\n\n观察1\n观察2", encoding="utf-8")
    
    export_path = optimizer.export_as_markdown("test_session")
    
    assert export_path.exists()
    assert export_path.suffix == ".md"
    content = export_path.read_text(encoding="utf-8")
    assert "观察1" in content


def test_knowledge_graph_export(tmp_path):
    optimizer = MemoryOptimizer(tmp_path)
    
    obs_dir = tmp_path / "memory" / "observations"
    obs_dir.mkdir(parents=True)
    
    obs_file = obs_dir / "test_session.md"
    obs_file.write_text("Date: 2026-02-27\n\n观察1\n观察2", encoding="utf-8")
    
    export_path = optimizer.export_as_knowledge_graph("test_session")
    
    assert export_path.exists()
    assert export_path.suffix == ".json"
    
    import json
    graph = json.loads(export_path.read_text(encoding="utf-8"))
    assert graph["@type"] == "Dataset"
    assert len(graph["hasPart"]) == 2


def test_advanced_search(tmp_path):
    optimizer = MemoryOptimizer(tmp_path)
    
    obs_dir = tmp_path / "memory" / "observations"
    obs_dir.mkdir(parents=True)
    
    obs_file = obs_dir / "test_session.md"
    obs_file.write_text("Date: 2026-02-27\n\n[HIGH] 重要观察\n[LOW] 普通观察", encoding="utf-8")
    
    results = optimizer.advanced_search("重要")
    assert len(results) > 0
    
    results = optimizer.advanced_search("观察", priority="HIGH")
    assert len(results) > 0
