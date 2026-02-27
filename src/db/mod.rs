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
    // 设置 UTF-8 编码
    conn.execute("PRAGMA encoding = 'UTF-8'", [])?;
    
    conn.execute(
        "CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            message_count INTEGER NOT NULL,
            token_count INTEGER NOT NULL,
            tags TEXT DEFAULT '[]',
            group_name TEXT,
            archived INTEGER DEFAULT 0
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
            tags TEXT DEFAULT '[]',
            linked_observations TEXT DEFAULT '[]',
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_observations_session 
         ON observations(session_id)",
        [],
    )?;
    
    // 添加新字段到现有表（如果不存在）
    let _ = conn.execute("ALTER TABLE sessions ADD COLUMN tags TEXT DEFAULT '[]'", []);
    let _ = conn.execute("ALTER TABLE sessions ADD COLUMN group_name TEXT", []);
    let _ = conn.execute("ALTER TABLE sessions ADD COLUMN archived INTEGER DEFAULT 0", []);
    let _ = conn.execute("ALTER TABLE observations ADD COLUMN tags TEXT DEFAULT '[]'", []);
    let _ = conn.execute("ALTER TABLE observations ADD COLUMN linked_observations TEXT DEFAULT '[]'", []);
    
    // 创建 messages 表
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_session_id 
         ON messages(session_id)",
        [],
    )?;
    
    Ok(())
}

