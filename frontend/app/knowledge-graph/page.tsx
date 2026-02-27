"use client";

import { useState, useEffect } from "react";

interface Node {
  id: string;
  label: string;
  node_type: string;
  properties: Record<string, string>;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  relation: string;
  weight: number;
}

interface KnowledgeGraph {
  nodes: Node[];
  edges: Edge[];
}

export default function KnowledgeGraphPage() {
  const [graph, setGraph] = useState<KnowledgeGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [relatedNodes, setRelatedNodes] = useState<Node[]>([]);

  useEffect(() => {
    loadGraph();
  }, []);

  const loadGraph = async () => {
    try {
      const res = await fetch("http://localhost:3000/api/knowledge/graph");
      const data = await res.json();
      setGraph(data);
      setLoading(false);
    } catch (error) {
      console.error("Failed to load knowledge graph:", error);
      setLoading(false);
    }
  };

  const loadRelatedEntities = async (nodeId: string) => {
    try {
      const res = await fetch(
        `http://localhost:3000/api/knowledge/related/${nodeId}`
      );
      const data = await res.json();
      setRelatedNodes(data);
    } catch (error) {
      console.error("Failed to load related entities:", error);
    }
  };

  const handleNodeClick = (node: Node) => {
    setSelectedNode(node);
    loadRelatedEntities(node.id);
  };

  const getNodeTypeColor = (type: string) => {
    switch (type) {
      case "Person":
        return "bg-blue-500";
      case "Project":
        return "bg-green-500";
      case "Technology":
        return "bg-purple-500";
      case "Topic":
        return "bg-yellow-500";
      case "Concept":
        return "bg-pink-500";
      default:
        return "bg-gray-500";
    }
  };

  const getNodeTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      Person: "人物",
      Project: "项目",
      Technology: "技术",
      Topic: "主题",
      Concept: "概念",
    };
    return labels[type] || type;
  };

  const getRelationLabel = (relation: string) => {
    const labels: Record<string, string> = {
      WorksOn: "开发",
      Uses: "使用",
      RelatesTo: "关联",
      DependsOn: "依赖",
      Discusses: "讨论",
      Implements: "实现",
    };
    return labels[relation] || relation;
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!graph || graph.nodes.length === 0) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">知识图谱</h1>
        <p className="text-gray-600 dark:text-gray-400">
          暂无数据，请先添加一些对话记录
        </p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">知识图谱</h1>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
            实体数量
          </h3>
          <div className="text-3xl font-bold">{graph.nodes.length}</div>
        </div>
        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
            关系数量
          </h3>
          <div className="text-3xl font-bold">{graph.edges.length}</div>
        </div>
        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
            平均连接度
          </h3>
          <div className="text-3xl font-bold">
            {(graph.edges.length / graph.nodes.length).toFixed(1)}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 实体列表 */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">实体列表</h2>
            
            {/* 按类型分组 */}
            {["Technology", "Project", "Topic", "Person", "Concept"].map(
              (type) => {
                const nodesOfType = graph.nodes.filter(
                  (n) => n.node_type === type
                );
                if (nodesOfType.length === 0) return null;

                return (
                  <div key={type} className="mb-6">
                    <h3 className="font-semibold mb-2 flex items-center gap-2">
                      <span
                        className={`w-3 h-3 rounded-full ${getNodeTypeColor(
                          type
                        )}`}
                      />
                      {getNodeTypeLabel(type)} ({nodesOfType.length})
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {nodesOfType.map((node) => (
                        <button
                          key={node.id}
                          onClick={() => handleNodeClick(node)}
                          className={`px-3 py-1 rounded-full text-sm ${
                            selectedNode?.id === node.id
                              ? "bg-blue-600 text-white"
                              : "bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
                          }`}
                        >
                          {node.label}
                        </button>
                      ))}
                    </div>
                  </div>
                );
              }
            )}
          </div>
        </div>

        {/* 详情面板 */}
        <div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">实体详情</h2>
            
            {selectedNode ? (
              <div>
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`w-4 h-4 rounded-full ${getNodeTypeColor(
                        selectedNode.node_type
                      )}`}
                    />
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {getNodeTypeLabel(selectedNode.node_type)}
                    </span>
                  </div>
                  <h3 className="text-2xl font-bold">{selectedNode.label}</h3>
                </div>

                {/* 相关实体 */}
                {relatedNodes.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold mb-2">
                      相关实体 ({relatedNodes.length})
                    </h4>
                    <div className="space-y-2">
                      {relatedNodes.slice(0, 10).map((node) => (
                        <button
                          key={node.id}
                          onClick={() => handleNodeClick(node)}
                          className="w-full text-left px-3 py-2 bg-gray-50 dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600"
                        >
                          <div className="flex items-center gap-2">
                            <span
                              className={`w-2 h-2 rounded-full ${getNodeTypeColor(
                                node.node_type
                              )}`}
                            />
                            <span className="text-sm">{node.label}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* 关系 */}
                <div>
                  <h4 className="font-semibold mb-2">关系</h4>
                  <div className="space-y-2">
                    {graph.edges
                      .filter(
                        (e) =>
                          e.source === selectedNode.id ||
                          e.target === selectedNode.id
                      )
                      .slice(0, 10)
                      .map((edge) => {
                        const otherNodeId =
                          edge.source === selectedNode.id
                            ? edge.target
                            : edge.source;
                        const otherNode = graph.nodes.find(
                          (n) => n.id === otherNodeId
                        );
                        if (!otherNode) return null;

                        return (
                          <div
                            key={edge.id}
                            className="px-3 py-2 bg-gray-50 dark:bg-gray-700 rounded text-sm"
                          >
                            <span className="font-medium">
                              {getRelationLabel(edge.relation)}
                            </span>
                            <span className="mx-2">→</span>
                            <span>{otherNode.label}</span>
                          </div>
                        );
                      })}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-400">
                点击实体查看详情
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
