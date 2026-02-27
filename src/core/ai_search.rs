use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryIntent {
    pub intent_type: IntentType,
    pub entities: Vec<Entity>,
    pub time_range: Option<TimeRange>,
    pub keywords: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum IntentType {
    Search,           // 搜索查询
    Summary,          // 摘要请求
    Question,         // 问答
    Navigation,       // 导航
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Entity {
    pub entity_type: EntityType,
    pub value: String,
    pub confidence: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EntityType {
    Person,           // 人物
    Project,          // 项目
    Technology,       // 技术
    Topic,            // 主题
    Date,             // 日期
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TimeRange {
    pub start: Option<String>,
    pub end: Option<String>,
    pub relative: Option<String>, // "上周", "昨天", "最近7天"
}

pub struct AISearchEngine {
    // 时间关键词映射
    time_keywords: HashMap<String, i64>,
    // 实体关键词
    entity_keywords: HashMap<String, EntityType>,
}

impl AISearchEngine {
    pub fn new() -> Self {
        let mut time_keywords = HashMap::new();
        time_keywords.insert("今天".to_string(), 0);
        time_keywords.insert("昨天".to_string(), -1);
        time_keywords.insert("前天".to_string(), -2);
        time_keywords.insert("上周".to_string(), -7);
        time_keywords.insert("本周".to_string(), 0);
        time_keywords.insert("上个月".to_string(), -30);
        time_keywords.insert("最近".to_string(), -7);
        
        let mut entity_keywords = HashMap::new();
        entity_keywords.insert("rust".to_string(), EntityType::Technology);
        entity_keywords.insert("python".to_string(), EntityType::Technology);
        entity_keywords.insert("javascript".to_string(), EntityType::Technology);
        entity_keywords.insert("typescript".to_string(), EntityType::Technology);
        entity_keywords.insert("go".to_string(), EntityType::Technology);
        entity_keywords.insert("项目".to_string(), EntityType::Project);
        entity_keywords.insert("功能".to_string(), EntityType::Topic);
        entity_keywords.insert("bug".to_string(), EntityType::Topic);
        entity_keywords.insert("优化".to_string(), EntityType::Topic);
        
        Self {
            time_keywords,
            entity_keywords,
        }
    }
    
    /// 解析自然语言查询
    pub fn parse_query(&self, query: &str) -> QueryIntent {
        let query_lower = query.to_lowercase();
        
        // 识别意图类型
        let intent_type = self.detect_intent(&query_lower);
        
        // 提取实体
        let entities = self.extract_entities(&query_lower);
        
        // 提取时间范围
        let time_range = self.extract_time_range(&query_lower);
        
        // 提取关键词
        let keywords = self.extract_keywords(&query_lower);
        
        QueryIntent {
            intent_type,
            entities,
            time_range,
            keywords,
        }
    }
    
    fn detect_intent(&self, query: &str) -> IntentType {
        if query.contains("总结") || query.contains("摘要") || query.contains("概括") {
            IntentType::Summary
        } else if query.contains("什么") || query.contains("如何") || query.contains("为什么") || query.contains("?") {
            IntentType::Question
        } else if query.contains("查看") || query.contains("打开") || query.contains("进入") {
            IntentType::Navigation
        } else {
            IntentType::Search
        }
    }
    
    fn extract_entities(&self, query: &str) -> Vec<Entity> {
        let mut entities = Vec::new();
        
        for (keyword, entity_type) in &self.entity_keywords {
            if query.contains(keyword) {
                entities.push(Entity {
                    entity_type: entity_type.clone(),
                    value: keyword.clone(),
                    confidence: 0.8,
                });
            }
        }
        
        entities
    }
    
    fn extract_time_range(&self, query: &str) -> Option<TimeRange> {
        for (keyword, days_offset) in &self.time_keywords {
            if query.contains(keyword) {
                return Some(TimeRange {
                    start: None,
                    end: None,
                    relative: Some(keyword.clone()),
                });
            }
        }
        None
    }
    
    fn extract_keywords(&self, query: &str) -> Vec<String> {
        // 简单的分词（按空格和标点分割）
        query
            .split(|c: char| c.is_whitespace() || c.is_ascii_punctuation())
            .filter(|s| s.len() > 1)
            .map(|s| s.to_string())
            .collect()
    }
    
    /// 生成搜索建议
    pub fn generate_suggestions(&self, partial_query: &str) -> Vec<String> {
        let mut suggestions = Vec::new();
        
        // 基于部分查询生成建议
        if partial_query.len() < 2 {
            return suggestions;
        }
        
        let query_lower = partial_query.to_lowercase();
        
        // 时间相关建议
        if query_lower.contains("上") || query_lower.contains("最近") {
            suggestions.push("上周的讨论".to_string());
            suggestions.push("最近7天的对话".to_string());
            suggestions.push("上个月的项目".to_string());
        }
        
        // 技术相关建议
        if query_lower.contains("rust") || query_lower.contains("技术") {
            suggestions.push("Rust 相关的讨论".to_string());
            suggestions.push("技术栈选择".to_string());
        }
        
        // 项目相关建议
        if query_lower.contains("项目") || query_lower.contains("功能") {
            suggestions.push("项目进度".to_string());
            suggestions.push("功能开发".to_string());
            suggestions.push("Bug 修复".to_string());
        }
        
        suggestions
    }
    
    /// 优化搜索结果排序
    pub fn rank_results(&self, results: &mut Vec<(String, f32)>, intent: &QueryIntent) {
        // 根据意图和实体调整相关性分数
        for (content, score) in results.iter_mut() {
            let content_lower = content.to_lowercase();
            
            // 实体匹配加分
            for entity in &intent.entities {
                if content_lower.contains(&entity.value) {
                    *score += 0.2 * entity.confidence;
                }
            }
            
            // 关键词匹配加分
            for keyword in &intent.keywords {
                if content_lower.contains(keyword) {
                    *score += 0.1;
                }
            }
        }
        
        // 按分数降序排序
        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_parse_query() {
        let engine = AISearchEngine::new();
        
        let intent = engine.parse_query("上周关于 Rust 的讨论");
        assert!(matches!(intent.intent_type, IntentType::Search));
        assert!(intent.time_range.is_some());
        assert!(!intent.entities.is_empty());
    }
    
    #[test]
    fn test_detect_intent() {
        let engine = AISearchEngine::new();
        
        assert!(matches!(
            engine.detect_intent("总结一下项目进度"),
            IntentType::Summary
        ));
        
        assert!(matches!(
            engine.detect_intent("什么是 Rust"),
            IntentType::Question
        ));
    }
}
