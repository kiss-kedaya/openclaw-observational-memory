use axum::{
    extract::State,
    http::StatusCode,
    response::Json,
    routing::post,
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use crate::core::SearchResult;

#[derive(Debug, Deserialize)]
pub struct SearchRequest {
    pub query: String,
    #[serde(default = "default_threshold")]
    pub threshold: f32,
    #[serde(default = "default_top_k")]
    pub top_k: usize,
}

fn default_threshold() -> f32 {
    0.3
}

fn default_top_k() -> usize {
    10
}

#[derive(Debug, Serialize)]
pub struct SearchResponse {
    pub results: Vec<SearchResult>,
    pub total: usize,
}

pub fn create_search_router(state: Arc<crate::api::AppState>) -> Router {
    Router::new()
        .route("/api/search", post(search))
        .with_state(state)
}

async fn search(
    State(state): State<Arc<crate::api::AppState>>,
    Json(req): Json<SearchRequest>,
) -> Result<Json<SearchResponse>, StatusCode> {
    // TODO: Use actual vector search engine
    // For now, return empty results
    let results = vec![];
    
    Ok(Json(SearchResponse {
        total: results.len(),
        results,
    }))
}
