use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnowledgeGraph {
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Node {
    pub id: String,
    pub label: String,
    pub node_type: NodeType,
    pub properties: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum NodeType {
    Person,
    Project,
    Technology,
    Topic,
    Concept,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Edge {
    pub id: String,
    pub source: String,
    pub target: String,
    pub relation: RelationType,
    pub weight: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RelationType {
    WorksOn,      // 人物 -> 项目
    Uses,         // 项目 -> 技术
    RelatesTo,    // 主题 -> 主题
    DependsOn,    // 项目 -> 项目
    Discusses,    // 人物 -> 主题
    Implements,   // 项目 -> 功能
}

pub struct KnowledgeGraphBuilder {
    // 实体模式
    entity_patterns: HashMap<String, NodeType>,
    // 关系模式
    relation_patterns: Vec<(String, RelationType)>,
}

impl KnowledgeGraphBuilder {
    pub fn new() -> Self {
        let mut entity_patterns = HashMap::new();
        
        // 技术实体
        entity_patterns.insert("rust".to_string(), NodeType::Technology);
        entity_patterns.insert("python".to_string(), NodeType::Technology);
        entity_patterns.insert("javascript".to_string(), NodeType::Technology);
        entity_patterns.insert("typescript".to_string(), NodeType::Technology);
        entity_patterns.insert("react".to_string(), NodeType::Technology);
        entity_patterns.insert("next.js".to_string(), NodeType::Technology);
        entity_patterns.insert("axum".to_string(), NodeType::Technology);
        entity_patterns.insert("数据库".to_string(), NodeType::Technology);
        entity_patterns.insert("api".to_string(), NodeType::Technology);
        
        // 项目实体
        entity_patterns.insert("项目".to_string(), NodeType::Project);
        entity_patterns.insert("系统".to_string(), NodeType::Project);
        entity_patterns.insert("应用".to_string(), NodeType::Project);
        entity_patterns.insert("平台".to_string(), NodeType::Project);
        
        // 主题实体
        entity_patterns.insert("功能".to_string(), NodeType::Topic);
        entity_patterns.insert("优化".to_string(), NodeType::Topic);
        entity_patterns.insert("bug".to_string(), NodeType::Topic);
        entity_patterns.insert("性能".to_string(), NodeType::Topic);
        entity_patterns.insert("安全".to_string(), NodeType::Topic);
        
        let relation_patterns = vec![
            ("使用".to_string(), RelationType::Uses),
            ("开发".to_string(), RelationType::WorksOn),
            ("实现".to_string(), RelationType::Implements),
            ("依赖".to_string(), RelationType::DependsOn),
            ("讨论".to_string(), RelationType::Discusses),
            ("关于".to_string(), RelationType::RelatesTo),
        ];
        
        Self {
            entity_patterns,
            relation_patterns,
        }
    }
    
    /// 从文本构建知识图谱
    pub fn build_from_texts(&self, texts: &[String]) -> KnowledgeGraph {
        let mut nodes = Vec::new();
        let mut edges = Vec::new();
        let mut node_ids = HashSet::new();
        
        // 提取实体（节点）
        for text in texts {
            let extracted_nodes = self.extract_entities(text);
            for node in extracted_nodes {
                if !node_ids.contains(&node.id) {
                    node_ids.insert(node.id.clone());
                    nodes.push(node);
                }
            }
        }
        
        // 提取关系（边）
        for text in texts {
            let extracted_edges = self.extract_relations(text, &nodes);
            edges.extend(extracted_edges);
        }
        
        // 计算边的权重（基于共现频率）
        self.calculate_edge_weights(&mut edges);
        
        KnowledgeGraph { nodes, edges }
    }
    
    /// 提取实体
    fn extract_entities(&self, text: &str) -> Vec<Node> {
        let mut nodes = Vec::new();
        let text_lower = text.to_lowercase();
        
        for (pattern, node_type) in &self.entity_patterns {
            if text_lower.contains(pattern) {
                let node = Node {
                    id: format!("{}_{}", pattern, uuid::Uuid::new_v4()),
                    label: pattern.clone(),
                    node_type: node_type.clone(),
                    properties: HashMap::new(),
                };
                nodes.push(node);
            }
        }
        
        nodes
    }
    
    /// 提取关系
    fn extract_relations(&self, text: &str, nodes: &[Node]) -> Vec<Edge> {
        let mut edges = Vec::new();
        let text_lower = text.to_lowercase();
        
        // 查找关系模式
        for (pattern, relation_type) in &self.relation_patterns {
            if text_lower.contains(pattern) {
                // 查找模式前后的实体
                if let Some(pos) = text_lower.find(pattern) {
                    let before = &text_lower[..pos];
                    let after = &text_lower[pos + pattern.len()..];
                    
                    // 查找前后的实体
                    let source_entities: Vec<_> = nodes
                        .iter()
                        .filter(|n| before.contains(&n.label))
                        .collect();
                    
                    let target_entities: Vec<_> = nodes
                        .iter()
                        .filter(|n| after.contains(&n.label))
                        .collect();
                    
                    // 创建边
                    for source in &source_entities {
                        for target in &target_entities {
                            let edge = Edge {
                                id: uuid::Uuid::new_v4().to_string(),
                                source: source.id.clone(),
                                target: target.id.clone(),
                                relation: relation_type.clone(),
                                weight: 1.0,
                            };
                            edges.push(edge);
                        }
                    }
                }
            }
        }
        
        edges
    }
    
    /// 计算边的权重
    fn calculate_edge_weights(&self, edges: &mut [Edge]) {
        let mut edge_counts: HashMap<(String, String), usize> = HashMap::new();
        
        // 统计边的出现次数
        for edge in edges.iter() {
            let key = (edge.source.clone(), edge.target.clone());
            *edge_counts.entry(key).or_insert(0) += 1;
        }
        
        // 更新权重
        for edge in edges.iter_mut() {
            let key = (edge.source.clone(), edge.target.clone());
            if let Some(&count) = edge_counts.get(&key) {
                edge.weight = (count as f32).ln() + 1.0;
            }
        }
    }
    
    /// 查询相关实体
    pub fn find_related_entities(
        &self,
        graph: &KnowledgeGraph,
        entity_id: &str,
        max_depth: usize,
    ) -> Vec<Node> {
        let mut related = Vec::new();
        let mut visited = HashSet::new();
        let mut queue = vec![(entity_id.to_string(), 0)];
        
        while let Some((current_id, depth)) = queue.pop() {
            if depth >= max_depth || visited.contains(&current_id) {
                continue;
            }
            
            visited.insert(current_id.clone());
            
            // 查找当前节点
            if let Some(node) = graph.nodes.iter().find(|n| n.id == current_id) {
                related.push(node.clone());
            }
            
            // 查找相邻节点
            for edge in &graph.edges {
                if edge.source == current_id && !visited.contains(&edge.target) {
                    queue.push((edge.target.clone(), depth + 1));
                } else if edge.target == current_id && !visited.contains(&edge.source) {
                    queue.push((edge.source.clone(), depth + 1));
                }
            }
        }
        
        related
    }
    
    /// 查找最短路径
    pub fn find_shortest_path(
        &self,
        graph: &KnowledgeGraph,
        start_id: &str,
        end_id: &str,
    ) -> Option<Vec<String>> {
        let mut queue = vec![(start_id.to_string(), vec![start_id.to_string()])];
        let mut visited = HashSet::new();
        
        while let Some((current_id, path)) = queue.pop() {
            if current_id == end_id {
                return Some(path);
            }
            
            if visited.contains(&current_id) {
                continue;
            }
            
            visited.insert(current_id.clone());
            
            // 查找相邻节点
            for edge in &graph.edges {
                let next_id = if edge.source == current_id {
                    &edge.target
                } else if edge.target == current_id {
                    &edge.source
                } else {
                    continue;
                };
                
                if !visited.contains(next_id) {
                    let mut new_path = path.clone();
                    new_path.push(next_id.clone());
                    queue.push((next_id.clone(), new_path));
                }
            }
        }
        
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_build_knowledge_graph() {
        let builder = KnowledgeGraphBuilder::new();
        let texts = vec![
            "使用 Rust 开发项目".to_string(),
            "项目实现了新功能".to_string(),
        ];
        
        let graph = builder.build_from_texts(&texts);
        assert!(!graph.nodes.is_empty());
    }
    
    #[test]
    fn test_extract_entities() {
        let builder = KnowledgeGraphBuilder::new();
        let nodes = builder.extract_entities("使用 Rust 和 Python 开发");
        assert!(!nodes.is_empty());
    }
}
