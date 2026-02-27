use crate::db::{DbPool, models::Observation};
use anyhow::Result;
use chrono::{DateTime, Utc, Duration};

/// 记忆整合：合并相似观察
pub async fn consolidate_memories(
    pool: &DbPool,
    similarity_threshold: f32,
) -> Result<i32> {
    use crate::memory::deduplication::search_similar_observations;
    
    let observations = get_all_observations(pool).await?;
    let mut merged_count = 0;
    
    for obs in &observations {
        let similar = search_similar_observations(pool, &obs.content, similarity_threshold).await?;
        
        if similar.len() > 1 {
            // 合并相似观察
            merge_similar_observations(pool, &similar).await?;
            merged_count += similar.len() as i32 - 1;
        }
    }
    
    Ok(merged_count)
}

/// 获取所有观察
async fn get_all_observations(pool: &DbPool) -> Result<Vec<Observation>> {
    let conn = pool.get()?;
    
    let mut stmt = conn.prepare(
        "SELECT id, session_id, content, priority, created_at, access_count, last_accessed_at, merged_from
         FROM observations 
         ORDER BY created_at DESC"
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

/// 合并相似观察
async fn merge_similar_observations(
    pool: &DbPool,
    observations: &[Observation],
) -> Result<()> {
    if observations.is_empty() {
        return Ok(());
    }
    
    let conn = pool.get()?;
    let target_id = &observations[0].id;
    
    // 合并其他观察到第一个
    for obs in &observations[1..] {
        conn.execute(
            "UPDATE observations 
             SET merged_from = json_insert(merged_from, '$[#]', ?1)
             WHERE id = ?2",
            (&obs.id, target_id),
        )?;
        
        // 删除被合并的观察
        conn.execute(
            "DELETE FROM observations WHERE id = ?1",
            [&obs.id],
        )?;
    }
    
    Ok(())
}

/// 归档低优先级记忆
pub async fn archive_low_priority_memories(
    pool: &DbPool,
    days_threshold: i64,
    access_threshold: i32,
) -> Result<i32> {
    let conn = pool.get()?;
    let cutoff_date = (Utc::now() - Duration::days(days_threshold)).to_rfc3339();
    
    // 查找需要归档的观察
    let mut stmt = conn.prepare(
        "SELECT id, session_id, content, priority, created_at, access_count, last_accessed_at, merged_from
         FROM observations 
         WHERE created_at < ?1 
           AND access_count < ?2 
           AND priority = 'LOW'"
    )?;
    
    let to_archive = stmt.query_map((cutoff_date, access_threshold), |row| {
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
    
    let archived_count = to_archive.len() as i32;
    
    // 移动到归档表
    for obs in to_archive {
        archive_observation(pool, &obs).await?;
        
        // 从主表删除
        conn.execute(
            "DELETE FROM observations WHERE id = ?1",
            [&obs.id],
        )?;
    }
    
    Ok(archived_count)
}

/// 归档单个观察
async fn archive_observation(
    pool: &DbPool,
    obs: &Observation,
) -> Result<()> {
    let conn = pool.get()?;
    
    conn.execute(
        "INSERT INTO archives (id, session_id, content, priority, created_at, archived_at)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
        (
            &obs.id,
            &obs.session_id,
            &obs.content,
            &obs.priority,
            obs.created_at.to_rfc3339(),
            Utc::now().to_rfc3339(),
        ),
    )?;
    
    Ok(())
}

/// 生成周摘要
pub async fn generate_weekly_summary(
    pool: &DbPool,
    week_start: DateTime<Utc>,
) -> Result<String> {
    let conn = pool.get()?;
    let week_end = week_start + Duration::days(7);
    
    // 获取本周的观察
    let mut stmt = conn.prepare(
        "SELECT content, priority 
         FROM observations 
         WHERE created_at >= ?1 AND created_at < ?2
         ORDER BY priority DESC, created_at DESC"
    )?;
    
    let observations = stmt.query_map(
        (week_start.to_rfc3339(), week_end.to_rfc3339()),
        |row| {
            Ok((
                row.get::<_, String>(0)?,
                row.get::<_, String>(1)?,
            ))
        }
    )?
    .collect::<Result<Vec<_>, _>>()?;
    
    // 生成摘要
    let mut summary = format!("周摘要 ({} - {})\n\n", 
        week_start.format("%Y-%m-%d"),
        week_end.format("%Y-%m-%d")
    );
    
    // 按优先级分组
    let high_priority: Vec<_> = observations.iter()
        .filter(|(_, p)| p == "HIGH")
        .collect();
    let medium_priority: Vec<_> = observations.iter()
        .filter(|(_, p)| p == "MEDIUM")
        .collect();
    let low_priority: Vec<_> = observations.iter()
        .filter(|(_, p)| p == "LOW")
        .collect();
    
    summary.push_str(&format!("高优先级事项 ({}):\n", high_priority.len()));
    for (content, _) in high_priority.iter().take(10) {
        summary.push_str(&format!("- {}\n", content.chars().take(100).collect::<String>()));
    }
    
    summary.push_str(&format!("\n中优先级事项 ({}):\n", medium_priority.len()));
    for (content, _) in medium_priority.iter().take(5) {
        summary.push_str(&format!("- {}\n", content.chars().take(100).collect::<String>()));
    }
    
    summary.push_str(&format!("\n总计: {} 条观察\n", observations.len()));
    
    Ok(summary)
}

/// 保存摘要
pub async fn save_summary(
    pool: &DbPool,
    summary: &str,
    period_start: DateTime<Utc>,
    period_end: DateTime<Utc>,
) -> Result<()> {
    let conn = pool.get()?;
    let id = uuid::Uuid::new_v4().to_string();
    
    conn.execute(
        "INSERT INTO summaries (id, content, period_start, period_end, created_at)
         VALUES (?1, ?2, ?3, ?4, ?5)",
        (
            id,
            summary,
            period_start.to_rfc3339(),
            period_end.to_rfc3339(),
            Utc::now().to_rfc3339(),
        ),
    )?;
    
    Ok(())
}

/// 自动整合任务（每周运行）
pub async fn auto_consolidation_task(pool: &DbPool) -> Result<()> {
    // 1. 合并相似观察（阈值 0.85）
    let merged = consolidate_memories(pool, 0.85).await?;
    println!("Merged {} similar observations", merged);
    
    // 2. 归档低优先级记忆（30 天 + 访问次数 < 2）
    let archived = archive_low_priority_memories(pool, 30, 2).await?;
    println!("Archived {} low-priority observations", archived);
    
    // 3. 生成周摘要
    let week_start = Utc::now() - Duration::days(7);
    let summary = generate_weekly_summary(pool, week_start).await?;
    save_summary(pool, &summary, week_start, Utc::now()).await?;
    println!("Generated weekly summary");
    
    Ok(())
}
