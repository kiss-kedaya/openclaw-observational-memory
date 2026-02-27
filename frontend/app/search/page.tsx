"use client";

import { useState, useEffect, useCallback, useRef } from "react";
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

// 防抖 Hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// 高亮搜索关键词
function highlightText(text: string, query: string): string {
  if (!query.trim()) return text;
  
  const regex = new RegExp(`(${query})`, 'gi');
  return text.replace(regex, '<mark class="bg-yellow-300 dark:bg-yellow-600">$1</mark>');
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [threshold, setThreshold] = useState(0.2);
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
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  
  const searchInputRef = useRef<HTMLInputElement>(null);
  
  // 防抖搜索
  const debouncedQuery = useDebounce(query, 300);

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

  // 快捷键支持 (Ctrl+K / Cmd+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setShowCommandPalette(true);
        searchInputRef.current?.focus();
      }
      
      if (e.key === 'Escape') {
        setShowCommandPalette(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // 自动搜索（防抖后）
  useEffect(() => {
    if (debouncedQuery.trim()) {
      handleSearch();
    }
  }, [debouncedQuery]);

  const handleSearch = async () => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

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
          console.error("正则表达式格式错误");
        }
      }

      setResults(filteredResults);

      // 更新搜索历史
      if (query.trim()) {
        const newHistory = [query, ...searchHistory.filter((h) => h !== query)].slice(0, 10);
        setSearchHistory(newHistory);
        localStorage.setItem("searchHistory", JSON.stringify(newHistory));
      }
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
  };

  const loadSearch = (search: SavedSearch) => {
    setQuery(search.query);
    setThreshold(search.threshold);
    setDateFrom(search.dateFrom);
    setDateTo(search.dateTo);
    setPriority(search.priority);
    setUseRegex(search.useRegex);
  };

  const deleteSearch = (index: number) => {
    const updated = savedSearches.filter((_, i) => i !== index);
    setSavedSearches(updated);
    localStorage.setItem("savedSearches", JSON.stringify(updated));
  };

  const clearHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem("searchHistory");
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">搜索</h1>

      {/* 快捷键提示 */}
      <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
        提示：按 <kbd className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded">Ctrl+K</kbd> 快速搜索
      </div>

      {/* 搜索框 */}
      <div className="mb-6">
        <div className="relative">
          <input
            ref={searchInputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="输入搜索关键词..."
            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
          />
          {loading && (
            <div className="absolute right-3 top-3">
              <div className="animate-spin h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            </div>
          )}
        </div>

        {/* 搜索历史下拉 */}
        {query.length === 0 && searchHistory.length > 0 && (
          <div className="mt-2 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-semibold">搜索历史</h3>
              <button
                onClick={clearHistory}
                className="text-sm text-red-600 hover:text-red-700"
              >
                清空
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {searchHistory.map((h, i) => (
                <button
                  key={i}
                  onClick={() => setQuery(h)}
                  className="px-3 py-1 bg-white dark:bg-gray-700 rounded-full text-sm hover:bg-gray-100 dark:hover:bg-gray-600"
                >
                  {h}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 高级选项 */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">相似度阈值</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-full"
          />
          <span className="text-sm text-gray-600">{threshold.toFixed(1)}</span>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">优先级</label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
          >
            <option value="ALL">全部</option>
            <option value="HIGH">高</option>
            <option value="MEDIUM">中</option>
            <option value="LOW">低</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">日期范围</label>
          <div className="flex gap-2">
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="flex-1 px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
            />
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="flex-1 px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
            />
          </div>
        </div>
      </div>

      {/* 搜索结果 */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4">
          搜索结果 ({results.length})
        </h2>
        {results.length === 0 && query.trim() && !loading && (
          <p className="text-gray-600 dark:text-gray-400">未找到匹配结果</p>
        )}
        <div className="space-y-4">
          {results.map((result) => (
            <div
              key={result.observation_id}
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
                  相似度: {(result.similarity * 100).toFixed(1)}%
                </span>
              </div>
              <p 
                className="text-gray-800 dark:text-gray-200 mb-2"
                dangerouslySetInnerHTML={{ __html: highlightText(result.content, query) }}
              />
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <span>会话: {result.session_id.substring(0, 8)}...</span>
                <span className="ml-4">
                  {new Date(result.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 保存的搜索 */}
      {savedSearches.length > 0 && (
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">保存的搜索</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {savedSearches.map((search, index) => (
              <div
                key={index}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold">{search.name}</h3>
                  <button
                    onClick={() => deleteSearch(index)}
                    className="text-red-600 hover:text-red-700"
                  >
                    删除
                  </button>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {search.query}
                </p>
                <button
                  onClick={() => loadSearch(search)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  加载搜索
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 保存搜索按钮 */}
      <div className="flex gap-4">
        <button
          onClick={() => setShowSaveDialog(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          保存当前搜索
        </button>
      </div>

      {/* 保存对话框 */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-md w-full">
            <h3 className="text-xl font-semibold mb-4">保存搜索</h3>
            <input
              type="text"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              placeholder="输入搜索名称..."
              className="w-full px-4 py-2 border rounded-lg mb-4 dark:bg-gray-700 dark:border-gray-600"
            />
            <div className="flex gap-4">
              <button
                onClick={saveSearch}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                保存
              </button>
              <button
                onClick={() => setShowSaveDialog(false)}
                className="flex-1 px-4 py-2 bg-gray-300 dark:bg-gray-600 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500"
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
