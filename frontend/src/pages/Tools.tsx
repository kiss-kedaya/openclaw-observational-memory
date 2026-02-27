import { useEffect, useState } from "react";
import { observationApi } from "../lib/api";
import type { Observation } from "../types";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

interface ToolSuggestion {
  tool: string;
  reason: string;
  confidence: number;
  context: string;
  timestamp: string;
}

export default function Tools() {
  const [suggestions, setSuggestions] = useState<ToolSuggestion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load observations and analyze for tool suggestions
      // This is a placeholder - real implementation will use backend API
      const mockSuggestions: ToolSuggestion[] = [
        {
          tool: "agent-reach",
          reason: "检测到社交媒体链接",
          confidence: 0.9,
          context: "https://twitter.com/user/status/123",
          timestamp: new Date().toISOString(),
        },
        {
          tool: "agent-browser",
          reason: "需要浏览器交互",
          confidence: 0.85,
          context: "打开浏览器填写表单",
          timestamp: new Date().toISOString(),
        },
        {
          tool: "web_search",
          reason: "需要搜索信息",
          confidence: 0.75,
          context: "搜索 OpenClaw 文档",
          timestamp: new Date().toISOString(),
        },
        {
          tool: "debugging-wizard",
          reason: "检测到代码问题",
          confidence: 0.8,
          context: "ImportError: No module named xxx",
          timestamp: new Date().toISOString(),
        },
      ];

      setSuggestions(mockSuggestions);
    } catch (error) {
      console.error("Failed to load tool suggestions:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading tool suggestions...</div>
      </div>
    );
  }

  // Calculate statistics
  const totalSuggestions = suggestions.length;
  const avgConfidence =
    suggestions.reduce((sum, s) => sum + s.confidence, 0) / totalSuggestions;
  const toolCounts = suggestions.reduce((acc: any, s) => {
    acc[s.tool] = (acc[s.tool] || 0) + 1;
    return acc;
  }, {});
  const mostUsedTool = Object.entries(toolCounts).sort(
    ([, a]: any, [, b]: any) => b - a
  )[0]?.[0] || "N/A";

  // Tool distribution data
  const toolDistribution = Object.entries(toolCounts).map(([tool, count]) => ({
    name: tool,
    value: count as number,
  }));

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

  const getConfidenceColor = (confidence: number) => {
    if (confidence > 0.8) return "text-green-500";
    if (confidence > 0.6) return "text-yellow-500";
    return "text-red-500";
  };

  const getConfidenceBg = (confidence: number) => {
    if (confidence > 0.8)
      return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    if (confidence > 0.6)
      return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
    return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Tool Suggestions</h1>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Total Suggestions
          </div>
          <div className="text-3xl font-bold mt-2">{totalSuggestions}</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Average Confidence
          </div>
          <div className={`text-3xl font-bold mt-2 ${getConfidenceColor(avgConfidence)}`}>
            {(avgConfidence * 100).toFixed(0)}%
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Most Used Tool
          </div>
          <div className="text-2xl font-bold mt-2 truncate">{mostUsedTool}</div>
        </div>
      </div>

      {/* Tool Distribution Chart */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Tool Distribution</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={toolDistribution}
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
              {toolDistribution.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Suggestions */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Recent Suggestions</h2>
        <div className="space-y-4">
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 transition"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold text-blue-500">
                    {suggestion.tool}
                  </span>
                  <span
                    className={`px-2 py-1 text-xs rounded ${getConfidenceBg(
                      suggestion.confidence
                    )}`}
                  >
                    {(suggestion.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {new Date(suggestion.timestamp).toLocaleString()}
                </span>
              </div>

              <div className="mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Reason:
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400 ml-2">
                  {suggestion.reason}
                </span>
              </div>

              {suggestion.context && (
                <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    Context:
                  </div>
                  <div className="text-sm text-gray-700 dark:text-gray-300 font-mono">
                    {suggestion.context}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Tool Legend */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Tool Reference</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border border-gray-200 dark:border-gray-700 rounded">
            <div className="font-bold text-blue-500 mb-2">agent-reach</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Social media interaction and content retrieval
            </div>
          </div>

          <div className="p-4 border border-gray-200 dark:border-gray-700 rounded">
            <div className="font-bold text-green-500 mb-2">agent-browser</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Browser automation and web interaction
            </div>
          </div>

          <div className="p-4 border border-gray-200 dark:border-gray-700 rounded">
            <div className="font-bold text-yellow-500 mb-2">web_search</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Web search and information retrieval
            </div>
          </div>

          <div className="p-4 border border-gray-200 dark:border-gray-700 rounded">
            <div className="font-bold text-red-500 mb-2">debugging-wizard</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Code debugging and error analysis
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
