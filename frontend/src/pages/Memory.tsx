import { useState } from "react";

export default function Memory() {
  const [compressing, setCompressing] = useState(false);
  const [compressionResult, setCompressionResult] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchPriority, setSearchPriority] = useState("ALL");
  const [useRegex, setUseRegex] = useState(false);

  const handleCompress = async () => {
    setCompressing(true);
    // Simulate compression
    setTimeout(() => {
      setCompressionResult({
        original: 150,
        compressed: 120,
        removed: 30,
        ratio: 0.2,
      });
      setCompressing(false);
    }, 2000);
  };

  const clusters = {
    "工具": ["安装了 agent-browser", "配置 web_search API"],
    "错误": ["ImportError 修复", "编译错误解决"],
    "配置": ["更新 Cargo.toml", "修改 vite.config.ts"],
    "UI": ["实现 Dashboard 页面", "添加 Analytics 图表"],
    "数据": ["导出 JSON 格式", "创建备份"],
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Memory Optimization</h1>

      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex -mb-px">
            {["Compress", "Clustering", "Search", "Export"].map((tab) => (
              <button
                key={tab}
                className="px-6 py-3 border-b-2 border-transparent hover:border-blue-500 transition"
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Compress Tab */}
          <div className="space-y-4">
            <h2 className="text-xl font-bold">Observation Compression</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Remove duplicate and redundant observations to optimize storage.
            </p>

            <button
              onClick={handleCompress}
              disabled={compressing}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              {compressing ? "Compressing..." : "Compress Now"}
            </button>

            {compressionResult && (
              <div className="mt-4 p-4 bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg">
                <div className="font-bold text-green-800 dark:text-green-200 mb-2">
                  Compression Complete!
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-gray-600 dark:text-gray-400">Original</div>
                    <div className="text-xl font-bold">{compressionResult.original}</div>
                  </div>
                  <div>
                    <div className="text-gray-600 dark:text-gray-400">Compressed</div>
                    <div className="text-xl font-bold">{compressionResult.compressed}</div>
                  </div>
                  <div>
                    <div className="text-gray-600 dark:text-gray-400">Removed</div>
                    <div className="text-xl font-bold text-red-500">
                      {compressionResult.removed}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-600 dark:text-gray-400">Ratio</div>
                    <div className="text-xl font-bold">
                      {(compressionResult.ratio * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Clustering Section */}
          <div className="mt-8 space-y-4">
            <h2 className="text-xl font-bold">Topic Clustering</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Observations grouped by topic using keyword analysis.
            </p>

            <div className="space-y-3">
              {Object.entries(clusters).map(([topic, observations]) => (
                <div
                  key={topic}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <button className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition">
                    <span className="font-medium">
                      {topic} ({observations.length})
                    </span>
                    <span className="text-gray-400">▼</span>
                  </button>
                  <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
                    {observations.map((obs, i) => (
                      <div
                        key={i}
                        className="text-sm text-gray-600 dark:text-gray-400"
                      >
                        • {obs}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Advanced Search */}
          <div className="mt-8 space-y-4">
            <h2 className="text-xl font-bold">Advanced Search</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Search Query
                </label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter search query..."
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Priority Filter
                  </label>
                  <select
                    value={searchPriority}
                    onChange={(e) => setSearchPriority(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                  >
                    <option value="ALL">All</option>
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </select>
                </div>

                <div className="flex items-center">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={useRegex}
                      onChange={(e) => setUseRegex(e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm">Use Regular Expression</span>
                  </label>
                </div>
              </div>

              <button className="w-full px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
                Search
              </button>
            </div>
          </div>

          {/* Export Options */}
          <div className="mt-8 space-y-4">
            <h2 className="text-xl font-bold">Export Options</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 transition text-left">
                <div className="font-bold mb-1">Markdown</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Human-readable format
                </div>
              </button>

              <button className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 transition text-left">
                <div className="font-bold mb-1">Knowledge Graph (JSON-LD)</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Structured data format
                </div>
              </button>

              <button className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 transition text-left">
                <div className="font-bold mb-1">Timeline HTML</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Interactive timeline view
                </div>
              </button>

              <button className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 transition text-left">
                <div className="font-bold mb-1">Mind Map</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  FreeMind/XMind format
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
