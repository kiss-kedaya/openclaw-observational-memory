use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Session {
    pub id: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub message_count: i32,
    pub token_count: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Observation {
    pub id: String,
    pub session_id: String,
    pub content: String,
    pub priority: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
    pub timestamp: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub session_id: String,
    pub observation: String,
    pub similarity: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolSuggestion {
    pub tool: String,
    pub reason: String,
    pub confidence: f32,
    pub context: String,
}
