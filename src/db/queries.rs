use super::models::{Session, Observation, Message};
use super::DbPool;
use anyhow::Result;
use chrono::Utc;
use rusqlite::params;

pub fn create_session(pool: &DbPool, session_id: &str) -> Result<Session> {
    let conn = pool.get()?;
    let now = Utc::now();
    
    let session = Session {
        id: session_id.to_string(),
        created_at: now,
        updated_at: now,
        message_count: 0,
        token_count: 0,
    };
    
    conn.execute(
        "INSERT OR IGNORE INTO sessions (id, created_at, updated_at, message_count, token_count)
         VALUES (?1, ?2, ?3, ?4, ?5)",
        (
            &session.id,
            session.created_at.to_rfc3339(),
            session.updated_at.to_rfc3339(),
            session.message_count,
            session.token_count,
        ),
    )?;
    
    Ok(session)
}

/// 估算文本的 token 数量
/// 使用更准确的估算方法：
/// - 英文：按空格分词，每个词约 1.3 tokens
/// - 中文：每个字符约 1.5-2 tokens
/// - 标点和空格：约 1 token
fn estimate_tokens(text: &str) -> i32 {
    let mut token_count = 0;
    
    // 统计中文字符
    let chinese_chars = text.chars().filter(|c| {
        let code = *c as u32;
        (0x4E00..=0x9FFF).contains(&code) || // CJK Unified Ideographs
        (0x3400..=0x4DBF).contains(&code) || // CJK Extension A
        (0x20000..=0x2A6DF).contains(&code)  // CJK Extension B
    }).count();
    
    // 中文字符：每个字符约 2 tokens
    token_count += (chinese_chars as f32 * 2.0) as i32;
    
    // 统计英文单词
    let words: Vec<&str> = text.split_whitespace().collect();
    let english_words = words.iter().filter(|w| {
        w.chars().all(|c| c.is_ascii_alphanumeric() || c.is_ascii_punctuation())
    }).count();
    
    // 英文单词：每个词约 1.3 tokens
    token_count += (english_words as f32 * 1.3) as i32;
    
    // 标点符号和其他字符
    let other_chars = text.len() - chinese_chars - words.join(" ").len();
    token_count += (other_chars as f32 * 0.5) as i32;
    
    // 最小值为 1
    token_count.max(1)
}

pub fn save_messages(
    pool: &DbPool,
    session_id: &str,
    messages: &[Message],
) -> Result<()> {
    let conn = pool.get()?;
    
    for msg in messages {
        conn.execute(
            "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?1, ?2, ?3, ?4)",
            params![session_id, msg.role, msg.content, msg.timestamp],
        )?;
    }
    
    // 更新会话的 message_count 和 token_count
    let message_count = messages.len() as i32;
    let token_count: i32 = messages.iter()
        .map(|m| estimate_tokens(&m.content))
        .sum();
    
    conn.execute(
        "UPDATE sessions SET message_count = message_count + ?1, token_count = token_count + ?2, updated_at = ?3 WHERE id = ?4",
        params![message_count, token_count, Utc::now().to_rfc3339(), session_id],
    )?;
    
    Ok(())
}

pub fn get_session(pool: &DbPool, session_id: &str) -> Result<Option<Session>> {
    let conn = pool.get()?;
    
    let mut stmt = conn.prepare(
        "SELECT id, created_at, updated_at, message_count, token_count
         FROM sessions WHERE id = ?1"
    )?;
    
    let session = stmt.query_row([session_id], |row| {
        Ok(Session {
            id: row.get(0)?,
            created_at: row.get::<_, String>(1)?.parse().unwrap(),
            updated_at: row.get::<_, String>(2)?.parse().unwrap(),
            message_count: row.get(3)?,
            token_count: row.get(4)?,
        })
    }).ok();
    
    Ok(session)
}

pub fn list_sessions(pool: &DbPool, limit: usize) -> Result<Vec<Session>> {
    let conn = pool.get()?;
    
    let mut stmt = conn.prepare(
        "SELECT id, created_at, updated_at, message_count, token_count
         FROM sessions ORDER BY updated_at DESC LIMIT ?1"
    )?;
    
    let sessions = stmt.query_map([limit], |row| {
        Ok(Session {
            id: row.get(0)?,
            created_at: row.get::<_, String>(1)?.parse().unwrap(),
            updated_at: row.get::<_, String>(2)?.parse().unwrap(),
            message_count: row.get(3)?,
            token_count: row.get(4)?,
        })
    })?
    .collect::<Result<Vec<_>, _>>()?;
    
    Ok(sessions)
}

pub fn create_observation(
    pool: &DbPool,
    session_id: &str,
    content: &str,
    priority: &str,
) -> Result<()> {
    let conn = pool.get()?;
    let id = uuid::Uuid::new_v4().to_string();
    let now = Utc::now();
    
    conn.execute(
        "INSERT INTO observations (id, session_id, content, priority, created_at)
         VALUES (?1, ?2, ?3, ?4, ?5)",
        (
            id,
            session_id,
            content,
            priority,
            now.to_rfc3339(),
        ),
    )?;
    
    Ok(())
}

pub fn get_observations(pool: &DbPool, session_id: &str) -> Result<Vec<Observation>> {
    let conn = pool.get()?;
    
    let mut stmt = conn.prepare(
        "SELECT id, session_id, content, priority, created_at, access_count, last_accessed_at, merged_from
         FROM observations WHERE session_id = ?1 ORDER BY created_at DESC"
    )?;
    
    let observations = stmt.query_map([session_id], |row| {
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

pub fn search_full_text(
    pool: &DbPool,
    query: &str,
) -> Result<Vec<Observation>> {
    let conn = pool.get()?;
    
    let mut stmt = conn.prepare(
        "SELECT id, session_id, content, priority, created_at, access_count, last_accessed_at, merged_from
         FROM observations 
         WHERE content LIKE ?1 
         ORDER BY created_at DESC 
         LIMIT 50"
    )?;
    
    let pattern = format!("%{}%", query);
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
    
    Ok(observations)
}
