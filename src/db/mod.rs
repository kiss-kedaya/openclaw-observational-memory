pub mod models;
pub mod queries;

use anyhow::Result;
use r2d2::Pool;
use r2d2_sqlite::SqliteConnectionManager;
use rusqlite::Connection;
use std::path::Path;

pub type DbPool = Pool<SqliteConnectionManager>;

pub fn init_db<P: AsRef<Path>>(db_path: P) -> Result<DbPool> {
    let manager = SqliteConnectionManager::file(db_path);
    let pool = Pool::new(manager)?;
    
    let conn = pool.get()?;
    create_tables(&conn)?;
    
    Ok(pool)
}

fn create_tables(conn: &Connection) -> Result<()> {
    conn.execute(
        "CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            message_count INTEGER NOT NULL,
            token_count INTEGER NOT NULL
        )",
        [],
    )?;
    
    conn.execute(
        "CREATE TABLE IF NOT EXISTS observations (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            content TEXT NOT NULL,
            priority TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_observations_session 
         ON observations(session_id)",
        [],
    )?;
    
    Ok(())
}
