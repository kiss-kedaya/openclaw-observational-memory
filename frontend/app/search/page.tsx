"use client";

import { useState, useEffect } from "react";
import { searchApi } from "@/lib/api";

interface SearchResult {
  observation_id: string;
  session_id: string;
  content: string;
  similarity: number;
  priority: string;
  timestamp: string;
}

interface SavedSearch {
  name: string;
  query: string;
  threshold: number;
  dateFrom: string;
  dateTo: string;
  priority: string;
  useRegex: boolean;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [threshold, setThreshold] = useState(0.7);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [priority, setPriority] = useState<string>("ALL");
  const [useRegex, setUseRegex] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [searchName, setSearchName] = useState("");

  useEffect(() => {
    const history = localStorage.getItem("searchHistory");
    if (history) {
      setSearchHistory(JSON.parse(history));
    }
    const saved = localStorage.getItem("savedSearches");
    if (saved) {
      setSavedSearches(JSON.parse(saved));
    }
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await searchApi.search(query, threshold);
      let filteredResults = res.data;

      if (priority !== "ALL") {
        filteredResults = filteredResults.filter(
          (r: SearchResult) => r.priority === priority
        );
      }

      if (dateFrom) {
        filteredResults = filteredResults.filter(
          (r: SearchResult) => new Date(r.timestamp) >= new Date(dateFrom)
        );
      }

      if (dateTo) {
        filteredResults = filteredResults.filter(
          (r: SearchResult) => new Date(r.timestamp) <= new Date(dateTo)
        );
      }

      if (useRegex) {
        try {
          const regex = new RegExp(query, "i");
          filteredResults = filteredResults.filter((r: SearchResult) =>
            regex.test(r.content)
          );
        } catch (e) {
          alert("正则表达式格式错误");
        }
      }

      setResults(filteredResults);

      const newHistory = [query, ...searchHistory.filter((h) => h !== query)].slice(0, 10);
      setSearchHistory(newHistory);
      localStorage.setItem("searchHistory", JSON.stringify(newHistory));
    } catch (error) {
      console.error("搜索失败:", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const saveSearch = () => {
    if (!searchName.trim()) {
      alert("请输入搜索名称");
      return;
    }

    const newSearch: SavedSearch = {
      name: searchName,
      query,
      threshold,
      dateFrom,
      dateTo,
      priority,
      useRegex,
    };

    const updated = [...savedSearches, newSearch];
    setSavedSearches(updated);
    localStorage.setItem("savedSearches", JSON.stringify(updated));
    setShowSaveDialog(false);
    setSearchName("");
    alert("搜索条件已保存");
  };

  const loadSavedSearch = (search: SavedSearch) => {
    setQuery(search.query);
    setThreshold(search.threshold);
    setDateFrom(search.dateFrom);
    setDateTo(search.dateTo);
    setPriority(search.priority);
    setUseRegex(search.useRegex);
  };

  const deleteSavedSearch = (index: number) => {
    const updated = savedSearches.filter((_, i) => i !== index);
    setSavedSearches(updated);
    localStorage.setItem("savedSearches", JSON.stringify(updated));
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">高级搜索</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">搜索条件</h2>
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

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    开始日期
                  </label>
                  <input
                    type="date"
                    value={dateFrom}
                    onChange={(e) => setDateFrom(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    结束日期
                  </label>
                  <input
                    type="date"
                    value={dateTo}
                    onChange={(e) => setDateTo(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  优先级筛选
                </label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="ALL">全部</option>
                  <option value="HIGH">高</option>
                  <option value="MEDIUM">中</option>
                  <option value="LOW">低</option>
                </select>
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

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="useRegex"
                  checked={useRegex}
                  onChange={(e) => setUseRegex(e.target.checked)}
                  className="mr-2"
                />
                <label htmlFor="useRegex" className="text-sm font-medium">
                  使用正则表达式
                </label>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={handleSearch}
                  disabled={loading || !query.trim()}
                  className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? "搜索中..." : "搜索"}
                </button>
                <button
                  onClick={() => setShowSaveDialog(true)}
                  disabled={!query.trim()}
                  className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  保存搜索
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-xl font-semibold">搜索结果 ({results.length})</h2>
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
              <div className="text-center text-gray-500 py-8">
                未找到匹配结果
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">搜索历史</h2>
            <div className="space-y-2">
              {searchHistory.map((h, i) => (
                <div
                  key={i}
                  onClick={() => setQuery(h)}
                  className="p-2 hover:bg-gray-50 rounded cursor-pointer text-sm"
                >
                  {h}
                </div>
              ))}
              {searchHistory.length === 0 && (
                <div className="text-sm text-gray-500">暂无搜索历史</div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">保存的搜索</h2>
            <div className="space-y-2">
              {savedSearches.map((s, i) => (
                <div
                  key={i}
                  className="p-3 border rounded hover:bg-gray-50"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="font-medium">{s.name}</div>
                    <button
                      onClick={() => deleteSavedSearch(i)}
                      className="text-red-500 text-sm hover:text-red-700"
                    >
                      删除
                    </button>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">{s.query}</div>
                  <button
                    onClick={() => loadSavedSearch(s)}
                    className="text-sm text-blue-500 hover:text-blue-700"
                  >
                    加载
                  </button>
                </div>
              ))}
              {savedSearches.length === 0 && (
                <div className="text-sm text-gray-500">暂无保存的搜索</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {showSaveDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">保存搜索条件</h3>
            <input
              type="text"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              placeholder="输入搜索名称..."
              className="w-full px-4 py-2 border rounded-lg mb-4 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
            <div className="flex space-x-4">
              <button
                onClick={saveSearch}
                className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
              >
                保存
              </button>
              <button
                onClick={() => setShowSaveDialog(false)}
                className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
