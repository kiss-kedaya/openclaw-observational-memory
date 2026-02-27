use axum::{
    extract::State,
    response::Json,
    routing::get,
    Router,
};
use serde::Serialize;
use std::sync::Arc;
use sysinfo::System;

use crate::api::AppState;

#[derive(Debug, Serialize)]
pub struct PerformanceMetrics {
    pub cpu_usage: f32,
    pub memory_usage: u64,
    pub memory_total: u64,
    pub memory_percent: f32,
    pub db_size: u64,
    pub uptime: u64,
    pub process_count: usize,
}

#[derive(Debug, Serialize)]
pub struct HealthStatus {
    pub status: String,
    pub database: bool,
    pub memory: bool,
    pub disk: bool,
}

pub fn create_monitoring_router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/api/monitoring/metrics", get(get_metrics))
        .route("/api/monitoring/health", get(get_health))
        .with_state(state)
}

async fn get_metrics(
    State(_state): State<Arc<AppState>>,
) -> Json<PerformanceMetrics> {
    let mut sys = System::new_all();
    sys.refresh_all();
    
    let pid = sysinfo::get_current_pid().ok();
    let process = pid.and_then(|p| sys.process(p));
    
    let cpu_usage = process.map(|p| p.cpu_usage()).unwrap_or(0.0);
    let memory_usage = process.map(|p| p.memory()).unwrap_or(0);
    let memory_total = sys.total_memory();
    let memory_percent = (memory_usage as f32 / memory_total as f32) * 100.0;
    
    // 获取数据库文件大小
    let db_size = std::fs::metadata("memory.db")
        .map(|m| m.len())
        .unwrap_or(0);
    
    // 获取运行时间（秒）
    let uptime = process.map(|p| p.run_time()).unwrap_or(0);
    
    Json(PerformanceMetrics {
        cpu_usage,
        memory_usage,
        memory_total,
        memory_percent,
        db_size,
        uptime,
        process_count: sys.processes().len(),
    })
}

async fn get_health(
    State(state): State<Arc<AppState>>,
) -> Json<HealthStatus> {
    // 检查数据库连接
    let db_ok = state.db.get().is_ok();
    
    // 检查内存使用
    let mut sys = System::new_all();
    sys.refresh_all();
    let memory_ok = sys.available_memory() > 100 * 1024 * 1024; // > 100MB
    
    // 检查磁盘空间
    let disk_ok = std::fs::metadata(".")
        .map(|_| true)
        .unwrap_or(false);
    
    let status = if db_ok && memory_ok && disk_ok {
        "healthy"
    } else {
        "unhealthy"
    };
    
    Json(HealthStatus {
        status: status.to_string(),
        database: db_ok,
        memory: memory_ok,
        disk: disk_ok,
    })
}

