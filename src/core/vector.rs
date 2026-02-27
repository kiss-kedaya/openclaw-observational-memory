use crate::db::models::Observation;

#[derive(Debug, Clone, serde::Serialize)]
pub struct SearchResult {
    pub id: String,
    pub session_id: String,
    pub content: String,
    pub priority: String,
    pub similarity: f32,
}

pub struct VectorSearchEngine;

impl VectorSearchEngine {
    pub fn new() -> Self {
        Self
    }

    pub fn search(&self, observations: Vec<Observation>, query: &str, threshold: f32) -> Vec<SearchResult> {
        let query_lower = query.to_lowercase();
        
        observations
            .into_iter()
            .filter_map(|obs| {
                let similarity = calculate_similarity(&query_lower, &obs.content.to_lowercase());
                if similarity >= threshold {
                    Some(SearchResult {
                        id: obs.id,
                        session_id: obs.session_id,
                        content: obs.content,
                        priority: obs.priority,
                        similarity,
                    })
                } else {
                    None
                }
            })
            .collect()
    }
}

fn calculate_similarity(query: &str, content: &str) -> f32 {
    let query_words: Vec<&str> = query.split_whitespace().collect();
    let content_words: Vec<&str> = content.split_whitespace().collect();

    if query_words.is_empty() {
        return 0.0;
    }

    let mut matches = 0;
    for word in &query_words {
        if content_words.contains(word) {
            matches += 1;
        }
    }

    (matches as f32) / (query_words.len() as f32)
}
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_similarity() {
        let query = "rust programming";
        let content = "learning rust programming language";
        let similarity = calculate_similarity(query, content);
        assert!(similarity > 0.5);
    }

    #[test]
    fn test_search_with_threshold() {
        let engine = VectorSearchEngine::new();
        let observations = vec![
            Observation {
                id: "1".to_string(),
                session_id: "test".to_string(),
                content: "rust programming tutorial".to_string(),
                priority: "HIGH".to_string(),
                created_at: chrono::Utc::now(),
            },
            Observation {
                id: "2".to_string(),
                session_id: "test".to_string(),
                content: "python data science".to_string(),
                priority: "LOW".to_string(),
                created_at: chrono::Utc::now(),
            },
        ];

        let results = engine.search(observations, "rust", 0.3);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].id, "1");
    }

    #[test]
    fn test_empty_query() {
        let engine = VectorSearchEngine::new();
        let observations = vec![];
        let results = engine.search(observations, "", 0.3);
        assert_eq!(results.len(), 0);
    }
}
