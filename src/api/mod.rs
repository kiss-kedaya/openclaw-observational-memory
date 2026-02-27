use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::Json,
    routing::{get, post, delete},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use crate::db::{queries, DbPool};
use crate::db::models::{Session, Message};
use crate::core::{Observer, ToolSuggestionEngine, MemoryOptimizer, VectorSearchEngine, AISearchEngine, SummaryGenerator, KnowledgeGraphBuilder};

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
    0.2  // 降低阈值以提高搜索召回率
}

#[derive(Debug, Deserialize)]
pub struct AddTagRequest {
    pub tag: String,
}

#[derive(Debug, Deserialize)]
pub struct RemoveTagRequest {
    pub tag: String,
}

#[derive(Debug, Deserialize)]
pub struct SetGroupRequest {
    pub group: String,
}

pub fn create_router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/api/sessions", get(list_sessions).post(create_session))
        .route("/api/sessions/:id", get(get_session))
        .route("/api/sessions/:id/tags", post(add_tag).delete(remove_tag))
        .route("/api/sessions/:id/group", post(set_group))
        .route("/api/sessions/:id/archive", post(archive_session))
        .route("/api/sessions/:id/unarchive", post(unarchive_session))
        .route("/api/observations/:session_id", get(get_observations))
        .route("/api/search", post(search))
        .route("/api/tools/suggestions", get(tool_suggestions))
        .route("/api/memory/compress", post(compress_memory))
        .route("/api/memory/clusters", get(get_clusters))
        .route("/api/ai/search", post(ai_search))
        .route("/api/ai/summary/:session_id", get(generate_summary))
        .route("/api/ai/suggestions", post(get_suggestions))
        .route("/api/knowledge/graph", get(get_knowledge_graph))
        .route("/api/knowledge/related/:entity_id", get(get_related_entities))
        
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
    
    // 保存消息
    queries::save_messages(&state.db, &req.session_id, &req.messages)
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

async fn add_tag(
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
    Json(req): Json<AddTagRequest>,
) -> Result<Json<()>, StatusCode> {
    let conn = state.db.get().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let current_tags: String = conn
        .query_row(
            "SELECT COALESCE(tags, ''[]'') FROM sessions WHERE id = ?1",
            [&session_id],
            |row| row.get(0),
        )
        .unwrap_or_else(|_| "[]".to_string());
    
    let mut tags: Vec<String> = serde_json::from_str(&current_tags).unwrap_or_default();
    
    if !tags.contains(&req.tag) {
        tags.push(req.tag);
    }
    
    conn.execute(
        "UPDATE sessions SET tags = ?1 WHERE id = ?2",
        [serde_json::to_string(&tags).unwrap(), session_id],
    )
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    Ok(Json(()))
}

async fn remove_tag(
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
    Json(req): Json<RemoveTagRequest>,
) -> Result<Json<()>, StatusCode> {
    let conn = state.db.get().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let current_tags: String = conn
        .query_row(
            "SELECT COALESCE(tags, ''[]'') FROM sessions WHERE id = ?1",
            [&session_id],
            |row| row.get(0),
        )
        .unwrap_or_else(|_| "[]".to_string());
    
    let mut tags: Vec<String> = serde_json::from_str(&current_tags).unwrap_or_default();
    tags.retain(|t| t != &req.tag);
    
    conn.execute(
        "UPDATE sessions SET tags = ?1 WHERE id = ?2",
        [serde_json::to_string(&tags).unwrap(), session_id],
    )
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    Ok(Json(()))
}

async fn set_group(
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
    Json(req): Json<SetGroupRequest>,
) -> Result<Json<()>, StatusCode> {
    let conn = state.db.get().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    conn.execute(
        "UPDATE sessions SET group_name = ?1 WHERE id = ?2",
        [req.group, session_id],
    )
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    Ok(Json(()))
}

async fn archive_session(
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
) -> Result<Json<()>, StatusCode> {
    let conn = state.db.get().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    conn.execute(
        "UPDATE sessions SET archived = 1 WHERE id = ?1",
        [session_id],
    )
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    Ok(Json(()))
}

async fn unarchive_session(
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
) -> Result<Json<()>, StatusCode> {
    let conn = state.db.get().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    conn.execute(
        "UPDATE sessions SET archived = 0 WHERE id = ?1",
        [session_id],
    )
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    Ok(Json(()))
}

async fn get_observations(
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
) -> Result<Json<Vec<crate::db::models::Observation>>, StatusCode> {
    queries::get_observations(&state.db, &session_id)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

// AI 辅助搜索
async fn ai_search(
    State(state): State<Arc<AppState>>,
    Json(req): Json<SearchRequest>,
) -> Result<Json<Vec<crate::core::SearchResult>>, StatusCode> {
    let ai_engine = AISearchEngine::new();
    let intent = ai_engine.parse_query(&req.query);
    
    // 执行基础搜索
    let sessions = queries::list_sessions(&state.db, 100)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let mut all_obs = Vec::new();
    for session in sessions {
        let obs = queries::get_observations(&state.db, &session.id)
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
        all_obs.extend(obs);
    }
    
    let engine = VectorSearchEngine::new();
    let mut results = engine.search(all_obs, &req.query, req.threshold);
    
    // AI 优化排序
    let mut scored_results: Vec<(String, f32)> = results
        .iter()
        .map(|r| (r.content.clone(), r.similarity))
        .collect();
    
    ai_engine.rank_results(&mut scored_results, &intent);
    
    // 转换回 SearchResult
    let optimized_results: Vec<_> = scored_results
        .into_iter()
        .zip(results.iter())
        .map(|((_, score), r)| crate::core::SearchResult {
            id: r.id.clone(),
            session_id: r.session_id.clone(),
            content: r.content.clone(),
            similarity: score,
            priority: r.priority.clone(),
        })
        .collect();
    
    Ok(Json(optimized_results))
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

// 生成会话摘要
async fn generate_summary(
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
) -> Result<Json<crate::core::Summary>, StatusCode> {
    let generator = SummaryGenerator::new();
    
    // 获取会话消息
    let conn = state.db.get().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    let mut stmt = conn.prepare(
        "SELECT content FROM messages WHERE session_id = ? ORDER BY timestamp"
    ).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let messages: Vec<String> = stmt.query_map([&session_id], |row| {
        row.get(0)
    }).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
    .collect::<Result<Vec<_>, _>>()
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let summary = generator.generate_session_summary(&messages);
    Ok(Json(summary))
}

// 获取搜索建议
async fn get_suggestions(
    State(_state): State<Arc<AppState>>,
    Json(req): Json<SearchRequest>,
) -> Result<Json<Vec<String>>, StatusCode> {
    let ai_engine = AISearchEngine::new();
    let suggestions = ai_engine.generate_suggestions(&req.query);
    Ok(Json(suggestions))
}

// 获取知识图谱
async fn get_knowledge_graph(
    State(state): State<Arc<AppState>>,
) -> Result<Json<crate::core::KnowledgeGraph>, StatusCode> {
    let builder = KnowledgeGraphBuilder::new();
    
    // 获取所有观察
    let sessions = queries::list_sessions(&state.db, 100)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let mut all_texts = Vec::new();
    for session in sessions {
        let obs = queries::get_observations(&state.db, &session.id)
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
        all_texts.extend(obs.into_iter().map(|o| o.content));
    }
    
    let graph = builder.build_from_texts(&all_texts);
    Ok(Json(graph))
}

// 获取相关实体
async fn get_related_entities(
    State(state): State<Arc<AppState>>,
    Path(entity_id): Path<String>,
) -> Result<Json<Vec<crate::core::Node>>, StatusCode> {
    let builder = KnowledgeGraphBuilder::new();
    
    // 先获取完整图谱
    let sessions = queries::list_sessions(&state.db, 100)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    
    let mut all_texts = Vec::new();
    for session in sessions {
        let obs = queries::get_observations(&state.db, &session.id)
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
        all_texts.extend(obs.into_iter().map(|o| o.content));
    }
    
    let graph = builder.build_from_texts(&all_texts);
    
    // 查找相关实体
    let related = builder.find_related_entities(&graph, &entity_id, 2);
    Ok(Json(related))
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










