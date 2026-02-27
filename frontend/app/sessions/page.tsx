"use client";

import { useState, useEffect } from "react";
import { sessionApi, observationApi } from "@/lib/api";
import type { Session, Observation } from "@/types";

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSessions, setSelectedSessions] = useState<string[]>([]);
  const [showArchived, setShowArchived] = useState(false);
  const [filterTag, setFilterTag] = useState<string>("ALL");
  const [filterGroup, setFilterGroup] = useState<string>("ALL");
  const [allTags, setAllTags] = useState<string[]>([]);
  const [allGroups, setAllGroups] = useState<string[]>([]);
  const [showTagDialog, setShowTagDialog] = useState(false);
  const [showGroupDialog, setShowGroupDialog] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string>("");
  const [newTag, setNewTag] = useState("");
  const [newGroup, setNewGroup] = useState("");

  useEffect(() => {
    loadSessions();
    const interval = setInterval(loadSessions, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    extractTagsAndGroups();
  }, [sessions]);

  const extractTagsAndGroups = () => {
    const tags = new Set<string>();
    const groups = new Set<string>();
    sessions.forEach((s) => {
      if (s.tags) {
        try {
          const sessionTags = JSON.parse(s.tags);
          sessionTags.forEach((t: string) => tags.add(t));
        } catch (e) {}
      }
      if (s.group_name) {
        groups.add(s.group_name);
      }
    });
    setAllTags(Array.from(tags));
    setAllGroups(Array.from(groups));
  };

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

  const toggleSelectSession = (sessionId: string) => {
    setSelectedSessions((prev) =>
      prev.includes(sessionId)
        ? prev.filter((id) => id !== sessionId)
        : [...prev, sessionId]
    );
  };

  const openTagDialog = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    setShowTagDialog(true);
  };

  const openGroupDialog = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    setShowGroupDialog(true);
  };

  const addTag = async () => {
    if (!newTag.trim()) return;
    try {
      await sessionApi.addTag(currentSessionId, newTag.trim());
      setNewTag("");
      setShowTagDialog(false);
      loadSessions();
    } catch (error) {
      console.error("添加标签失败:", error);
    }
  };

  const removeTag = async (sessionId: string, tag: string) => {
    try {
      await sessionApi.removeTag(sessionId, tag);
      loadSessions();
    } catch (error) {
      console.error("删除标签失败:", error);
    }
  };

  const setGroup = async () => {
    if (!newGroup.trim()) return;
    try {
      await sessionApi.setGroup(currentSessionId, newGroup.trim());
      setNewGroup("");
      setShowGroupDialog(false);
      loadSessions();
    } catch (error) {
      console.error("设置分组失败:", error);
    }
  };

  const archiveSession = async (sessionId: string) => {
    try {
      await sessionApi.archive(sessionId);
      loadSessions();
    } catch (error) {
      console.error("归档失败:", error);
    }
  };

  const unarchiveSession = async (sessionId: string) => {
    try {
      await sessionApi.unarchive(sessionId);
      loadSessions();
    } catch (error) {
      console.error("取消归档失败:", error);
    }
  };

  const batchArchive = async () => {
    for (const id of selectedSessions) {
      await archiveSession(id);
    }
    setSelectedSessions([]);
  };

  const filteredSessions = sessions.filter((s) => {
    if (!showArchived && s.archived === 1) return false;
    if (filterTag !== "ALL") {
      try {
        const tags = JSON.parse(s.tags || "[]");
        if (!tags.includes(filterTag)) return false;
      } catch (e) {
        return false;
      }
    }
    if (filterGroup !== "ALL" && s.group_name !== filterGroup) return false;
    return true;
  });

  const getSessionTags = (session: Session): string[] => {
    try {
      return JSON.parse(session.tags || "[]");
    } catch (e) {
      return [];
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">加载中...</div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">会话管理</h1>
        <button
          onClick={createSession}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
        >
          创建新会话
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-4 items-center">
          <select
            value={filterTag}
            onChange={(e) => setFilterTag(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          >
            <option value="ALL">所有标签</option>
            {allTags.map((tag) => (
              <option key={tag} value={tag}>
                {tag}
              </option>
            ))}
          </select>

          <select
            value={filterGroup}
            onChange={(e) => setFilterGroup(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          >
            <option value="ALL">所有分组</option>
            {allGroups.map((group) => (
              <option key={group} value={group}>
                {group}
              </option>
            ))}
          </select>

          <label className="flex items-center">
            <input
              type="checkbox"
              checked={showArchived}
              onChange={(e) => setShowArchived(e.target.checked)}
              className="mr-2"
            />
            显示归档
          </label>
        </div>
      </div>

      {selectedSessions.length > 0 && (
        <div className="bg-blue-50 rounded-lg p-4 mb-6">
          <div className="flex gap-4 items-center">
            <span>已选择 {selectedSessions.length} 个会话</span>
            <button
              onClick={batchArchive}
              className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors"
            >
              批量归档
            </button>
            <button
              onClick={() => setSelectedSessions([])}
              className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors"
            >
              取消选择
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4">
        {filteredSessions.map((session) => (
          <div
            key={session.id}
            className={`bg-white rounded-lg shadow p-6 ${
              session.archived === 1 ? "opacity-60" : ""
            }`}
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-4">
                <input
                  type="checkbox"
                  checked={selectedSessions.includes(session.id)}
                  onChange={() => toggleSelectSession(session.id)}
                  className="w-4 h-4"
                />
                <div>
                  <h3 className="text-lg font-semibold">{session.id}</h3>
                  <p className="text-sm text-gray-500">
                    创建于: {new Date(session.created_at).toLocaleString("zh-CN")}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => viewSession(session.id)}
                  className="text-blue-500 hover:text-blue-700 text-sm"
                >
                  查看详情
                </button>
                <button
                  onClick={() => openTagDialog(session.id)}
                  className="text-green-500 hover:text-green-700 text-sm"
                >
                  添加标签
                </button>
                <button
                  onClick={() => openGroupDialog(session.id)}
                  className="text-purple-500 hover:text-purple-700 text-sm"
                >
                  设置分组
                </button>
                {session.archived === 1 ? (
                  <button
                    onClick={() => unarchiveSession(session.id)}
                    className="text-orange-500 hover:text-orange-700 text-sm"
                  >
                    取消归档
                  </button>
                ) : (
                  <button
                    onClick={() => archiveSession(session.id)}
                    className="text-orange-500 hover:text-orange-700 text-sm"
                  >
                    归档
                  </button>
                )}
              </div>
            </div>

            <div className="flex gap-2 mb-2">
              {getSessionTags(session).map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs flex items-center gap-1"
                >
                  {tag}
                  <button
                    onClick={() => removeTag(session.id, tag)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>

            {session.group_name && (
              <div className="text-sm text-gray-600">
                分组: {session.group_name}
              </div>
            )}

            <div className="mt-2 text-sm text-gray-600">
              消息数: {session.message_count} | Token 数: {session.token_count}
            </div>
          </div>
        ))}
      </div>

      {showTagDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">添加标签</h3>
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="输入标签名称..."
              className="w-full px-4 py-2 border rounded-lg mb-4 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
            <div className="flex gap-4">
              <button
                onClick={addTag}
                className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
              >
                添加
              </button>
              <button
                onClick={() => setShowTagDialog(false)}
                className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {showGroupDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">设置分组</h3>
            <input
              type="text"
              value={newGroup}
              onChange={(e) => setNewGroup(e.target.value)}
              placeholder="输入分组名称..."
              className="w-full px-4 py-2 border rounded-lg mb-4 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
            <div className="flex gap-4">
              <button
                onClick={setGroup}
                className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
              >
                设置
              </button>
              <button
                onClick={() => setShowGroupDialog(false)}
                className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {selectedSession && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-3/4 max-h-3/4 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">会话详情: {selectedSession}</h3>
              <button
                onClick={() => setSelectedSession(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                关闭
              </button>
            </div>
            <div className="space-y-4">
              {observations.map((obs) => (
                <div key={obs.id} className="border-l-4 border-blue-500 pl-4">
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
                    <span className="text-sm text-gray-500">
                      {new Date(obs.created_at).toLocaleString("zh-CN")}
                    </span>
                  </div>
                  <p className="text-gray-700">{obs.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
