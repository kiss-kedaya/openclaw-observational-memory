"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "仪表盘" },
  { href: "/sessions", label: "会话" },
  { href: "/search", label: "搜索" },
  { href: "/analytics", label: "分析" },
  { href: "/tools", label: "工具" },
  { href: "/memory", label: "记忆" },
  { href: "/settings", label: "设置" },
];

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${
                  pathname === item.href
                    ? "text-gray-900 border-b-2 border-blue-500"
                    : "text-gray-500 hover:text-gray-900"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
