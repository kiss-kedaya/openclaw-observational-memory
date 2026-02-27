"use client";

import { useState, useEffect } from "react";
import { sessionApi, observationApi } from "@/lib/api";
import type { Session } from "@/types";

export default function AnalyticsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [stats, setStats] = useState({
    totalSessions: 0,
    totalObservations: 0,
    totalTokens: 0,
    avgTokensPerSession: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const res = await sessionApi.list();
      const sessionList = res.data;
      setSessions(sessionList);

      const totalTokens = sessionList.reduce(
        (sum: number, s: Session) => sum + s.token_count,
        0
      );

      let totalObs = 0;
      for (const s of sessionList) {
        const obsList = await observationApi.list(s.id);
        totalObs += obsList.data.length;
      }

      setStats({
        totalSessions: sessionList.length,
        totalObservations: totalObs,
        totalTokens,
        avgTokensPerSession:
          sessionList.length > 0 ? totalTokens / sessionList.length : 0,
      });
    } catch (error) {
      console.error("加载数据失败:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">数据分析</h1>

      {loading ? (
        <div className="text-center py-8">加载中...</div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">总会话数</h3>
              <p className="text-3xl font-bold mt-2">{stats.totalSessions}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">总观察数</h3>
              <p className="text-3xl font-bold mt-2">
                {stats.totalObservations}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">总 Token 数</h3>
              <p className="text-3xl font-bold mt-2">
                {stats.totalTokens.toLocaleString()}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm font-medium">
                平均 Token/会话
              </h3>
              <p className="text-3xl font-bold mt-2">
                {Math.round(stats.avgTokensPerSession).toLocaleString()}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <h2 className="text-xl font-semibold">会话趋势</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {sessions.slice(0, 10).map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between"
                  >
                    <div className="flex-1">
                      <div className="text-sm font-medium">{session.id}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(session.created_at).toLocaleString("zh-CN")}
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-sm">
                        <span className="text-gray-500">消息:</span>{" "}
                        {session.message_count}
                      </div>
                      <div className="text-sm">
                        <span className="text-gray-500">Token:</span>{" "}
                        {session.token_count}
                      </div>
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{
                            width: `${Math.min(
                              (session.token_count / stats.totalTokens) * 100 *
                                10,
                              100
                            )}%`,
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
