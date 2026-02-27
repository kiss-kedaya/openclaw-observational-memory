use anyhow::Result;
use tantivy::collector::TopDocs;
use tantivy::query::QueryParser;
use tantivy::schema::*;
use tantivy::{doc, Index, IndexWriter, ReloadPolicy};
use std::path::Path;

use crate::db::models::Observation;

pub struct VectorSearchEngine {
    index: Index,
    schema: Schema,
    writer: IndexWriter,
}

impl VectorSearchEngine {
    pub fn new<P: AsRef<Path>>(index_path: P) -> Result<Self> {
        // Build schema
        let mut schema_builder = Schema::builder();
        schema_builder.add_text_field("id", TEXT | STORED);
        schema_builder.add_text_field("session_id", TEXT | STORED);
        schema_builder.add_text_field("content", TEXT | STORED);
        schema_builder.add_text_field("priority", TEXT | STORED);
        schema_builder.add_date_field("created_at", STORED);
        let schema = schema_builder.build();

        // Create or open index
        let index = if index_path.as_ref().exists() {
            Index::open_in_dir(index_path)?
        } else {
            std::fs::create_dir_all(&index_path)?;
            Index::create_in_dir(index_path, schema.clone())?
        };

        // Create writer
        let writer = index.writer(50_000_000)?;

        Ok(Self {
            index,
            schema,
            writer,
        })
    }

    pub fn index_observation(&mut self, obs: &Observation) -> Result<()> {
        let id = self.schema.get_field("id").unwrap();
        let session_id = self.schema.get_field("session_id").unwrap();
        let content = self.schema.get_field("content").unwrap();
        let priority = self.schema.get_field("priority").unwrap();
        let created_at = self.schema.get_field("created_at").unwrap();

        let timestamp = chrono::DateTime::parse_from_rfc3339(&obs.created_at)
            .unwrap()
            .timestamp();

        self.writer.add_document(doc!(
            id => obs.id.clone(),
            session_id => obs.session_id.clone(),
            content => obs.content.clone(),
            priority => obs.priority.clone(),
            created_at => tantivy::DateTime::from_timestamp_secs(timestamp),
        ))?;

        self.writer.commit()?;

        Ok(())
    }

    pub fn search(&self, query_str: &str, threshold: f32, top_k: usize) -> Result<Vec<SearchResult>> {
        let reader = self
            .index
            .reader_builder()
            .reload_policy(ReloadPolicy::OnCommit)
            .try_into()?;

        let searcher = reader.searcher();

        let content_field = self.schema.get_field("content").unwrap();
        let query_parser = QueryParser::for_index(&self.index, vec![content_field]);
        let query = query_parser.parse_query(query_str)?;

        let top_docs = searcher.search(&query, &TopDocs::with_limit(top_k))?;

        let mut results = Vec::new();

        for (_score, doc_address) in top_docs {
            let retrieved_doc = searcher.doc(doc_address)?;

            let id = retrieved_doc
                .get_first(self.schema.get_field("id").unwrap())
                .and_then(|v| v.as_text())
                .unwrap_or("")
                .to_string();

            let session_id = retrieved_doc
                .get_first(self.schema.get_field("session_id").unwrap())
                .and_then(|v| v.as_text())
                .unwrap_or("")
                .to_string();

            let content = retrieved_doc
                .get_first(self.schema.get_field("content").unwrap())
                .and_then(|v| v.as_text())
                .unwrap_or("")
                .to_string();

            let priority = retrieved_doc
                .get_first(self.schema.get_field("priority").unwrap())
                .and_then(|v| v.as_text())
                .unwrap_or("")
                .to_string();

            // Simple similarity calculation (placeholder)
            let similarity = calculate_similarity(query_str, &content);

            if similarity >= threshold {
                results.push(SearchResult {
                    id,
                    session_id,
                    content,
                    priority,
                    similarity,
                });
            }
        }

        Ok(results)
    }
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SearchResult {
    pub id: String,
    pub session_id: String,
    pub content: String,
    pub priority: String,
    pub similarity: f32,
}

fn calculate_similarity(query: &str, content: &str) -> f32 {
    let query_lower = query.to_lowercase();
    let content_lower = content.to_lowercase();

    // Simple word overlap similarity
    let query_words: Vec<&str> = query_lower.split_whitespace().collect();
    let content_words: Vec<&str> = content_lower.split_whitespace().collect();

    let mut matches = 0;
    for word in &query_words {
        if content_words.contains(word) {
            matches += 1;
        }
    }

    if query_words.is_empty() {
        return 0.0;
    }

    (matches as f32) / (query_words.len() as f32)
}
