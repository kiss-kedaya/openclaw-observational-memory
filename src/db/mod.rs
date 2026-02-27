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
    
    // Phase 1: 添加去重和冲突检测字段
    let _ = conn.execute("ALTER TABLE observations ADD COLUMN access_count INTEGER DEFAULT 0", []);
    let _ = conn.execute("ALTER TABLE observations ADD COLUMN last_accessed_at TEXT", []);
    let _ = conn.execute("ALTER TABLE observations ADD COLUMN merged_from TEXT DEFAULT '[]'", []);
    
    // 创建 conflicts 表
    conn.execute(
        "CREATE TABLE IF NOT EXISTS conflicts (
            id TEXT PRIMARY KEY,
            old_id TEXT NOT NULL,
            new_id TEXT NOT NULL,
            confidence REAL NOT NULL,
            resolved INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (old_id) REFERENCES observations(id),
            FOREIGN KEY (new_id) REFERENCES observations(id)
        )",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_conflicts_resolved 
         ON conflicts(resolved)",
        [],
    )?;
    
    // Phase 3: 创建 patterns 表
    conn.execute(
        "CREATE TABLE IF NOT EXISTS patterns (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            description TEXT NOT NULL,
            confidence REAL NOT NULL,
            occurrences INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_patterns_type 
         ON patterns(type)",
        [],
    )?;
    
    // Phase 4: 创建 archives 和 summaries 表
    conn.execute(
        "CREATE TABLE IF NOT EXISTS archives (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            content TEXT NOT NULL,
            priority TEXT NOT NULL,
            created_at TEXT NOT NULL,
            archived_at TEXT NOT NULL
        )",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_archives_archived_at 
         ON archives(archived_at)",
        [],
    )?;
    
    conn.execute(
        "CREATE TABLE IF NOT EXISTS summaries (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            created_at TEXT NOT NULL
        )",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_summaries_period 
         ON summaries(period_start, period_end)",
        [],
    )?;
    
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
    
    // v2.1.0: 性能优化索引
    
    // 1. sessions 表索引
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sessions_updated_at 
         ON sessions(updated_at DESC)",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sessions_archived 
         ON sessions(archived)",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sessions_group 
         ON sessions(group_name)",
        [],
    )?;
    
    // 2. observations 表索引
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_observations_created_at 
         ON observations(created_at DESC)",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_observations_priority 
         ON observations(priority)",
        [],
    )?;
    
    // 3. messages 表索引
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
         ON messages(timestamp DESC)",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_role 
         ON messages(role)",
        [],
    )?;
    
    // 4. 复合索引（常用查询组合）
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_observations_session_created 
         ON observations(session_id, created_at DESC)",
        [],
    )?;
    
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_session_timestamp 
         ON messages(session_id, timestamp DESC)",
        [],
    )?;
    
    Ok(())
}





