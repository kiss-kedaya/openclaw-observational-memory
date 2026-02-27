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
