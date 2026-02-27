use std::collections::HashMap;

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
        
        // Remove duplicates
        let mut seen = std::collections::HashSet::new();
        let compressed: Vec<_> = observations
            .into_iter()
            .filter(|obs| {
                let normalized = obs.content.to_lowercase().trim().to_string();
                seen.insert(normalized)
            })
            .collect();

        let compressed_count = compressed.len();
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
        let mut clusters: HashMap<String, Vec<String>> = HashMap::new();

        let keywords = vec![
            ("工具", vec!["工具", "tool", "安装", "install"]),
            ("错误", vec!["错误", "error", "bug", "问题"]),
            ("配置", vec!["配置", "config", "设置", "setting"]),
            ("UI", vec!["界面", "UI", "页面", "page"]),
            ("数据", vec!["数据", "data", "导出", "export"]),
        ];

        for obs in observations {
            let mut matched = false;
            for (topic, kws) in &keywords {
                if kws.iter().any(|kw| obs.content.to_lowercase().contains(kw)) {
                    clusters
                        .entry(topic.to_string())
                        .or_insert_with(Vec::new)
                        .push(obs.content.clone());
                    matched = true;
                    break;
                }
            }

            if !matched {
                clusters
                    .entry("其他".to_string())
                    .or_insert_with(Vec::new)
                    .push(obs.content);
            }
        }

        clusters
            .into_iter()
            .map(|(topic, observations)| Cluster {
                count: observations.len(),
                topic,
                observations,
            })
            .collect()
    }

    pub fn advanced_search(
        &self,
        observations: Vec<Observation>,
        query: &str,
        priority: Option<&str>,
        use_regex: bool,
    ) -> Vec<Observation> {
        observations
            .into_iter()
            .filter(|obs| {
                // Priority filter
                if let Some(p) = priority {
                    if obs.priority != p {
                        return false;
                    }
                }

                // Query filter
                if use_regex {
                    if let Ok(re) = regex::Regex::new(query) {
                        re.is_match(&obs.content)
                    } else {
                        false
                    }
                } else {
                    obs.content.to_lowercase().contains(&query.to_lowercase())
                }
            })
            .collect()
    }
}
