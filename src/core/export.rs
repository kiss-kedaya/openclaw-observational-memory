use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::Write;
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportConfig {
    pub format: ExportFormat,
    pub include_messages: bool,
    pub include_observations: bool,
    pub time_range: Option<TimeRange>,
    pub session_ids: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExportFormat {
    Json,
    Csv,
    Markdown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TimeRange {
    pub start: String,
    pub end: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportData {
    pub sessions: Vec<SessionExport>,
    pub metadata: ExportMetadata,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionExport {
    pub id: String,
    pub created_at: String,
    pub updated_at: String,
    pub message_count: i32,
    pub token_count: i32,
    pub messages: Option<Vec<MessageExport>>,
    pub observations: Option<Vec<ObservationExport>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessageExport {
    pub role: String,
    pub content: String,
    pub timestamp: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObservationExport {
    pub content: String,
    pub priority: String,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportMetadata {
    pub export_time: String,
    pub version: String,
    pub total_sessions: usize,
    pub total_messages: usize,
    pub total_observations: usize,
}

pub struct DataExporter;

impl DataExporter {
    pub fn new() -> Self {
        Self
    }
    
    /// 导出为 JSON
    pub fn export_to_json(&self, data: &ExportData, path: &Path) -> Result<()> {
        let json = serde_json::to_string_pretty(data)?;
        let mut file = File::create(path)?;
        file.write_all(json.as_bytes())?;
        Ok(())
    }
    
    /// 导出为 CSV
    pub fn export_to_csv(&self, data: &ExportData, path: &Path) -> Result<()> {
        let mut file = File::create(path)?;
        
        // 写入表头
        writeln!(file, "Session ID,Created At,Message Count,Token Count,Role,Content,Timestamp")?;
        
        // 写入数据
        for session in &data.sessions {
            if let Some(messages) = &session.messages {
                for message in messages {
                    writeln!(
                        file,
                        "{},{},{},{},{},{},{}",
                        session.id,
                        session.created_at,
                        session.message_count,
                        session.token_count,
                        message.role,
                        Self::escape_csv(&message.content),
                        message.timestamp
                    )?;
                }
            } else {
                writeln!(
                    file,
                    "{},{},{},{},,,,",
                    session.id,
                    session.created_at,
                    session.message_count,
                    session.token_count
                )?;
            }
        }
        
        Ok(())
    }
    
    /// 导出为 Markdown
    pub fn export_to_markdown(&self, data: &ExportData, path: &Path) -> Result<()> {
        let mut file = File::create(path)?;
        
        // 写入标题
        writeln!(file, "# Observational Memory Export\n")?;
        writeln!(file, "Export Time: {}\n", data.metadata.export_time)?;
        writeln!(file, "Version: {}\n", data.metadata.version)?;
        writeln!(file, "---\n")?;
        
        // 写入统计信息
        writeln!(file, "## Statistics\n")?;
        writeln!(file, "- Total Sessions: {}", data.metadata.total_sessions)?;
        writeln!(file, "- Total Messages: {}", data.metadata.total_messages)?;
        writeln!(file, "- Total Observations: {}\n", data.metadata.total_observations)?;
        writeln!(file, "---\n")?;
        
        // 写入会话数据
        for session in &data.sessions {
            writeln!(file, "## Session: {}\n", session.id)?;
            writeln!(file, "- Created: {}", session.created_at)?;
            writeln!(file, "- Messages: {}", session.message_count)?;
            writeln!(file, "- Tokens: {}\n", session.token_count)?;
            
            if let Some(messages) = &session.messages {
                writeln!(file, "### Messages\n")?;
                for message in messages {
                    writeln!(file, "**{}** ({})", message.role, message.timestamp)?;
                    writeln!(file, "{}\n", message.content)?;
                }
            }
            
            if let Some(observations) = &session.observations {
                writeln!(file, "### Observations\n")?;
                for obs in observations {
                    writeln!(file, "- **{}** [{}]: {}", obs.priority, obs.created_at, obs.content)?;
                }
                writeln!(file)?;
            }
            
            writeln!(file, "---\n")?;
        }
        
        Ok(())
    }
    
    /// CSV 转义
    fn escape_csv(s: &str) -> String {
        if s.contains(',') || s.contains('"') || s.contains('\n') {
            format!("\"{}\"", s.replace('"', "\"\""))
        } else {
            s.to_string()
        }
    }
}

pub struct DataImporter;

impl DataImporter {
    pub fn new() -> Self {
        Self
    }
    
    /// 从 JSON 导入
    pub fn import_from_json(&self, path: &Path) -> Result<ExportData> {
        let content = std::fs::read_to_string(path)?;
        let data: ExportData = serde_json::from_str(&content)?;
        Ok(data)
    }
    
    /// 验证导入数据
    pub fn validate_import_data(&self, data: &ExportData) -> Result<()> {
        // 检查版本兼容性
        if data.metadata.version != "2.3.0" && !data.metadata.version.starts_with("2.") {
            return Err(anyhow::anyhow!("Incompatible version: {}", data.metadata.version));
        }
        
        // 检查数据完整性
        if data.sessions.is_empty() {
            return Err(anyhow::anyhow!("No sessions to import"));
        }
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_export_json() {
        let exporter = DataExporter::new();
        let data = ExportData {
            sessions: vec![],
            metadata: ExportMetadata {
                export_time: chrono::Utc::now().to_rfc3339(),
                version: "2.3.0".to_string(),
                total_sessions: 0,
                total_messages: 0,
                total_observations: 0,
            },
        };
        
        let path = Path::new("test_export.json");
        assert!(exporter.export_to_json(&data, path).is_ok());
        std::fs::remove_file(path).ok();
    }
    
    #[test]
    fn test_escape_csv() {
        assert_eq!(DataExporter::escape_csv("hello"), "hello");
        assert_eq!(DataExporter::escape_csv("hello,world"), "\"hello,world\"");
        assert_eq!(DataExporter::escape_csv("hello\"world"), "\"hello\"\"world\"");
    }
}
