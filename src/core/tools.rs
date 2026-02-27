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
    patterns: HashMap<String, Regex>,
}

impl ToolSuggestionEngine {
    pub fn new() -> Self {
        let mut patterns = HashMap::new();
        
        patterns.insert(
            "agent-reach".to_string(),
            Regex::new(r"(?i)(twitter|reddit|github|youtube)\.com").unwrap(),
        );
        
        patterns.insert(
            "agent-browser".to_string(),
            Regex::new(r"(?i)(login|form|screenshot|pdf|browser)").unwrap(),
        );
        
        patterns.insert(
            "web_search".to_string(),
            Regex::new(r"(?i)(search|find|lookup|query)").unwrap(),
        );
        
        patterns.insert(
            "debugging-wizard".to_string(),
            Regex::new(r"(?i)(error|bug|exception|crash)").unwrap(),
        );

        Self { patterns }
    }

    pub fn analyze(&self, obs: &Observation) -> Vec<ToolSuggestion> {
        let mut suggestions = Vec::new();
        
        for (tool, pattern) in &self.patterns {
            if pattern.is_match(&obs.content) {
                suggestions.push(ToolSuggestion {
                    tool: tool.clone(),
                    reason: format!("Detected pattern for {}", tool),
                    confidence: 0.8,
                    context: obs.content.chars().take(50).collect(),
                });
            }
        }
        
        suggestions
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_social_media() {
        let engine = ToolSuggestionEngine::new();
        let obs = Observation {
            id: "1".to_string(),
            session_id: "test".to_string(),
            content: "Check this tweet: https://twitter.com/user/status/123".to_string(),
            priority: "HIGH".to_string(),
            created_at: chrono::Utc::now(),
        };

        let suggestions = engine.analyze(&obs);
        assert!(!suggestions.is_empty());
        assert_eq!(suggestions[0].tool, "agent-reach");
    }

    #[test]
    fn test_detect_browser_need() {
        let engine = ToolSuggestionEngine::new();
        let obs = Observation {
            id: "1".to_string(),
            session_id: "test".to_string(),
            content: "Need to login to the website".to_string(),
            priority: "MEDIUM".to_string(),
            created_at: chrono::Utc::now(),
        };

        let suggestions = engine.analyze(&obs);
        assert!(!suggestions.is_empty());
        assert_eq!(suggestions[0].tool, "agent-browser");
    }

    #[test]
    fn test_no_match() {
        let engine = ToolSuggestionEngine::new();
        let obs = Observation {
            id: "1".to_string(),
            session_id: "test".to_string(),
            content: "Just a normal observation".to_string(),
            priority: "LOW".to_string(),
            created_at: chrono::Utc::now(),
        };

        let suggestions = engine.analyze(&obs);
        assert!(suggestions.is_empty());
    }
}
