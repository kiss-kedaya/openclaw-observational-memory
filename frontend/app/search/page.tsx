"use client";

import { useState } from "react";

interface SearchResult {
  observation_id: string;
  session_id: string;
  content: string;
  similarity: number;
  priority: string;
  timestamp: string;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [threshold, setThreshold] = useState(0.7);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await fetch("http://localhost:3000/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, threshold }),
      });
      const data = await res.json();
      setResults(data);
    } catch (error) {
      console.error("搜索失败:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">搜索观察</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              搜索关键词
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              placeholder="输入搜索关键词..."
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              相似度阈值: {threshold.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="w-full bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? "搜索中..." : "搜索"}
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {results.map((result) => (
          <div
            key={result.observation_id}
            className="bg-white rounded-lg shadow p-6"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <span
                  className={`px-2 py-1 rounded text-xs ${
                    result.priority === "HIGH"
                      ? "bg-red-100 text-red-800"
                      : result.priority === "MEDIUM"
                      ? "bg-yellow-100 text-yellow-800"
                      : "bg-green-100 text-green-800"
                  }`}
                >
                  {result.priority === "HIGH"
                    ? "高"
                    : result.priority === "MEDIUM"
                    ? "中"
                    : "低"}
                </span>
                <span className="ml-2 text-sm text-gray-500">
                  相似度: {(result.similarity * 100).toFixed(1)}%
                </span>
              </div>
              <span className="text-sm text-gray-500">
                {new Date(result.timestamp).toLocaleString("zh-CN")}
              </span>
            </div>
            <p className="text-gray-700">{result.content}</p>
            <div className="mt-2 text-xs text-gray-500">
              会话: {result.session_id}
            </div>
          </div>
        ))}

        {results.length === 0 && !loading && query && (
          <div className="text-center text-gray-500 py-8">未找到匹配结果</div>
        )}
      </div>
    </div>
  );
}
