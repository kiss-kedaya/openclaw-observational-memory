"use client";

import { useTheme } from "./ThemeProvider";

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();

  return (
    <div className="flex items-center gap-2 p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
      <button
        onClick={() => setTheme("light")}
        className={`p-2 rounded ${
          theme === "light"
            ? "bg-white dark:bg-gray-700 shadow"
            : "hover:bg-gray-200 dark:hover:bg-gray-700"
        }`}
        title="浅色模式"
      >
        ☀️
      </button>
      <button
        onClick={() => setTheme("dark")}
        className={`p-2 rounded ${
          theme === "dark"
            ? "bg-white dark:bg-gray-700 shadow"
            : "hover:bg-gray-200 dark:hover:bg-gray-700"
        }`}
        title="深色模式"
      >
        🌙
      </button>
      <button
        onClick={() => setTheme("system")}
        className={`p-2 rounded ${
          theme === "system"
            ? "bg-white dark:bg-gray-700 shadow"
            : "hover:bg-gray-200 dark:hover:bg-gray-700"
        }`}
        title="跟随系统"
      >
        💻
      </button>
    </div>
  );
}
