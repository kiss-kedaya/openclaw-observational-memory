use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Summary {
    pub id: String,
    pub summary_type: SummaryType,
    pub content: String,
    pub key_points: Vec<String>,
    pub entities: Vec<String>,
    pub period_start: String,
    pub period_end: String,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SummaryType {
    Session,    // 会话摘要
    Daily,      // 每日摘要
    Weekly,     // 每周摘要
    Monthly,    // 每月摘要
}

pub struct SummaryGenerator {
    // 关键词权重
    keyword_weights: HashMap<String, f32>,
}

impl SummaryGenerator {
    pub fn new() -> Self {
        let mut keyword_weights = HashMap::new();
        
        // 高权重关键词
        keyword_weights.insert("重要".to_string(), 2.0);
        keyword_weights.insert("关键".to_string(), 2.0);
        keyword_weights.insert("紧急".to_string(), 2.0);
        keyword_weights.insert("完成".to_string(), 1.5);
        keyword_weights.insert("实现".to_string(), 1.5);
        keyword_weights.insert("修复".to_string(), 1.5);
        keyword_weights.insert("优化".to_string(), 1.3);
        keyword_weights.insert("改进".to_string(), 1.3);
        keyword_weights.insert("问题".to_string(), 1.2);
        keyword_weights.insert("bug".to_string(), 1.2);
        
        Self { keyword_weights }
    }
    
    /// 生成会话摘要
    pub fn generate_session_summary(&self, messages: &[String]) -> Summary {
        let key_points = self.extract_key_points(messages);
        let entities = self.extract_entities(messages);
        let content = self.generate_summary_text(&key_points);
        
        Summary {
            id: uuid::Uuid::new_v4().to_string(),
            summary_type: SummaryType::Session,
            content,
            key_points,
            entities,
            period_start: chrono::Utc::now().to_rfc3339(),
            period_end: chrono::Utc::now().to_rfc3339(),
            created_at: chrono::Utc::now().to_rfc3339(),
        }
    }
    
    /// 生成每日摘要
    pub fn generate_daily_summary(&self, messages: &[String]) -> Summary {
        let key_points = self.extract_key_points(messages);
        let entities = self.extract_entities(messages);
        
        // 按主题分组
        let topics = self.group_by_topic(&key_points);
        
        let mut content = String::from("今日摘要：\n\n");
        for (topic, points) in topics {
            content.push_str(&format!("【{}】\n", topic));
            for point in points {
                content.push_str(&format!("- {}\n", point));
            }
            content.push('\n');
        }
        
        Summary {
            id: uuid::Uuid::new_v4().to_string(),
            summary_type: SummaryType::Daily,
            content,
            key_points,
            entities,
            period_start: chrono::Utc::now().to_rfc3339(),
            period_end: chrono::Utc::now().to_rfc3339(),
            created_at: chrono::Utc::now().to_rfc3339(),
        }
    }
    
    /// 生成每周摘要
    pub fn generate_weekly_summary(&self, messages: &[String]) -> Summary {
        let key_points = self.extract_key_points(messages);
        let entities = self.extract_entities(messages);
        
        // 统计关键指标
        let stats = self.calculate_stats(messages);
        
        let mut content = String::from("本周摘要：\n\n");
        content.push_str(&format!("总对话数：{}\n", messages.len()));
        content.push_str(&format!("关键事项：{}\n\n", key_points.len()));
        
        content.push_str("重点内容：\n");
        for (i, point) in key_points.iter().take(10).enumerate() {
            content.push_str(&format!("{}. {}\n", i + 1, point));
        }
        
        Summary {
            id: uuid::Uuid::new_v4().to_string(),
            summary_type: SummaryType::Weekly,
            content,
            key_points,
            entities,
            period_start: chrono::Utc::now().to_rfc3339(),
            period_end: chrono::Utc::now().to_rfc3339(),
            created_at: chrono::Utc::now().to_rfc3339(),
        }
    }
    
    /// 提取关键要点
    fn extract_key_points(&self, messages: &[String]) -> Vec<String> {
        let mut scored_sentences: Vec<(String, f32)> = Vec::new();
        
        for message in messages {
            // 按句子分割
            let sentences: Vec<&str> = message
                .split(|c| c == '。' || c == '！' || c == '？' || c == '.' || c == '!' || c == '?')
                .filter(|s| s.len() > 10)
                .collect();
            
            for sentence in sentences {
                let score = self.calculate_sentence_score(sentence);
                if score > 0.5 {
                    scored_sentences.push((sentence.to_string(), score));
                }
            }
        }
        
        // 按分数排序
        scored_sentences.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        
        // 返回前 N 个关键句子
        scored_sentences
            .into_iter()
            .take(10)
            .map(|(s, _)| s)
            .collect()
    }
    
    /// 计算句子重要性分数
    fn calculate_sentence_score(&self, sentence: &str) -> f32 {
        let mut score = 0.0;
        let sentence_lower = sentence.to_lowercase();
        
        // 关键词匹配
        for (keyword, weight) in &self.keyword_weights {
            if sentence_lower.contains(keyword) {
                score += weight;
            }
        }
        
        // 长度加分（适中长度的句子更重要）
        let len = sentence.len();
        if len > 20 && len < 200 {
            score += 0.5;
        }
        
        // 包含数字加分（可能是统计数据）
        if sentence.chars().any(|c| c.is_numeric()) {
            score += 0.3;
        }
        
        score
    }
    
    /// 提取实体
    fn extract_entities(&self, messages: &[String]) -> Vec<String> {
        let mut entities = Vec::new();
        let content = messages.join(" ");
        
        // 简单的实体识别（基于关键词）
        let entity_patterns = vec![
            "项目", "功能", "模块", "系统", "服务",
            "Rust", "Python", "JavaScript", "TypeScript",
            "数据库", "API", "前端", "后端",
        ];
        
        for pattern in entity_patterns {
            if content.contains(pattern) {
                entities.push(pattern.to_string());
            }
        }
        
        entities.sort();
        entities.dedup();
        entities
    }
    
    /// 按主题分组
    fn group_by_topic(&self, points: &[String]) -> HashMap<String, Vec<String>> {
        let mut groups: HashMap<String, Vec<String>> = HashMap::new();
        
        for point in points {
            let topic = self.identify_topic(point);
            groups.entry(topic).or_insert_with(Vec::new).push(point.clone());
        }
        
        groups
    }
    
    /// 识别主题
    fn identify_topic(&self, text: &str) -> String {
        let text_lower = text.to_lowercase();
        
        if text_lower.contains("bug") || text_lower.contains("修复") || text_lower.contains("问题") {
            "Bug 修复".to_string()
        } else if text_lower.contains("功能") || text_lower.contains("实现") || text_lower.contains("开发") {
            "功能开发".to_string()
        } else if text_lower.contains("优化") || text_lower.contains("改进") || text_lower.contains("性能") {
            "优化改进".to_string()
        } else if text_lower.contains("讨论") || text_lower.contains("决策") || text_lower.contains("方案") {
            "讨论决策".to_string()
        } else {
            "其他".to_string()
        }
    }
    
    /// 生成摘要文本
    fn generate_summary_text(&self, key_points: &[String]) -> String {
        if key_points.is_empty() {
            return "暂无重要内容".to_string();
        }
        
        let mut summary = String::from("本次对话主要讨论了以下内容：\n\n");
        for (i, point) in key_points.iter().enumerate() {
            summary.push_str(&format!("{}. {}\n", i + 1, point));
        }
        
        summary
    }
    
    /// 计算统计数据
    fn calculate_stats(&self, messages: &[String]) -> HashMap<String, usize> {
        let mut stats = HashMap::new();
        
        stats.insert("total_messages".to_string(), messages.len());
        
        let total_chars: usize = messages.iter().map(|m| m.len()).sum();
        stats.insert("total_chars".to_string(), total_chars);
        
        stats
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_generate_session_summary() {
        let generator = SummaryGenerator::new();
        let messages = vec![
            "今天完成了 Rust 后端的开发".to_string(),
            "修复了一个重要的 bug".to_string(),
            "优化了数据库查询性能".to_string(),
        ];
        
        let summary = generator.generate_session_summary(&messages);
        assert!(!summary.key_points.is_empty());
        assert!(!summary.entities.is_empty());
    }
    
    #[test]
    fn test_extract_key_points() {
        let generator = SummaryGenerator::new();
        let messages = vec![
            "这是一个重要的功能实现。需要优化性能。".to_string(),
        ];
        
        let points = generator.extract_key_points(&messages);
        assert!(!points.is_empty());
    }
}
