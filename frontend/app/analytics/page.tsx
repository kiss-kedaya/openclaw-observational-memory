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
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
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

  const highPriorityCount = observations.filter((o) => o.priority === "HIGH").length;
  const mediumPriorityCount = observations.filter((o) => o.priority === "MEDIUM").length;
  const lowPriorityCount = observations.filter((o) => o.priority === "LOW").length;
  const totalTokens = sessions.reduce((sum, s) => sum + s.token_count, 0);

  const priorityData = [
    { name: "高", value: highPriorityCount, color: "#ef4444" },
    { name: "中", value: mediumPriorityCount, color: "#f59e0b" },
    { name: "低", value: lowPriorityCount, color: "#10b981" },
  ];

  const radarData = [
    { subject: "高优先级", value: highPriorityCount },
    { subject: "中优先级", value: mediumPriorityCount },
    { subject: "低优先级", value: lowPriorityCount },
    { subject: "会话数", value: sessions.length },
    { subject: "Token(K)", value: Math.round(totalTokens / 1000) },
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

  const heatmapData = Array.from({ length: 24 }, (_, hour) => ({
    hour: `${hour}:00`,
    count: observations.filter((o) => {
      const obsHour = new Date(o.created_at).getHours();
      return obsHour === hour;
    }).length,
  }));

  const getHeatColor = (count: number) => {
    if (count === 0) return "#e5e7eb";
    if (count < 5) return "#93c5fd";
    if (count < 10) return "#60a5fa";
    if (count < 20) return "#3b82f6";
    return "#1d4ed8";
  };

  const exportChart = (chartId: string, filename: string) => {
    const chartElement = document.querySelector(`#${chartId}`);
    if (!chartElement) {
      alert("图表未找到");
      return;
    }

    const svg = chartElement.querySelector("svg");
    if (!svg) {
      alert("SVG 元素未找到");
      return;
    }

    const svgData = new XMLSerializer().serializeToString(svg);
    const blob = new Blob([svgData], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `${filename}.svg`;
    a.click();

    URL.revokeObjectURL(url);
  };

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
              <p className="text-3xl font-bold mt-2">{totalTokens.toLocaleString()}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">平均消息数</h3>
              <p className="text-3xl font-bold mt-2">
                {sessions.length > 0
                  ? Math.round(
                      sessions.reduce((sum, s) => sum + s.message_count, 0) /
                        sessions.length
                    )
                  : 0}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">优先级分布</h2>
                <button
                  onClick={() => exportChart("priority-chart", "priority-distribution")}
                  className="text-sm text-blue-500 hover:text-blue-700"
                >
                  导出图表
                </button>
              </div>
              <div id="priority-chart">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={priorityData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }: any) =>
                        `${name}: ${(percent * 100).toFixed(0)}%`
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
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">雷达图分析</h2>
                <button
                  onClick={() => exportChart("radar-chart", "radar-analysis")}
                  className="text-sm text-blue-500 hover:text-blue-700"
                >
                  导出图表
                </button>
              </div>
              <div id="radar-chart">
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <PolarRadiusAxis />
                    <Radar
                      name="观察分析"
                      dataKey="value"
                      stroke="#8b5cf6"
                      fill="#8b5cf6"
                      fillOpacity={0.6}
                    />
                    <Tooltip />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">消息时间线</h2>
              <button
                onClick={() => exportChart("timeline-chart", "message-timeline")}
                className="text-sm text-blue-500 hover:text-blue-700"
              >
                导出图表
              </button>
            </div>
            <div id="timeline-chart">
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
                    name="消息数"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Token 使用统计</h2>
              <button
                onClick={() => exportChart("token-chart", "token-usage")}
                className="text-sm text-blue-500 hover:text-blue-700"
              >
                导出图表
              </button>
            </div>
            <div id="token-chart">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={tokenData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="session" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="tokens" fill="#10b981" name="Token 数" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">24 小时活动热力图</h2>
              <button
                onClick={() => exportChart("heatmap-chart", "activity-heatmap")}
                className="text-sm text-blue-500 hover:text-blue-700"
              >
                导出图表
              </button>
            </div>
            <div id="heatmap-chart">
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={heatmapData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" name="观察数">
                    {heatmapData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getHeatColor(entry.count)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
