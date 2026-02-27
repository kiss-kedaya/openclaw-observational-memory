"use client";

import { useState, useEffect } from "react";
import { toolsApi } from "@/lib/api";

interface ToolSuggestion {
  tool: string;
  reason: string;
  confidence: number;
  context: string;
  timestamp: string;
}

export default function ToolsPage() {
  const [suggestions, setSuggestions] = useState<ToolSuggestion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    try {
      const res = await toolsApi.suggestions();
      setSuggestions(res.data);
    } catch (error) {
      console.error("加载工具建议失败:", error);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">工具建议</h1>

      {loading ? (
        <div className="text-center py-8">加载中...</div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">总建议数</h3>
              <p className="text-3xl font-bold mt-2">{suggestions.length}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">平均置信度</h3>
              <p className="text-3xl font-bold mt-2">
                {suggestions.length > 0
                  ? (
                      (suggestions.reduce((sum, s) => sum + s.confidence, 0) /
                        suggestions.length) *
                      100
                    ).toFixed(1)
                  : 0}
                %
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">工具类型</h3>
              <p className="text-3xl font-bold mt-2">
                {new Set(suggestions.map((s) => s.tool)).size}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <h2 className="text-xl font-semibold">最近建议</h2>
            </div>
            <div className="divide-y">
              {suggestions.length === 0 ? (
                <div className="p-8 text-center text-gray-500">暂无建议</div>
              ) : (
                suggestions.map((suggestion, index) => (
                  <div key={index} className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                          {suggestion.tool}
                        </span>
                        <span className="ml-2 text-sm text-gray-500">
                          置信度: {(suggestion.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <span className="text-sm text-gray-500">
                        {new Date(suggestion.timestamp).toLocaleString("zh-CN")}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-2">{suggestion.reason}</p>
                    <div className="text-sm text-gray-500 bg-gray-50 p-3 rounded">
                      上下文: {suggestion.context}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
