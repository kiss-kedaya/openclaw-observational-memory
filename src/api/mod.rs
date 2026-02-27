use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use crate::db::{queries, DbPool};
use crate::db::models::{Session, Message};
use crate::core::{Observer, ToolSuggestionEngine, MemoryOptimizer, VectorSearchEngine};

pub struct AppState {
    pub db: DbPool,
}

#[derive(Debug, Deserialize)]
pub struct CreateSessionRequest {
    pub session_id: String,
    pub messages: Vec<Message>,
}

#[derive(Debug, Serialize)]
pub struct CreateSessionResponse {
    pub session: Session,
    pub observations: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct SearchRequest {
    query: String,
    #[serde(default = "default_threshold")]
    threshold: f32,
}

fn default_threshold() -> f32 {
    0.3
}

pub fn create_router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/api/sessions", get(list_sessions).post(create_session))
        .route("/api/sessions/:id", get(get_session))
        .route("/api/observations/:session_id", get(get_observations))
        .route("/api/search", post(search))
        .route("/api/tools/suggestions", get(tool_suggestions))
        .route("/api/memory/compress", post(compress_memory))
        .route("/api/memory/clusters", get(get_clusters))
        .with_state(state)
}

async fn list_sessions(
    State(state): State<Arc<AppState>>,
) -> Result<Json<Vec<Session>>, StatusCode> {
    queries::list_sessions(&state.db, 50)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

async fn get_session(
    State(state): State<Arc<AppState>>,
    Path(id): Path<String>,
) -> Result<Json<Session>, StatusCode> {
    queries::get_session(&state.db, &id)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
        .map(Json)
        .ok_or(StatusCode::NOT_FOUND)
}

async fn create_session(
    State(state): State<Arc<AppState>>,
    Json(req): Json<CreateSessionRequest>,
) -> Result<Json<CreateSessionResponse>, StatusCode> {
    let session = queries::create_session(&state.db, &req.session_id)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let observations = Observer::extract_observations(&req.messages)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    for obs in &observations {
        let priority = Observer::calculate_priority(obs);
        queries::create_observation(&state.db, &req.session_id, obs, &priority)
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    }
    
    Ok(Json(CreateSessionResponse {
        session,
        observations,
    }))
}

async fn get_observations(
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
) -> Result<Json<Vec<crate::db::models::Observation>>, StatusCode> {
    queries::get_observations(&state.db, &session_id)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

async fn search(
    State(state): State<Arc<AppState>>,
    Json(req): Json<SearchRequest>,
) -> Result<Json<Vec<crate::core::SearchResult>>, StatusCode> {
    let sessions = queries::list_sessions(&state.db, 100)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let mut all_obs = Vec::new();
    for session in sessions {
        let obs = queries::get_observations(&state.db, &session.id)
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
        all_obs.extend(obs);
    }
    
    let engine = VectorSearchEngine::new();
    let results = engine.search(all_obs, &req.query, req.threshold);
    
    Ok(Json(results))
}

async fn tool_suggestions(
    State(state): State<Arc<AppState>>,
) -> Result<Json<Vec<crate::core::ToolSuggestion>>, StatusCode> {
    let engine = ToolSuggestionEngine::new();
    
    let sessions = queries::list_sessions(&state.db, 10)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let mut suggestions = Vec::new();
    for session in sessions {
        let obs = queries::get_observations(&state.db, &session.id)
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
        
        for o in obs {
            suggestions.extend(engine.analyze(&o));
        }
    }
    
    Ok(Json(suggestions))
}

async fn compress_memory(
    State(state): State<Arc<AppState>>,
) -> Result<Json<crate::core::CompressionResult>, StatusCode> {
    let optimizer = MemoryOptimizer::new();
    
    let sessions = queries::list_sessions(&state.db, 100)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let mut all_obs = Vec::new();
    for session in sessions {
        let obs = queries::get_observations(&state.db, &session.id)
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
        all_obs.extend(obs);
    }
    
    let result = optimizer.compress(all_obs);
    Ok(Json(result))
}

async fn get_clusters(
    State(state): State<Arc<AppState>>,
) -> Result<Json<Vec<crate::core::Cluster>>, StatusCode> {
    let optimizer = MemoryOptimizer::new();
    
    let sessions = queries::list_sessions(&state.db, 100)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let mut all_obs = Vec::new();
    for session in sessions {
        let obs = queries::get_observations(&state.db, &session.id)
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
        all_obs.extend(obs);
    }
    
    let clusters = optimizer.cluster_by_topic(all_obs);
    Ok(Json(clusters))
}
