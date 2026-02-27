use crate::db::{DbPool, models::Observation};
use anyhow::Result;
use chrono::Utc;

/// 语义去重：基于向量相似度合并重复观察
pub async fn deduplicate_observation(
    pool: &DbPool,
    new_obs: &Observation,
    threshold: f32,
) -> Result<bool> {
    // 搜索相似观察（阈值 0.95）
    let similar = search_similar_observations(pool, &new_obs.content, threshold).await?;
    
    if !similar.is_empty() {
        // 合并观察
        merge_observations(pool, &similar[0].id, new_obs).await?;
        return Ok(false); // 已合并，不需要插入新记录
    }
    
    Ok(true) // 无重复，可以插入
}

/// 搜索相似观察
async fn search_similar_observations(
    pool: &DbPool,
    content: &str,
    threshold: f32,
) -> Result<Vec<Observation>> {
    let conn = pool.get()?;
    
    // 使用 LIKE 进行简单的文本相似度检测
    // TODO: 实现真正的向量相似度搜索
    let mut stmt = conn.prepare(
        "SELECT id, session_id, content, priority, created_at, access_count, last_accessed_at, merged_from
         FROM observations 
         WHERE content LIKE ?1 
         LIMIT 10"
    )?;
    
    let pattern = format!("%{}%", content);
    let observations = stmt.query_map([pattern], |row| {
        Ok(Observation {
            id: row.get(0)?,
            session_id: row.get(1)?,
            content: row.get(2)?,
            priority: row.get(3)?,
            created_at: row.get::<_, String>(4)?.parse().unwrap(),
            access_count: row.get(5).unwrap_or(0),
            last_accessed_at: row.get::<_, Option<String>>(6)?
                .and_then(|s| s.parse().ok()),
            merged_from: row.get(7).unwrap_or_else(|_| "[]".to_string()),
        })
    })?
    .collect::<Result<Vec<_>, _>>()?;
    
    // 计算相似度并过滤
    let similar: Vec<Observation> = observations
        .into_iter()
        .filter(|obs| calculate_similarity(&obs.content, content) >= threshold)
        .collect();
    
    Ok(similar)
}

/// 计算文本相似度（简单实现）
fn calculate_similarity(text1: &str, text2: &str) -> f32 {
    let words1: std::collections::HashSet<&str> = text1.split_whitespace().collect();
    let words2: std::collections::HashSet<&str> = text2.split_whitespace().collect();
    
    let intersection = words1.intersection(&words2).count();
    let union = words1.union(&words2).count();
    
    if union == 0 {
        return 0.0;
    }
    
    intersection as f32 / union as f32
}

/// 合并观察
async fn merge_observations(
    pool: &DbPool,
    target_id: &str,
    source: &Observation,
) -> Result<()> {
    let conn = pool.get()?;
    
    // 更新 merged_from 字段
    let mut merged_from: Vec<String> = serde_json::from_str(
        &conn.query_row(
            "SELECT merged_from FROM observations WHERE id = ?1",
            [target_id],
            |row| row.get(0)
        ).unwrap_or_else(|_| "[]".to_string())
    ).unwrap_or_default();
    
    merged_from.push(source.id.clone());
    
    conn.execute(
        "UPDATE observations SET merged_from = ?1, access_count = access_count + 1 WHERE id = ?2",
        (serde_json::to_string(&merged_from)?, target_id),
    )?;
    
    Ok(())
}

/// 冲突检测：识别矛盾信息
pub async fn detect_conflicts(
    pool: &DbPool,
    new_obs: &Observation,
) -> Result<Vec<Conflict>> {
    let related = search_related_observations(pool, new_obs).await?;
    let mut conflicts = Vec::new();
    
    for old_obs in related {
        if is_contradictory(&old_obs, &new_obs) {
            conflicts.push(Conflict {
                id: uuid::Uuid::new_v4().to_string(),
                old_id: old_obs.id.clone(),
                new_id: new_obs.id.clone(),
                confidence: calculate_conflict_score(&old_obs, &new_obs),
                resolved: false,
                created_at: Utc::now(),
            });
        }
    }
    
    Ok(conflicts)
}

/// 搜索相关观察
async fn search_related_observations(
    pool: &DbPool,
    obs: &Observation,
) -> Result<Vec<Observation>> {
    // 搜索同一会话或相似内容的观察
    search_similar_observations(pool, &obs.content, 0.7).await
}

/// 判断是否矛盾
fn is_contradictory(old_obs: &Observation, new_obs: &Observation) -> bool {
    // 简单实现：检测否定词
    let negation_words = ["不", "没", "非", "无", "not", "no", "never"];
    
    let old_has_negation = negation_words.iter().any(|&w| old_obs.content.contains(w));
    let new_has_negation = negation_words.iter().any(|&w| new_obs.content.contains(w));
    
    // 如果一个有否定词，一个没有，且内容相似，则可能矛盾
    old_has_negation != new_has_negation && calculate_similarity(&old_obs.content, &new_obs.content) > 0.6
}

/// 计算冲突评分
fn calculate_conflict_score(old_obs: &Observation, new_obs: &Observation) -> f32 {
    let similarity = calculate_similarity(&old_obs.content, &new_obs.content);
    let time_diff = (new_obs.created_at - old_obs.created_at).num_days() as f32;
    
    // 相似度高且时间接近，冲突可能性更大
    similarity * (1.0 / (1.0 + time_diff / 30.0))
}

/// 冲突结构
#[derive(Debug, Clone)]
pub struct Conflict {
    pub id: String,
    pub old_id: String,
    pub new_id: String,
    pub confidence: f32,
    pub resolved: bool,
    pub created_at: chrono::DateTime<Utc>,
}
