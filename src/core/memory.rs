use crate::db::models::Observation;

#[derive(Debug, Clone, serde::Serialize)]
pub struct CompressionResult {
    pub original_count: usize,
    pub compressed_count: usize,
    pub removed: usize,
    pub ratio: f32,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct Cluster {
    pub topic: String,
    pub observations: Vec<String>,
    pub count: usize,
}

pub struct MemoryOptimizer;

impl MemoryOptimizer {
    pub fn new() -> Self {
        Self
    }

    pub fn compress(&self, observations: Vec<Observation>) -> CompressionResult {
        let original_count = observations.len();
        
        let mut unique = Vec::new();
        for obs in observations {
            if !unique.iter().any(|o: &Observation| o.content == obs.content) {
                unique.push(obs);
            }
        }
        
        let compressed_count = unique.len();
        let removed = original_count - compressed_count;
        let ratio = if original_count > 0 {
            removed as f32 / original_count as f32
        } else {
            0.0
        };

        CompressionResult {
            original_count,
            compressed_count,
            removed,
            ratio,
        }
    }

    pub fn cluster_by_topic(&self, observations: Vec<Observation>) -> Vec<Cluster> {
        let keywords = vec![
            ("Tools", vec!["tool", "agent", "install"]),
            ("Errors", vec!["error", "bug", "exception"]),
            ("Config", vec!["config", "setting", "setup"]),
            ("UI", vec!["ui", "page", "interface"]),
            ("Data", vec!["data", "export", "import"]),
        ];

        let mut clusters = Vec::new();

        for (topic, kws) in keywords {
            let matching: Vec<String> = observations
                .iter()
                .filter(|obs| {
                    kws.iter().any(|kw| obs.content.to_lowercase().contains(kw))
                })
                .map(|obs| obs.content.clone())
                .collect();

            if !matching.is_empty() {
                clusters.push(Cluster {
                    topic: topic.to_string(),
                    count: matching.len(),
                    observations: matching,
                });
            }
        }

        clusters
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compress() {
        let optimizer = MemoryOptimizer::new();
        let observations = vec![
            Observation {
                id: "1".to_string(),
                session_id: "test".to_string(),
                content: "duplicate content".to_string(),
                priority: "HIGH".to_string(),
                created_at: chrono::Utc::now(),
            },
            Observation {
                id: "2".to_string(),
                session_id: "test".to_string(),
                content: "duplicate content".to_string(),
                priority: "HIGH".to_string(),
                created_at: chrono::Utc::now(),
            },
            Observation {
                id: "3".to_string(),
                session_id: "test".to_string(),
                content: "unique content".to_string(),
                priority: "LOW".to_string(),
                created_at: chrono::Utc::now(),
            },
        ];

        let result = optimizer.compress(observations);
        assert_eq!(result.original_count, 3);
        assert_eq!(result.compressed_count, 2);
        assert_eq!(result.removed, 1);
    }

    #[test]
    fn test_cluster_by_topic() {
        let optimizer = MemoryOptimizer::new();
        let observations = vec![
            Observation {
                id: "1".to_string(),
                session_id: "test".to_string(),
                content: "installed new tool".to_string(),
                priority: "HIGH".to_string(),
                created_at: chrono::Utc::now(),
            },
            Observation {
                id: "2".to_string(),
                session_id: "test".to_string(),
                content: "found an error in code".to_string(),
                priority: "HIGH".to_string(),
                created_at: chrono::Utc::now(),
            },
        ];

        let clusters = optimizer.cluster_by_topic(observations);
        assert!(!clusters.is_empty());
    }

    #[test]
    fn test_empty_observations() {
        let optimizer = MemoryOptimizer::new();
        let result = optimizer.compress(vec![]);
        assert_eq!(result.original_count, 0);
        assert_eq!(result.compressed_count, 0);
    }
}
