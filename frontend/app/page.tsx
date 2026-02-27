"use client";

import { useRouter } from "next/navigation";

import { useState, useEffect } from "react";
import { sessionApi, observationApi } from "@/lib/api";
import type { Session } from "@/types";

export default function Dashboard() {
  const router = useRouter();
  
  useEffect(() => {
    // 检查是否完成首次设置
    const hasCompletedSetup = localStorage.getItem("hasCompletedSetup");
    if (!hasCompletedSetup) {
      router.push("/welcome");
    }
  }, [router]);
  
  const [sessions, setSessions] = useState<Session[]>([]);
  const [stats, setStats] = useState({
    totalSessions: 0,
    totalObservations: 0,
    totaltokens: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const sessionList = await sessionApi.list();
      setSessions(sessionList.data);
      
      const totaltokens = sessionList.data.reduce((sum: number, s: Session) => sum + s.token_count, 0);
      
      let totalObs = 0;
      for (const s of sessionList.data) {
        const obsList = await observationApi.list(s.id);
        totalObs += obsList.data.length;
      }
      
      setStats({
        totalSessions: sessionList.data.length,
        totalObservations: totalObs,
        totaltokens,
      });
    } catch (error) {
      console.error("Failed to load data:", error);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">仪表盘</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">总会话数</h3>
          <p className="text-3xl font-bold mt-2">{stats.totalSessions}</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">总观察数</h3>
          <p className="text-3xl font-bold mt-2">{stats.totalObservations}</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">总 Token 数</h3>
          <p className="text-3xl font-bold mt-2">{stats.totaltokens.toLocaleString()}</p>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-xl font-semibold">最近会话</h2>
        </div>
        <div className="p-6">
          {sessions.length === 0 ? (
            <p className="text-gray-500">暂无会话</p>
          ) : (
            <div className="space-y-4">
              {sessions.slice(0, 5).map((session) => (
                <div key={session.id} className="border-b pb-4 last:border-0">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{session.id}</p>
                      <p className="text-sm text-gray-500">
                        {session.message_count} 条消息 • {session.token_count} tokens
                      </p>
                    </div>
                    <p className="text-sm text-gray-500">
                      {new Date(session.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

