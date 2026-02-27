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
        .map(|m| (m.content.len() / 4) as i32)
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
        "SELECT id, session_id, content, priority, created_at
         FROM observations WHERE session_id = ?1 ORDER BY created_at DESC"
    )?;
    
    let observations = stmt.query_map([session_id], |row| {
        Ok(Observation {
            id: row.get(0)?,
            session_id: row.get(1)?,
            content: row.get(2)?,
            priority: row.get(3)?,
            created_at: row.get::<_, String>(4)?.parse().unwrap(),
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
        "SELECT id, session_id, content, priority, created_at
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
        })
    })?
    .collect::<Result<Vec<_>, _>>()?;
    
    Ok(observations)
}
