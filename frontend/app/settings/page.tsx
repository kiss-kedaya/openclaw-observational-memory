"use client";

import { useState } from "react";

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState("http://localhost:3000/api");
  const [saved, setSaved] = useState(false);

  const saveSettings = () => {
    localStorage.setItem("apiUrl", apiUrl);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">系统设置</h1>

      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-xl font-semibold">OpenClaw 集成</h2>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                API 地址
              </label>
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <button
              onClick={saveSettings}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
            >
              {saved ? "已保存 ✓" : "保存设置"}
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-xl font-semibold">数据管理</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                disabled
                className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 disabled:bg-gray-300"
              >
                导入数据
              </button>
              <button
                disabled
                className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
              >
                导出数据
              </button>
              <button
                disabled
                className="bg-orange-500 text-white px-6 py-3 rounded-lg hover:bg-orange-600 disabled:bg-gray-300"
              >
                备份数据
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-xl font-semibold">系统状态</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="text-sm text-gray-500">版本</div>
                <div className="text-lg font-semibold">v1.0.1</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">后端</div>
                <div className="text-lg font-semibold">Rust + Axum</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">前端</div>
                <div className="text-lg font-semibold">Next.js 15</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">数据库</div>
                <div className="text-lg font-semibold">SQLite</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-xl font-semibold">关于</h2>
          </div>
          <div className="p-6">
            <p className="text-gray-600 mb-4">
              观察记忆系统是一个为 AI Agent 设计的记忆管理工具，提供会话管理、观察记录、搜索分析等功能。
            </p>
            <div className="flex space-x-4">
              <a
                href="https://github.com/kiss-kedaya/openclaw-observational-memory"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline"
              >
                GitHub 仓库
              </a>
              <a
                href="https://github.com/kiss-kedaya/openclaw-observational-memory/blob/master/README.md"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline"
              >
                文档
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
