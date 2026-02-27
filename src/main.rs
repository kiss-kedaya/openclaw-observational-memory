mod api;
mod core;
mod db;

use anyhow::Result;
use std::sync::Arc;
use tower_http::cors::CorsLayer;
use tower_http::services::ServeDir;
use tracing_subscriber;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();
    
    // Initialize database
    let db_pool = db::init_db("memory.db")?;
    
    // Create app state
    let state = Arc::new(api::AppState { db: db_pool });
    
    // Create router
    let app = api::create_router(state)
        .nest_service("/", ServeDir::new("frontend/dist"))
        .layer(CorsLayer::permissive());
    
    // Start server
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await?;
    tracing::info!("Server running on http://127.0.0.1:3000");
    
    axum::serve(listener, app).await?;
    
    Ok(())
}
