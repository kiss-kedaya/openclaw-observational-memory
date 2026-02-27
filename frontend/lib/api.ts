import axios from "axios";
import type { Session, Observation, Message } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api";

export interface CreateSessionRequest {
  session_id: string;
  messages: Message[];
}

export interface CreateSessionResponse {
  session: Session;
  observations: string[];
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const sessionApi = {
  list: () => api.get<Session[]>("/sessions"),
  get: (id: string) => api.get<Session>(`/sessions/${id}`),
  create: (data: CreateSessionRequest) =>
    api.post<CreateSessionResponse>("/sessions", data),
};

export const observationApi = {
  list: (sessionId: string) =>
    api.get<Observation[]>(`/observations/${sessionId}`),
};

export const searchApi = {
  search: (query: string, threshold: number) =>
    api.post("/search", { query, threshold }),
};

export const toolsApi = {
  suggestions: () => api.get("/tools/suggestions"),
};

export const memoryApi = {
  compress: () => api.post("/memory/compress"),
  clusters: () => api.get("/memory/clusters"),
};

export default api;
