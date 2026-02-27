use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackupInfo {
    pub id: String,
    pub created_at: String,
    pub size: u64,
    pub backup_type: BackupType,
    pub file_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BackupType {
    Full,        // 完整备份
    Incremental, // 增量备份
    Manual,      // 手动备份
    Auto,        // 自动备份
}

pub struct BackupManager {
    backup_dir: PathBuf,
}

impl BackupManager {
    pub fn new(backup_dir: &Path) -> Result<Self> {
        // 创建备份目录
        fs::create_dir_all(backup_dir)?;
        
        Ok(Self {
            backup_dir: backup_dir.to_path_buf(),
        })
    }
    
    /// 创建完整备份
    pub fn create_full_backup(&self, db_path: &Path) -> Result<BackupInfo> {
        let backup_id = uuid::Uuid::new_v4().to_string();
        let timestamp = chrono::Utc::now().format("%Y%m%d_%H%M%S");
        let backup_filename = format!("backup_full_{}_{}.db", timestamp, &backup_id[..8]);
        let backup_path = self.backup_dir.join(&backup_filename);
        
        // 复制数据库文件
        fs::copy(db_path, &backup_path)?;
        
        let size = fs::metadata(&backup_path)?.len();
        
        Ok(BackupInfo {
            id: backup_id,
            created_at: chrono::Utc::now().to_rfc3339(),
            size,
            backup_type: BackupType::Full,
            file_path: backup_path.to_string_lossy().to_string(),
        })
    }
    
    /// 创建增量备份
    pub fn create_incremental_backup(&self, db_path: &Path, last_backup_time: &str) -> Result<BackupInfo> {
        // 简化版：实际应该只备份变化的数据
        // 这里先实现完整备份，后续可以优化
        let mut backup_info = self.create_full_backup(db_path)?;
        backup_info.backup_type = BackupType::Incremental;
        Ok(backup_info)
    }
    
    /// 恢复备份
    pub fn restore_backup(&self, backup_info: &BackupInfo, target_path: &Path) -> Result<()> {
        let backup_path = Path::new(&backup_info.file_path);
        
        if !backup_path.exists() {
            return Err(anyhow::anyhow!("Backup file not found: {}", backup_info.file_path));
        }
        
        // 备份当前数据库（以防恢复失败）
        if target_path.exists() {
            let temp_backup = target_path.with_extension("db.bak");
            fs::copy(target_path, &temp_backup)?;
        }
        
        // 恢复备份
        fs::copy(backup_path, target_path)?;
        
        Ok(())
    }
    
    /// 列出所有备份
    pub fn list_backups(&self) -> Result<Vec<BackupInfo>> {
        let mut backups = Vec::new();
        
        for entry in fs::read_dir(&self.backup_dir)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.extension().and_then(|s| s.to_str()) == Some("db") {
                let metadata = fs::metadata(&path)?;
                let filename = path.file_name().unwrap().to_string_lossy();
                
                // 解析文件名获取信息
                let backup_type = if filename.contains("_full_") {
                    BackupType::Full
                } else if filename.contains("_incremental_") {
                    BackupType::Incremental
                } else if filename.contains("_manual_") {
                    BackupType::Manual
                } else {
                    BackupType::Auto
                };
                
                backups.push(BackupInfo {
                    id: uuid::Uuid::new_v4().to_string(),
                    created_at: metadata.created()
                        .ok()
                        .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                        .map(|d| chrono::DateTime::from_timestamp(d.as_secs() as i64, 0))
                        .flatten()
                        .map(|dt| dt.to_rfc3339())
                        .unwrap_or_default(),
                    size: metadata.len(),
                    backup_type,
                    file_path: path.to_string_lossy().to_string(),
                });
            }
        }
        
        // 按创建时间排序
        backups.sort_by(|a, b| b.created_at.cmp(&a.created_at));
        
        Ok(backups)
    }
    
    /// 删除备份
    pub fn delete_backup(&self, backup_info: &BackupInfo) -> Result<()> {
        let backup_path = Path::new(&backup_info.file_path);
        fs::remove_file(backup_path)?;
        Ok(())
    }
    
    /// 清理旧备份（保留最近 N 个）
    pub fn cleanup_old_backups(&self, keep_count: usize) -> Result<usize> {
        let backups = self.list_backups()?;
        let mut deleted = 0;
        
        for backup in backups.iter().skip(keep_count) {
            self.delete_backup(backup)?;
            deleted += 1;
        }
        
        Ok(deleted)
    }
    
    /// 获取备份目录大小
    pub fn get_backup_dir_size(&self) -> Result<u64> {
        let mut total_size = 0;
        
        for entry in fs::read_dir(&self.backup_dir)? {
            let entry = entry?;
            let metadata = fs::metadata(entry.path())?;
            total_size += metadata.len();
        }
        
        Ok(total_size)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    
    #[test]
    fn test_backup_manager() {
        let temp_dir = std::env::temp_dir().join("test_backups");
        let manager = BackupManager::new(&temp_dir).unwrap();
        
        // 创建测试数据库
        let test_db = temp_dir.join("test.db");
        File::create(&test_db).unwrap();
        
        // 测试备份
        let backup = manager.create_full_backup(&test_db).unwrap();
        assert!(Path::new(&backup.file_path).exists());
        
        // 清理
        fs::remove_dir_all(&temp_dir).ok();
    }
}
