export interface Session {
  id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  token_count: number;
}

export interface Observation {
  id: string;
  session_id: string;
  content: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  created_at: string;
}

export interface Message {
  role: string;
  content: string;
  timestamp: string;
}

export interface SearchResult {
  session_id: string;
  observation: string;
  similarity: number;
}

export interface ToolSuggestion {
  tool: string;
  reason: string;
  confidence: number;
  context: string;
}

export interface Statistics {
  total_sessions: number;
  total_observations: number;
  total_tokens: number;
  priority_distribution: {
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
}
