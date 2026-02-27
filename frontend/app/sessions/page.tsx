"use client";

import { useState, useEffect } from "react";
import { sessionApi, observationApi } from "@/lib/api";
import type { Session, Observation } from "@/types";

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const res = await sessionApi.list();
      setSessions(res.data);
    } catch (error) {
      console.error("加载会话失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const createSession = async () => {
    const sessionId = `session-${Date.now()}`;
    try {
      await sessionApi.create({
        session_id: sessionId,
        messages: [
          {
            role: "user",
            content: "新会话",
            timestamp: new Date().toISOString(),
          },
        ],
      });
      loadSessions();
    } catch (error) {
      console.error("创建会话失败:", error);
    }
  };

  const viewSession = async (sessionId: string) => {
    setSelectedSession(sessionId);
    try {
      const res = await observationApi.list(sessionId);
      setObservations(res.data);
    } catch (error) {
      console.error("加载观察失败:", error);
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">会话管理</h1>
        <button
          onClick={createSession}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          创建新会话
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8">加载中...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <h2 className="text-xl font-semibold">会话列表</h2>
            </div>
            <div className="divide-y max-h-[600px] overflow-y-auto">
              {sessions.length === 0 ? (
                <div className="p-8 text-center text-gray-500">暂无会话</div>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`p-4 hover:bg-gray-50 cursor-pointer ${
                      selectedSession === session.id ? "bg-blue-50" : ""
                    }`}
                    onClick={() => viewSession(session.id)}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium">{session.id}</div>
                        <div className="text-sm text-gray-500">
                          {new Date(session.created_at).toLocaleString("zh-CN")}
                        </div>
                      </div>
                      <div className="text-right text-sm">
                        <div>{session.message_count} 条消息</div>
                        <div>{session.token_count} tokens</div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <h2 className="text-xl font-semibold">观察记录</h2>
            </div>
            <div className="p-4 max-h-[600px] overflow-y-auto">
              {selectedSession ? (
                observations.length > 0 ? (
                  <div className="space-y-4">
                    {observations.map((obs) => (
                      <div
                        key={obs.id}
                        className="border-l-4 border-blue-500 pl-4"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <span
                            className={`px-2 py-1 rounded text-xs ${
                              obs.priority === "HIGH"
                                ? "bg-red-100 text-red-800"
                                : obs.priority === "MEDIUM"
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-green-100 text-green-800"
                            }`}
                          >
                            {obs.priority === "HIGH"
                              ? "高"
                              : obs.priority === "MEDIUM"
                              ? "中"
                              : "低"}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(obs.created_at).toLocaleString("zh-CN")}
                          </span>
                        </div>
                        <p className="text-gray-700">{obs.content}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    暂无观察记录
                  </div>
                )
              ) : (
                <div className="text-center text-gray-500 py-8">
                  请选择一个会话
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
