import { useEffect, useState } from "react";
import { sessionApi, observationApi } from "../lib/api";
import type { Session, Observation } from "../types";
import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function Analytics() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const { data: sessionList } = await sessionApi.list();
      setSessions(sessionList);

      // Load all observations
      const allObs: Observation[] = [];
      for (const session of sessionList.slice(0, 20)) {
        const { data: obs } = await observationApi.list(session.id);
        allObs.push(...obs);
      }
      setObservations(allObs);
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading analytics...</div>
      </div>
    );
  }

  // Priority distribution
  const priorityData = [
    {
      name: "HIGH",
      value: observations.filter((o) => o.priority === "HIGH").length,
      color: "#ef4444",
    },
    {
      name: "MEDIUM",
      value: observations.filter((o) => o.priority === "MEDIUM").length,
      color: "#f59e0b",
    },
    {
      name: "LOW",
      value: observations.filter((o) => o.priority === "LOW").length,
      color: "#10b981",
    },
  ];

  // Timeline data (sessions by date)
  const timelineData = sessions
    .reduce((acc: any[], session) => {
      const date = new Date(session.created_at).toLocaleDateString();
      const existing = acc.find((item) => item.date === date);
      if (existing) {
        existing.count += 1;
      } else {
        acc.push({ date, count: 1 });
      }
      return acc;
    }, [])
    .slice(-7); // Last 7 days

  // Token usage data
  const tokenData = sessions.slice(0, 10).map((session) => ({
    session: session.id.substring(0, 8),
    tokens: session.token_count,
  }));

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Analytics</h1>

      {/* Priority Distribution */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Priority Distribution</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={priorityData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent = 0 }) =>
                `${name}: ${(percent * 100).toFixed(0)}%`
              }
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {priorityData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Session Timeline */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Session Timeline (Last 7 Days)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timelineData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#3b82f6"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Token Usage */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Token Usage (Top 10 Sessions)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={tokenData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="session" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="tokens" fill="#8b5cf6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Statistics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Total Sessions
          </div>
          <div className="text-3xl font-bold mt-2">{sessions.length}</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Total Observations
          </div>
          <div className="text-3xl font-bold mt-2">{observations.length}</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Avg Tokens/Session
          </div>
          <div className="text-3xl font-bold mt-2">
            {sessions.length > 0
              ? Math.round(
                  sessions.reduce((sum, s) => sum + s.token_count, 0) /
                    sessions.length
                )
              : 0}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            High Priority
          </div>
          <div className="text-3xl font-bold mt-2 text-red-500">
            {observations.filter((o) => o.priority === "HIGH").length}
          </div>
        </div>
      </div>
    </div>
  );
}

