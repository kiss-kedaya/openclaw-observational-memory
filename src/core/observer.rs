use crate::db::models::Message;
use anyhow::Result;

pub struct Observer;

impl Observer {
    pub fn extract_observations(messages: &[Message]) -> Result<Vec<String>> {
        let mut observations = Vec::new();
        
        for msg in messages {
            // Extract from all message types, not just assistant
            let lines: Vec<&str> = msg.content.lines().collect();
            
            for line in lines {
                let trimmed = line.trim();
                
                // Skip empty lines and very short lines
                if trimmed.is_empty() || trimmed.len() < 20 {
                    continue;
                }
                
                // Skip markdown headers and list markers
                if trimmed.starts_with('#') || trimmed.starts_with('-') || trimmed.starts_with('*') {
                    continue;
                }
                
                // Extract meaningful observations
                if Self::is_meaningful(trimmed) {
                    observations.push(trimmed.to_string());
                }
            }
            
            // If no specific observations found, use the whole message as observation
            if observations.is_empty() && msg.content.len() > 20 {
                observations.push(msg.content.clone());
            }
        }
        
        Ok(observations)
    }
    
    fn is_meaningful(text: &str) -> bool {
        // Check if text contains meaningful information
        let keywords = [
            "完成", "实现", "创建", "修复", "优化", "添加", "更新", "删除",
            "completed", "implemented", "created", "fixed", "optimized", "added", "updated", "deleted",
            "安装", "配置", "部署", "测试", "运行", "启动",
            "installed", "configured", "deployed", "tested", "running", "started",
            "问题", "错误", "失败", "成功",
            "issue", "error", "failed", "success",
            "功能", "特性", "模块", "组件",
            "feature", "module", "component"
        ];
        
        keywords.iter().any(|&kw| text.to_lowercase().contains(kw))
    }
    
    pub fn calculate_priority(observation: &str) -> String {
        let obs_lower = observation.to_lowercase();
        
        if obs_lower.contains("错误") 
            || obs_lower.contains("error")
            || obs_lower.contains("失败")
            || obs_lower.contains("failed")
            || obs_lower.contains("紧急")
            || obs_lower.contains("urgent") {
            "HIGH".to_string()
        } else if obs_lower.contains("优化")
            || obs_lower.contains("optimize")
            || obs_lower.contains("改进")
            || obs_lower.contains("improve")
            || obs_lower.contains("重要")
            || obs_lower.contains("important") {
            "MEDIUM".to_string()
        } else {
            "LOW".to_string()
        }
    }
}
