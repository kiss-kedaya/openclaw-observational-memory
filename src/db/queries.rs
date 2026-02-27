use super::models::{Session, Observation};
use super::DbPool;
use anyhow::Result;
// use rusqlite::OptionalExtension;
use chrono::Utc;

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
        "INSERT INTO sessions (id, created_at, updated_at, message_count, token_count)
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

pub fn list_sessions(pool: &DbPool, limit: i32) -> Result<Vec<Session>> {
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
) -> Result<Observation> {
    let conn = pool.get()?;
    let now = Utc::now();
    let id = uuid::Uuid::new_v4().to_string();
    
    let observation = Observation {
        id: id.clone(),
        session_id: session_id.to_string(),
        content: content.to_string(),
        priority: priority.to_string(),
        created_at: now,
    };
    
    conn.execute(
        "INSERT INTO observations (id, session_id, content, priority, created_at)
         VALUES (?1, ?2, ?3, ?4, ?5)",
        (
            &observation.id,
            &observation.session_id,
            &observation.content,
            &observation.priority,
            observation.created_at.to_rfc3339(),
        ),
    )?;
    
    Ok(observation)
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
