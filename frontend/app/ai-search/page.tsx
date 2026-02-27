"use client";

import { useState, useEffect } from "react";

interface SearchResult {
  id: string;
  session_id: string;
  content: string;
  similarity: number;
  priority: string;
}

export default function AISearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  // 获取搜索建议
  useEffect(() => {
    if (query.length > 2) {
      fetchSuggestions();
    } else {
      setSuggestions([]);
    }
  }, [query]);

  const fetchSuggestions = async () => {
    try {
      const res = await fetch("http://localhost:3000/api/ai/suggestions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, threshold: 0.2 }),
      });
      const data = await res.json();
      setSuggestions(data);
    } catch (error) {
      console.error("Failed to fetch suggestions:", error);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await fetch("http://localhost:3000/api/ai/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, threshold: 0.2 }),
      });
      const data = await res.json();
      setResults(data);
    } catch (error) {
      console.error("Search failed:", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">AI 智能搜索</h1>

      {/* 搜索框 */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
            placeholder="用自然语言描述你想找的内容，例如：上周关于 Rust 的讨论"
            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
          />
          {loading && (
            <div className="absolute right-3 top-3">
              <div className="animate-spin h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            </div>
          )}
        </div>

        {/* 搜索建议 */}
        {suggestions.length > 0 && (
          <div className="mt-2 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h3 className="font-semibold mb-2">搜索建议</h3>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setQuery(s);
                    handleSearch();
                  }}
                  className="px-3 py-1 bg-white dark:bg-gray-700 rounded-full text-sm hover:bg-gray-100 dark:hover:bg-gray-600"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        <button
          onClick={handleSearch}
          disabled={!query.trim() || loading}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? "搜索中..." : "搜索"}
        </button>
      </div>

      {/* 示例查询 */}
      <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
        <h3 className="font-semibold mb-2">示例查询</h3>
        <div className="space-y-2 text-sm">
          <p className="text-gray-700 dark:text-gray-300">
            • "上周关于 Rust 的讨论"
          </p>
          <p className="text-gray-700 dark:text-gray-300">
            • "最近的 Bug 修复"
          </p>
          <p className="text-gray-700 dark:text-gray-300">
            • "项目进度相关的对话"
          </p>
          <p className="text-gray-700 dark:text-gray-300">
            • "总结一下本周的工作"
          </p>
        </div>
      </div>

      {/* 搜索结果 */}
      <div>
        <h2 className="text-xl font-semibold mb-4">
          搜索结果 ({results.length})
        </h2>
        {results.length === 0 && query.trim() && !loading && (
          <p className="text-gray-600 dark:text-gray-400">未找到匹配结果</p>
        )}
        <div className="space-y-4">
          {results.map((result) => (
            <div
              key={result.id}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow"
            >
              <div className="flex justify-between items-start mb-2">
                <span
                  className={`px-2 py-1 rounded text-xs ${
                    result.priority === "HIGH"
                      ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                      : result.priority === "MEDIUM"
                      ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                      : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                  }`}
                >
                  {result.priority}
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  相关度: {(result.similarity * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-gray-800 dark:text-gray-200 mb-2">
                {result.content}
              </p>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <span>会话: {result.session_id.substring(0, 8)}...</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
