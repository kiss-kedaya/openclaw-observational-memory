import { useEffect, useState } from "react";
import { sessionApi, observationApi } from "../lib/api";
import type { Session, Observation } from "../types";

export default function Dashboard() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [stats, setStats] = useState({
    totalSessions: 0,
    totalObservations: 0,
    totalTokens: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const { data: sessionList } = await sessionApi.list();
      setSessions(sessionList);

      // Calculate statistics
      const totalTokens = sessionList.reduce(
        (sum: number, s: Session) => sum + s.token_count,
        0
      );

      // Load observations count
      let totalObs = 0;
      for (const session of sessionList.slice(0, 10)) {
        const { data: obs } = await observationApi.list(session.id);
        totalObs += obs.length;
      }

      setStats({
        totalSessions: sessionList.length,
        totalObservations: totalObs,
        totalTokens,
      });
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
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
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Total Sessions
          </div>
          <div className="text-3xl font-bold mt-2">{stats.totalSessions}</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Total Observations
          </div>
          <div className="text-3xl font-bold mt-2">
            {stats.totalObservations}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Total Tokens
          </div>
          <div className="text-3xl font-bold mt-2">
            {stats.totalTokens.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Recent Sessions */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Recent Sessions</h2>
        <div className="space-y-2">
          {sessions.slice(0, 10).map((session) => (
            <div
              key={session.id}
              className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              <div>
                <div className="font-medium">{session.id}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {new Date(session.updated_at).toLocaleString()}
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm">
                  {session.message_count} messages
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {session.token_count} tokens
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

