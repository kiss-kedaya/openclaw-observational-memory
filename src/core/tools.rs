use regex::Regex;
use std::collections::HashMap;

use crate::db::models::Observation;

#[derive(Debug, Clone, serde::Serialize)]
pub struct ToolSuggestion {
    pub tool: String,
    pub reason: String,
    pub confidence: f32,
    pub context: String,
}

pub struct ToolSuggestionEngine {
    patterns: HashMap<String, Vec<Regex>>,
}

impl ToolSuggestionEngine {
    pub fn new() -> Self {
        let mut patterns = HashMap::new();

        // Social media patterns
        patterns.insert(
            "social_media".to_string(),
            vec![
                Regex::new(r"twitter\.com").unwrap(),
                Regex::new(r"x\.com").unwrap(),
                Regex::new(r"facebook\.com").unwrap(),
                Regex::new(r"instagram\.com").unwrap(),
                Regex::new(r"linkedin\.com").unwrap(),
                Regex::new(r"weibo\.com").unwrap(),
            ],
        );

        // Browser keywords
        patterns.insert(
            "browser".to_string(),
            vec![
                Regex::new(r"(?i)浏览器").unwrap(),
                Regex::new(r"(?i)browser").unwrap(),
                Regex::new(r"(?i)网页").unwrap(),
                Regex::new(r"(?i)webpage").unwrap(),
                Regex::new(r"(?i)点击").unwrap(),
                Regex::new(r"(?i)click").unwrap(),
            ],
        );

        // Search keywords
        patterns.insert(
            "search".to_string(),
            vec![
                Regex::new(r"(?i)搜索").unwrap(),
                Regex::new(r"(?i)search").unwrap(),
                Regex::new(r"(?i)查找").unwrap(),
                Regex::new(r"(?i)find").unwrap(),
            ],
        );

        // Code keywords
        patterns.insert(
            "code".to_string(),
            vec![
                Regex::new(r"(?i)错误").unwrap(),
                Regex::new(r"(?i)error").unwrap(),
                Regex::new(r"(?i)bug").unwrap(),
                Regex::new(r"(?i)调试").unwrap(),
                Regex::new(r"(?i)debug").unwrap(),
            ],
        );

        Self { patterns }
    }

    pub fn analyze(&self, observation: &Observation) -> Vec<ToolSuggestion> {
        let mut suggestions = Vec::new();

        // Check for social media
        if let Some(suggestion) = self.detect_social_media(&observation.content) {
            suggestions.push(suggestion);
        }

        // Check for browser need
        if let Some(suggestion) = self.detect_browser_need(&observation.content) {
            suggestions.push(suggestion);
        }

        // Check for search need
        if let Some(suggestion) = self.detect_search_need(&observation.content) {
            suggestions.push(suggestion);
        }

        // Check for code issue
        if let Some(suggestion) = self.detect_code_issue(&observation.content) {
            suggestions.push(suggestion);
        }

        suggestions
    }

    fn detect_social_media(&self, text: &str) -> Option<ToolSuggestion> {
        if let Some(patterns) = self.patterns.get("social_media") {
            for pattern in patterns {
                if pattern.is_match(text) {
                    return Some(ToolSuggestion {
                        tool: "agent-reach".to_string(),
                        reason: "检测到社交媒体链接".to_string(),
                        confidence: 0.9,
                        context: self.extract_context(text, pattern),
                    });
                }
            }
        }
        None
    }

    fn detect_browser_need(&self, text: &str) -> Option<ToolSuggestion> {
        if let Some(patterns) = self.patterns.get("browser") {
            for pattern in patterns {
                if pattern.is_match(text) {
                    return Some(ToolSuggestion {
                        tool: "agent-browser".to_string(),
                        reason: "需要浏览器交互".to_string(),
                        confidence: 0.8,
                        context: self.extract_context(text, pattern),
                    });
                }
            }
        }
        None
    }

    fn detect_search_need(&self, text: &str) -> Option<ToolSuggestion> {
        if let Some(patterns) = self.patterns.get("search") {
            for pattern in patterns {
                if pattern.is_match(text) {
                    return Some(ToolSuggestion {
                        tool: "web_search".to_string(),
                        reason: "需要搜索信息".to_string(),
                        confidence: 0.7,
                        context: self.extract_context(text, pattern),
                    });
                }
            }
        }
        None
    }

    fn detect_code_issue(&self, text: &str) -> Option<ToolSuggestion> {
        if let Some(patterns) = self.patterns.get("code") {
            for pattern in patterns {
                if pattern.is_match(text) {
                    return Some(ToolSuggestion {
                        tool: "debugging-wizard".to_string(),
                        reason: "检测到代码问题".to_string(),
                        confidence: 0.75,
                        context: self.extract_context(text, pattern),
                    });
                }
            }
        }
        None
    }

    fn extract_context(&self, text: &str, pattern: &Regex) -> String {
        if let Some(mat) = pattern.find(text) {
            let start = mat.start().saturating_sub(30);
            let end = (mat.end() + 30).min(text.len());
            text[start..end].to_string()
        } else {
            text.chars().take(50).collect()
        }
    }
}
