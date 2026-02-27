import { useEffect, useState } from "react";
import { sessionApi, observationApi } from "../lib/api";
import type { Session, Observation } from "../types";

export default function Sessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const { data } = await sessionApi.list();
      setSessions(data);
    } catch (error) {
      console.error("Failed to load sessions:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadObservations = async (sessionId: string) => {
    try {
      const { data } = await observationApi.list(sessionId);
      setObservations(data);
      setSelectedSession(sessionId);
    } catch (error) {
      console.error("Failed to load observations:", error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Sessions</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sessions List */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">All Sessions</h2>
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => loadObservations(session.id)}
                className={`p-4 border rounded cursor-pointer transition ${
                  selectedSession === session.id
                    ? "border-blue-500 bg-blue-50 dark:bg-blue-900"
                    : "border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
                }`}
              >
                <div className="font-medium">{session.id}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {new Date(session.updated_at).toLocaleString()}
                </div>
                <div className="flex gap-4 mt-2 text-sm">
                  <span>{session.message_count} messages</span>
                  <span>{session.token_count} tokens</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Observations */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Observations</h2>
          {selectedSession ? (
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {observations.map((obs) => (
                <div
                  key={obs.id}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm">{obs.content}</p>
                    </div>
                    <span
                      className={`ml-2 px-2 py-1 text-xs rounded ${
                        obs.priority === "HIGH"
                          ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                          : obs.priority === "MEDIUM"
                          ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                          : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                      }`}
                    >
                      {obs.priority}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    {new Date(obs.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-500 dark:text-gray-400 py-12">
              Select a session to view observations
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

