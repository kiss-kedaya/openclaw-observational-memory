use crate::db::{DbPool, models::Observation};
use chrono::Timelike;
use anyhow::Result;
use std::collections::HashMap;

/// 模式类型
#[derive(Debug, Clone)]
pub enum PatternType {
    Recurring,    // 重复性任务
    Temporal,     // 时序模式
    Association,  // 关联关系
}

/// 模式结构
#[derive(Debug, Clone)]
pub struct Pattern {
    pub id: String,
    pub pattern_type: PatternType,
    pub description: String,
    pub confidence: f32,
    pub occurrences: i32,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

/// K-means 聚类分析
pub async fn cluster_observations(
    pool: &DbPool,
    k: usize,
) -> Result<Vec<Vec<Observation>>> {
    use crate::db::queries;
    
    // 获取所有观察
    let all_observations = get_all_observations(pool).await?;
    
    if all_observations.is_empty() {
        return Ok(Vec::new());
    }
    
    // 简单的 K-means 实现（基于内容长度和关键词）
    let mut clusters: Vec<Vec<Observation>> = vec![Vec::new(); k];
    
    for obs in all_observations {
        // 简单的聚类：基于内容长度
        let cluster_idx = (obs.content.len() % k).min(k - 1);
        clusters[cluster_idx].push(obs);
    }
    
    Ok(clusters)
}

/// 获取所有观察
async fn get_all_observations(pool: &DbPool) -> Result<Vec<Observation>> {
    let conn = pool.get()?;
    
    let mut stmt = conn.prepare(
        "SELECT id, session_id, content, priority, created_at, access_count, last_accessed_at, merged_from
         FROM observations 
         ORDER BY created_at DESC 
         LIMIT 1000"
    )?;
    
    let observations = stmt.query_map([], |row| {
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
    
    Ok(observations)
}

/// 时序模式分析
pub async fn analyze_temporal_patterns(
    pool: &DbPool,
) -> Result<Vec<Pattern>> {
    let observations = get_all_observations(pool).await?;
    let mut patterns = Vec::new();
    
    // 按小时分组
    let mut hourly_counts: HashMap<u32, i32> = HashMap::new();
    
    for obs in &observations {
        let hour = obs.created_at.hour();
        *hourly_counts.entry(hour).or_insert(0) += 1;
    }
    
    // 找出高频时段
    for (hour, count) in hourly_counts {
        if count > 5 {
            patterns.push(Pattern {
                id: uuid::Uuid::new_v4().to_string(),
                pattern_type: PatternType::Temporal,
                description: format!("高频时段：{}:00-{}:00，出现 {} 次", hour, hour + 1, count),
                confidence: (count as f32 / observations.len() as f32).min(1.0),
                occurrences: count,
                created_at: chrono::Utc::now(),
            });
        }
    }
    
    Ok(patterns)
}

/// 关联规则挖掘（简化版 Apriori）
pub async fn mine_association_rules(
    pool: &DbPool,
    min_support: f32,
) -> Result<Vec<Pattern>> {
    let observations = get_all_observations(pool).await?;
    let mut patterns = Vec::new();
    
    // 提取关键词
    let mut keyword_pairs: HashMap<(String, String), i32> = HashMap::new();
    
    for obs in &observations {
        let words: Vec<&str> = obs.content.split_whitespace().collect();
        
        // 找出共现的关键词对
        for i in 0..words.len() {
            for j in (i + 1)..words.len() {
                if words[i].len() > 3 && words[j].len() > 3 {
                    let pair = if words[i] < words[j] {
                        (words[i].to_string(), words[j].to_string())
                    } else {
                        (words[j].to_string(), words[i].to_string())
                    };
                    *keyword_pairs.entry(pair).or_insert(0) += 1;
                }
            }
        }
    }
    
    // 找出高频关联
    let total_obs = observations.len() as f32;
    for ((word1, word2), count) in keyword_pairs {
        let support = count as f32 / total_obs;
        if support >= min_support {
            patterns.push(Pattern {
                id: uuid::Uuid::new_v4().to_string(),
                pattern_type: PatternType::Association,
                description: format!("关联：{} <-> {}，支持度 {:.2}", word1, word2, support),
                confidence: support,
                occurrences: count,
                created_at: chrono::Utc::now(),
            });
        }
    }
    
    Ok(patterns)
}

/// 识别重复性任务
pub async fn identify_recurring_tasks(
    pool: &DbPool,
) -> Result<Vec<Pattern>> {
    let observations = get_all_observations(pool).await?;
    let mut patterns = Vec::new();
    
    // 按内容相似度分组
    let mut content_groups: HashMap<String, Vec<Observation>> = HashMap::new();
    
    for obs in observations {
        // 提取前 50 个字符作为特征
        let key = obs.content.chars().take(50).collect::<String>();
        content_groups.entry(key).or_insert_with(Vec::new).push(obs);
    }
    
    // 找出重复出现的任务
    for (key, group) in content_groups {
        if group.len() > 2 {
            patterns.push(Pattern {
                id: uuid::Uuid::new_v4().to_string(),
                pattern_type: PatternType::Recurring,
                description: format!("重复任务：{}... 出现 {} 次", key, group.len()),
                confidence: (group.len() as f32 / 10.0).min(1.0),
                occurrences: group.len() as i32,
                created_at: chrono::Utc::now(),
            });
        }
    }
    
    Ok(patterns)
}

/// 保存模式到数据库
pub async fn save_pattern(
    pool: &DbPool,
    pattern: &Pattern,
) -> Result<()> {
    let conn = pool.get()?;
    
    let pattern_type_str = match pattern.pattern_type {
        PatternType::Recurring => "recurring",
        PatternType::Temporal => "temporal",
        PatternType::Association => "association",
    };
    
    conn.execute(
        "INSERT INTO patterns (id, type, description, confidence, occurrences, created_at)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
        (
            &pattern.id,
            pattern_type_str,
            &pattern.description,
            pattern.confidence,
            pattern.occurrences,
            pattern.created_at.to_rfc3339(),
        ),
    )?;
    
    Ok(())
}


