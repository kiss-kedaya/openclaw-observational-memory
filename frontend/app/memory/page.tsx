"use client";

import { useState } from "react";

interface CompressionResult {
  original_count: number;
  compressed_count: number;
  removed_count: number;
  compression_ratio: number;
}

interface Cluster {
  topic: string;
  count: number;
  observations: string[];
}

export default function MemoryPage() {
  const [compressionResult, setCompressionResult] =
    useState<CompressionResult | null>(null);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(false);

  const compressMemory = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:3000/api/memory/compress", {
        method: "POST",
      });
      const data = await res.json();
      setCompressionResult(data);
    } catch (error) {
      console.error("压缩失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadClusters = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:3000/api/memory/clusters");
      const data = await res.json();
      setClusters(data);
    } catch (error) {
      console.error("加载聚类失败:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">记忆管理</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <button
          onClick={compressMemory}
          disabled={loading}
          className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
        >
          压缩记忆
        </button>
        <button
          onClick={loadClusters}
          disabled={loading}
          className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 disabled:bg-gray-300"
        >
          查看聚类
        </button>
        <button
          disabled
          className="bg-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-600 disabled:bg-gray-300"
        >
          高级搜索
        </button>
        <button
          disabled
          className="bg-orange-500 text-white px-6 py-3 rounded-lg hover:bg-orange-600 disabled:bg-gray-300"
        >
          导出数据
        </button>
      </div>

      {compressionResult && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">压缩结果</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-500">原始数量</div>
              <div className="text-2xl font-bold">
                {compressionResult.original_count}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">压缩后数量</div>
              <div className="text-2xl font-bold">
                {compressionResult.compressed_count}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">删除数量</div>
              <div className="text-2xl font-bold text-red-600">
                {compressionResult.removed_count}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">压缩率</div>
              <div className="text-2xl font-bold text-green-600">
                {(compressionResult.compression_ratio * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {clusters.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-xl font-semibold">主题聚类</h2>
          </div>
          <div className="divide-y">
            {clusters.map((cluster, index) => (
              <div key={index} className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">{cluster.topic}</h3>
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {cluster.count} 条观察
                  </span>
                </div>
                <div className="space-y-2">
                  {cluster.observations.slice(0, 3).map((obs, i) => (
                    <div
                      key={i}
                      className="text-sm text-gray-600 border-l-2 border-gray-300 pl-3"
                    >
                      {obs}
                    </div>
                  ))}
                  {cluster.observations.length > 3 && (
                    <div className="text-sm text-gray-500 pl-3">
                      还有 {cluster.observations.length - 3} 条...
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!compressionResult && clusters.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
          点击上方按钮开始管理记忆
        </div>
      )}
    </div>
  );
}
