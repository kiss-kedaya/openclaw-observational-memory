pub mod deduplication;
pub mod relevance;

pub use deduplication::{deduplicate_observation, detect_conflicts, Conflict};
pub use relevance::{calculate_relevance_score, update_access_record, get_relevant_observations};
