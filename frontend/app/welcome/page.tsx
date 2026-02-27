"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function WelcomePage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [config, setConfig] = useState({
    dbPath: "./memory.db",
    port: 3000,
    autoStart: true,
  });

  useEffect(() => {
    // 检查是否已经完成首次设置
    const hasCompletedSetup = localStorage.getItem("hasCompletedSetup");
    if (hasCompletedSetup === "true") {
      router.push("/");
    }
  }, [router]);

  const completeSetup = () => {
    localStorage.setItem("hasCompletedSetup", "true");
    router.push("/");
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">
              欢迎使用 Observational Memory
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
              AI Agent 的智能记忆管理系统
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
                <div className="text-4xl mb-4">📝</div>
                <h3 className="text-lg font-semibold mb-2">自动记录</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  自动记录所有对话，不遗漏任何信息
                </p>
              </div>
              <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
                <div className="text-4xl mb-4">🔍</div>
                <h3 className="text-lg font-semibold mb-2">智能搜索</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  语义搜索，快速找到历史对话
                </p>
              </div>
              <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
                <div className="text-4xl mb-4">📊</div>
                <h3 className="text-lg font-semibold mb-2">数据分析</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  可视化分析，洞察对话模式
                </p>
              </div>
            </div>
            <button
              onClick={() => setStep(2)}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-lg"
            >
              开始设置
            </button>
          </div>
        );

      case 2:
        return (
          <div>
            <h2 className="text-2xl font-bold mb-6">系统配置</h2>
            <div className="space-y-6 mb-8">
              <div>
                <label className="block text-sm font-medium mb-2">
                  数据库路径
                </label>
                <input
                  type="text"
                  value={config.dbPath}
                  onChange={(e) =>
                    setConfig({ ...config, dbPath: e.target.value })
                  }
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                />
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  数据库文件存储位置
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  服务端口
                </label>
                <input
                  type="number"
                  value={config.port}
                  onChange={(e) =>
                    setConfig({ ...config, port: parseInt(e.target.value) })
                  }
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                />
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  API 服务监听端口
                </p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.autoStart}
                  onChange={(e) =>
                    setConfig({ ...config, autoStart: e.target.checked })
                  }
                  className="mr-2"
                />
                <label className="text-sm font-medium">
                  开机自动启动
                </label>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setStep(1)}
                className="px-6 py-2 bg-gray-300 dark:bg-gray-600 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500"
              >
                上一步
              </button>
              <button
                onClick={() => setStep(3)}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                下一步
              </button>
            </div>
          </div>
        );

      case 3:
        return (
          <div>
            <h2 className="text-2xl font-bold mb-6">快速入门</h2>
            <div className="space-y-6 mb-8">
              <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                <h3 className="font-semibold mb-2">1. 自动记录对话</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Observational Memory 会自动记录 OpenClaw 的所有对话。
                  无需手动操作，所有对话都会被保存到数据库中。
                </p>
              </div>

              <div className="p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                <h3 className="font-semibold mb-2">2. 搜索历史对话</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  使用搜索功能快速找到历史对话。支持语义搜索、关键词搜索、
                  正则表达式搜索等多种方式。按 Ctrl+K 快速打开搜索。
                </p>
              </div>

              <div className="p-4 bg-purple-50 dark:bg-purple-900 rounded-lg">
                <h3 className="font-semibold mb-2">3. 查看数据分析</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  在分析页面查看对话统计、优先级分布、时间趋势等数据可视化。
                  了解你的对话模式和习惯。
                </p>
              </div>

              <div className="p-4 bg-yellow-50 dark:bg-yellow-900 rounded-lg">
                <h3 className="font-semibold mb-2">4. 管理会话</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  在会话页面查看所有会话，添加标签、分组、归档等操作。
                  保持你的记忆井然有序。
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setStep(2)}
                className="px-6 py-2 bg-gray-300 dark:bg-gray-600 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500"
              >
                上一步
              </button>
              <button
                onClick={() => setStep(4)}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                下一步
              </button>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="text-center">
            <div className="text-6xl mb-6">🎉</div>
            <h2 className="text-3xl font-bold mb-4">设置完成！</h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
              Observational Memory 已经准备就绪
            </p>
            <div className="mb-8 p-6 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h3 className="font-semibold mb-4">配置摘要</h3>
              <div className="text-left space-y-2">
                <p>
                  <span className="font-medium">数据库路径:</span>{" "}
                  {config.dbPath}
                </p>
                <p>
                  <span className="font-medium">服务端口:</span> {config.port}
                </p>
                <p>
                  <span className="font-medium">自动启动:</span>{" "}
                  {config.autoStart ? "是" : "否"}
                </p>
              </div>
            </div>
            <div className="space-y-4">
              <button
                onClick={completeSetup}
                className="w-full px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-lg"
              >
                开始使用
              </button>
              <button
                onClick={() => setStep(1)}
                className="w-full px-8 py-3 bg-gray-300 dark:bg-gray-600 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500"
              >
                重新设置
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-4xl w-full bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-8">
        {/* 进度指示器 */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            {[1, 2, 3, 4].map((s) => (
              <div
                key={s}
                className={`flex-1 h-2 rounded-full mx-1 ${
                  s <= step
                    ? "bg-blue-600"
                    : "bg-gray-300 dark:bg-gray-700"
                }`}
              />
            ))}
          </div>
          <div className="flex justify-between mt-2 text-sm text-gray-600 dark:text-gray-400">
            <span>欢迎</span>
            <span>配置</span>
            <span>教程</span>
            <span>完成</span>
          </div>
        </div>

        {/* 步骤内容 */}
        {renderStep()}
      </div>
    </div>
  );
}
