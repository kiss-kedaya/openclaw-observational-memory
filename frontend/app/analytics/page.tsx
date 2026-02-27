"use client";

import { useState, useEffect } from "react";
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
import { sessionApi, observationApi } from "@/lib/api";
import type { Session, Observation } from "@/types";

export default function AnalyticsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const sessionsRes = await sessionApi.list();
      const sessionList = sessionsRes.data;
      setSessions(sessionList);

      const allObs: Observation[] = [];
      for (const session of sessionList) {
        try {
          const obsRes = await observationApi.list(session.id);
          allObs.push(...obsRes.data);
        } catch (error) {
          console.error(`加载会话 ${session.id} 的观察失败:`, error);
        }
      }
      setObservations(allObs);
    } catch (error) {
      console.error("加载数据失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const priorityData = [
    {
      name: "高",
      value: observations.filter((o) => o.priority === "HIGH").length,
      color: "#ef4444",
    },
    {
      name: "中",
      value: observations.filter((o) => o.priority === "MEDIUM").length,
      color: "#f59e0b",
    },
    {
      name: "低",
      value: observations.filter((o) => o.priority === "LOW").length,
      color: "#10b981",
    },
  ];

  const timelineData = sessions
    .map((s) => ({
      date: new Date(s.created_at).toLocaleDateString("zh-CN", {
        month: "short",
        day: "numeric",
      }),
      count: s.message_count,
    }))
    .slice(-10);

  const tokenData = sessions
    .map((s) => ({
      session: s.id.slice(0, 10) + "...",
      tokens: s.token_count,
    }))
    .slice(-10);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">数据分析</h1>

      {loading ? (
        <div className="text-center py-8">加载中...</div>
      ) : (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">总会话数</h3>
              <p className="text-3xl font-bold mt-2">{sessions.length}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">总观察数</h3>
              <p className="text-3xl font-bold mt-2">{observations.length}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">总 Token 数</h3>
              <p className="text-3xl font-bold mt-2">
                {sessions
                  .reduce((sum, s) => sum + s.token_count, 0)
                  .toLocaleString()}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">
                平均 Token/会话
              </h3>
              <p className="text-3xl font-bold mt-2">
                {sessions.length > 0
                  ? Math.round(
                      sessions.reduce((sum, s) => sum + s.token_count, 0) /
                        sessions.length
                    ).toLocaleString()
                  : 0}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">优先级分布</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={priorityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent = 0 }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={80}
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

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">会话时间线</h2>
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
                  name="消息数"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Token 使用统计</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tokenData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="session" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="tokens" fill="#8b5cf6" name="Token 数" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
