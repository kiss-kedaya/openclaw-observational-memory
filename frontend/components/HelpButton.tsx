"use client";

import { useState } from "react";

interface HelpItem {
  title: string;
  content: string;
}

const helpItems: HelpItem[] = [
  {
    title: "如何开始？",
    content: "首次使用请访问欢迎页面（/welcome），按照向导完成初始设置。",
  },
  {
    title: "如何搜索？",
    content: "在搜索页面输入关键词，支持自然语言查询。例如：'上周关于项目的讨论'。",
  },
  {
    title: "什么是知识图谱？",
    content: "知识图谱展示实体（人物、项目、技术）之间的关系，帮助你理解对话中的知识结构。",
  },
  {
    title: "如何查看会话？",
    content: "在会话页面可以查看所有对话记录，支持按标签、分组筛选。",
  },
  {
    title: "性能监控是什么？",
    content: "监控页面显示系统运行状态、资源使用情况和健康检查结果。",
  },
];

export default function HelpButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* 帮助按钮 */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center z-50 transition-all"
        title="帮助"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </button>

      {/* 帮助面板 */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            {/* 标题栏 */}
            <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
              <h2 className="text-2xl font-bold">使用帮助</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* 内容 */}
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="space-y-6">
                {helpItems.map((item, index) => (
                  <div key={index}>
                    <h3 className="text-lg font-semibold mb-2">
                      {item.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      {item.content}
                    </p>
                  </div>
                ))}

                {/* 快速链接 */}
                <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                  <h3 className="text-lg font-semibold mb-3">快速链接</h3>
                  <div className="grid grid-cols-2 gap-2">
                    <a
                      href="/welcome"
                      className="px-4 py-2 bg-white dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 text-center"
                    >
                      欢迎向导
                    </a>
                    <a
                      href="/search"
                      className="px-4 py-2 bg-white dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 text-center"
                    >
                      搜索
                    </a>
                    <a
                      href="/sessions"
                      className="px-4 py-2 bg-white dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 text-center"
                    >
                      会话
                    </a>
                    <a
                      href="/knowledge-graph"
                      className="px-4 py-2 bg-white dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 text-center"
                    >
                      知识图谱
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
