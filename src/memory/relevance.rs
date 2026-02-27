use crate::db::models::Observation;
use chrono::{DateTime, Utc};

/// 计算记忆相关性评分（时间衰减 + 访问频率）
pub fn calculate_relevance_score(obs: &Observation, query_time: DateTime<Utc>) -> f32 {
    // 基础评分（基于优先级）
    let base_score = match obs.priority.as_str() {
        "HIGH" => 1.0,
        "MEDIUM" => 0.6,
        "LOW" => 0.3,
        _ => 0.5,
    };
    
    // 时间衰减（7 天半衰期）
    let age_days = (query_time - obs.created_at).num_days() as f32;
    let decay_factor = 0.5_f32.powf(age_days / 7.0);
    
    // 访问频率加权
    let access_boost = if obs.access_count > 0 {
        (obs.access_count as f32).ln() * 0.1
    } else {
        0.0
    };
    
    // 最终评分
    base_score * decay_factor + access_boost
}

/// 更新观察的访问记录
pub async fn update_access_record(
    pool: &crate::db::DbPool,
    observation_id: &str,
) -> anyhow::Result<()> {
    let conn = pool.get()?;
    let now = Utc::now();
    
    conn.execute(
        "UPDATE observations 
         SET access_count = access_count + 1, 
             last_accessed_at = ?1 
         WHERE id = ?2",
        (now.to_rfc3339(), observation_id),
    )?;
    
    Ok(())
}

/// 获取最相关的观察（基于时间衰减和访问频率）
pub async fn get_relevant_observations(
    pool: &crate::db::DbPool,
    session_id: &str,
    limit: usize,
) -> anyhow::Result<Vec<(Observation, f32)>> {
    use crate::db::queries;
    
    let observations = queries::get_observations(pool, session_id)?;
    let query_time = Utc::now();
    
    let mut scored_observations: Vec<(Observation, f32)> = observations
        .into_iter()
        .map(|obs| {
            let score = calculate_relevance_score(&obs, query_time);
            (obs, score)
        })
        .collect();
    
    // 按评分降序排序
    scored_observations.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
    
    // 限制返回数量
    scored_observations.truncate(limit);
    
    Ok(scored_observations)
}

/// 计算优先级评分
pub fn calculate_priority_score(content: &str) -> f32 {
    let content_lower = content.to_lowercase();
    
    // 高优先级关键词
    let high_priority_keywords = [
        "错误", "error", "失败", "failed", "紧急", "urgent",
        "重要", "important", "关键", "critical"
    ];
    
    // 中优先级关键词
    let medium_priority_keywords = [
        "优化", "optimize", "改进", "improve", "建议", "suggest",
        "注意", "note", "警告", "warning"
    ];
    
    // 检查高优先级
    if high_priority_keywords.iter().any(|&kw| content_lower.contains(kw)) {
        return 1.0;
    }
    
    // 检查中优先级
    if medium_priority_keywords.iter().any(|&kw| content_lower.contains(kw)) {
        return 0.6;
    }
    
    // 默认低优先级
    0.3
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Duration;
    
    #[test]
    fn test_time_decay() {
        let now = Utc::now();
        let obs = Observation {
            id: "test".to_string(),
            session_id: "test".to_string(),
            content: "test".to_string(),
            priority: "HIGH".to_string(),
            created_at: now - Duration::days(7),
            access_count: 0,
            last_accessed_at: None,
            merged_from: "[]".to_string(),
        };
        
        let score = calculate_relevance_score(&obs, now);
        
        // 7 天后，HIGH 优先级应该衰减到 0.5
        assert!((score - 0.5).abs() < 0.01);
    }
    
    #[test]
    fn test_access_boost() {
        let now = Utc::now();
        let obs = Observation {
            id: "test".to_string(),
            session_id: "test".to_string(),
            content: "test".to_string(),
            priority: "LOW".to_string(),
            created_at: now,
            access_count: 10,
            last_accessed_at: Some(now),
            merged_from: "[]".to_string(),
        };
        
        let score = calculate_relevance_score(&obs, now);
        
        // LOW 优先级 (0.3) + 访问加权 (ln(10) * 0.1 ≈ 0.23)
        assert!(score > 0.5);
    }
}
