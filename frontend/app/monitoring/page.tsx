"use client";

import { useState, useEffect } from "react";

interface PerformanceMetrics {
  cpu_usage: number;
  memory_usage: number;
  memory_total: number;
  memory_percent: number;
  db_size: number;
  uptime: number;
  process_count: number;
}

interface HealthStatus {
  status: string;
  database: boolean;
  memory: boolean;
  disk: boolean;
}

export default function MonitoringPage() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // 每 5 秒刷新
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [metricsRes, healthRes] = await Promise.all([
        fetch("http://localhost:3000/api/monitoring/metrics"),
        fetch("http://localhost:3000/api/monitoring/health"),
      ]);

      const metricsData = await metricsRes.json();
      const healthData = await healthRes.json();

      setMetrics(metricsData);
      setHealth(healthData);
      setLoading(false);
    } catch (error) {
      console.error("Failed to load monitoring data:", error);
      setLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}h ${minutes}m ${secs}s`;
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">性能监控</h1>

      {/* 健康状态 */}
      {health && (
        <div className="mb-6 p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">系统健康</h2>
          <div className="flex items-center gap-4">
            <div
              className={`px-4 py-2 rounded-full text-white font-semibold ${
                health.status === "healthy"
                  ? "bg-green-500"
                  : "bg-red-500"
              }`}
            >
              {health.status === "healthy" ? "✓ 健康" : "✗ 异常"}
            </div>
            <div className="flex gap-4">
              <span className={health.database ? "text-green-600" : "text-red-600"}>
                数据库: {health.database ? "✓" : "✗"}
              </span>
              <span className={health.memory ? "text-green-600" : "text-red-600"}>
                内存: {health.memory ? "✓" : "✗"}
              </span>
              <span className={health.disk ? "text-green-600" : "text-red-600"}>
                磁盘: {health.disk ? "✓" : "✗"}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 性能指标 */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {/* CPU 使用率 */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              CPU 使用率
            </h3>
            <div className="text-3xl font-bold mb-2">
              {metrics.cpu_usage.toFixed(1)}%
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${Math.min(metrics.cpu_usage, 100)}%` }}
              />
            </div>
          </div>

          {/* 内存使用 */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              内存使用
            </h3>
            <div className="text-3xl font-bold mb-2">
              {formatBytes(metrics.memory_usage)}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              总计: {formatBytes(metrics.memory_total)}
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all"
                style={{ width: `${metrics.memory_percent}%` }}
              />
            </div>
          </div>

          {/* 数据库大小 */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              数据库大小
            </h3>
            <div className="text-3xl font-bold">
              {formatBytes(metrics.db_size)}
            </div>
          </div>

          {/* 运行时间 */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              运行时间
            </h3>
            <div className="text-3xl font-bold">
              {formatUptime(metrics.uptime)}
            </div>
          </div>

          {/* 进程数 */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              系统进程数
            </h3>
            <div className="text-3xl font-bold">{metrics.process_count}</div>
          </div>
        </div>
      )}

      {/* 刷新提示 */}
      <div className="text-sm text-gray-600 dark:text-gray-400 text-center">
        数据每 5 秒自动刷新
      </div>
    </div>
  );
}
