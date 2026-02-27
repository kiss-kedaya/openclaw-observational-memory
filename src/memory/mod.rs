pub mod deduplication;
pub mod relevance;
pub mod patterns;
pub mod consolidation;

pub use deduplication::{deduplicate_observation, detect_conflicts, Conflict};
pub use relevance::{calculate_relevance_score, update_access_record, get_relevant_observations};
pub use patterns::{Pattern, PatternType, cluster_observations, analyze_temporal_patterns, mine_association_rules, identify_recurring_tasks};
pub use consolidation::{consolidate_memories, archive_low_priority_memories, generate_weekly_summary, auto_consolidation_task};
