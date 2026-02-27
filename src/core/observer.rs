use crate::db::models::Message;
use anyhow::Result;

pub struct Observer;

impl Observer {
    pub fn extract_observations(messages: &[Message]) -> Result<Vec<String>> {
        let mut observations = Vec::new();
        
        for msg in messages {
            if msg.role == "assistant" {
                // Extract key information from assistant messages
                let lines: Vec<&str> = msg.content.lines().collect();
                
                for line in lines {
                    let trimmed = line.trim();
                    
                    // Skip empty lines and common patterns
                    if trimmed.is_empty() 
                        || trimmed.starts_with('#')
                        || trimmed.starts_with('-')
                        || trimmed.len() < 10 {
                        continue;
                    }
                    
                    // Extract meaningful observations
                    if Self::is_meaningful(trimmed) {
                        observations.push(trimmed.to_string());
                    }
                }
            }
        }
        
        Ok(observations)
    }
    
    fn is_meaningful(text: &str) -> bool {
        // Check if text contains meaningful information
        let keywords = [
            "完成", "实现", "创建", "修复", "优化", "添加",
            "completed", "implemented", "created", "fixed", "optimized", "added",
            "安装", "配置", "部署", "测试",
            "installed", "configured", "deployed", "tested"
        ];
        
        keywords.iter().any(|&kw| text.to_lowercase().contains(kw))
    }
    
    pub fn calculate_priority(observation: &str) -> String {
        if observation.contains("错误") 
            || observation.contains("error")
            || observation.contains("失败")
            || observation.contains("failed") {
            "HIGH".to_string()
        } else if observation.contains("优化")
            || observation.contains("optimize")
            || observation.contains("改进")
            || observation.contains("improve") {
            "MEDIUM".to_string()
        } else {
            "LOW".to_string()
        }
    }
}
