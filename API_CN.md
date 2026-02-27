# API 文档

[English](API.md) | 简体中文

## 基础信息

- **Base URL**: `http://localhost:3000/api`
- **Content-Type**: `application/json`
- **编码**: UTF-8

## 会话 API

### 获取所有会话

```http
GET /sessions
```

**响应示例**:
```json
[
  {
    "id": "session-001",
    "created_at": "2026-02-27T08:00:00Z",
    "updated_at": "2026-02-27T08:00:00Z",
    "message_count": 10,
    "token_count": 1000
  }
]
```

### 创建会话

```http
POST /sessions
```

**请求体**:
```json
{
  "session_id": "session-001",
  "messages": [
    {
      "role": "user",
      "content": "你好",
      "timestamp": "2026-02-27T08:00:00Z"
    },
    {
      "role": "assistant",
      "content": "你好！有什么可以帮助你的吗？",
      "timestamp": "2026-02-27T08:00:01Z"
    }
  ]
}
```

**响应示例**:
```json
{
  "session": {
    "id": "session-001",
    "created_at": "2026-02-27T08:00:00Z",
    "updated_at": "2026-02-27T08:00:00Z",
    "message_count": 2,
    "token_count": 20
  },
  "observations": [
    "用户发起对话",
    "助手响应问候"
  ]
}
```

### 获取单个会话

```http
GET /sessions/:id
```

**路径参数**:
- `id`: 会话 ID

**响应示例**:
```json
{
  "id": "session-001",
  "created_at": "2026-02-27T08:00:00Z",
  "updated_at": "2026-02-27T08:00:00Z",
  "message_count": 10,
  "token_count": 1000
}
```

## 观察 API

### 获取会话的观察记录

```http
GET /observations/:session_id
```

**路径参数**:
- `session_id`: 会话 ID

**响应示例**:
```json
[
  {
    "id": "obs-001",
    "session_id": "session-001",
    "content": "用户喜欢使用 Rust 编程",
    "priority": "HIGH",
    "created_at": "2026-02-27T08:00:00Z"
  },
  {
    "id": "obs-002",
    "session_id": "session-001",
    "content": "用户询问了 Next.js 相关问题",
    "priority": "MEDIUM",
    "created_at": "2026-02-27T08:05:00Z"
  }
]
```

**优先级说明**:
- `HIGH`: 高优先级 - 重要信息
- `MEDIUM`: 中优先级 - 一般信息
- `LOW`: 低优先级 - 次要信息

## 搜索 API

### 搜索观察

```http
POST /search
```

**请求体**:
```json
{
  "query": "Rust 编程",
  "threshold": 0.7
}
```

**参数说明**:
- `query`: 搜索关键词
- `threshold`: 相似度阈值（0-1），默认 0.7

**响应示例**:
```json
[
  {
    "observation_id": "obs-001",
    "session_id": "session-001",
    "content": "用户喜欢使用 Rust 编程",
    "similarity": 0.95,
    "priority": "HIGH",
    "timestamp": "2026-02-27T08:00:00Z"
  },
  {
    "observation_id": "obs-003",
    "session_id": "session-002",
    "content": "讨论了 Rust 的性能优势",
    "similarity": 0.82,
    "priority": "MEDIUM",
    "timestamp": "2026-02-27T09:00:00Z"
  }
]
```

## 工具 API

### 获取工具建议

```http
GET /tools/suggestions
```

**响应示例**:
```json
[
  {
    "tool": "agent-browser",
    "reason": "检测到需要浏览器自动化",
    "confidence": 0.85,
    "context": "用户提到需要抓取网页数据",
    "timestamp": "2026-02-27T08:00:00Z"
  },
  {
    "tool": "web_search",
    "reason": "检测到搜索需求",
    "confidence": 0.78,
    "context": "用户询问最新的技术资讯",
    "timestamp": "2026-02-27T08:05:00Z"
  }
]
```

**支持的工具**:
- `agent-reach`: 社交媒体工具
- `agent-browser`: 浏览器自动化
- `web_search`: 网页搜索
- `debugging-wizard`: 调试工具

## 记忆 API

### 压缩记忆

```http
POST /memory/compress
```

**响应示例**:
```json
{
  "original_count": 100,
  "compressed_count": 75,
  "removed_count": 25,
  "compression_ratio": 0.75
}
```

**说明**:
- `original_count`: 原始观察数量
- `compressed_count`: 压缩后数量
- `removed_count`: 删除的重复项数量
- `compression_ratio`: 压缩率

### 获取聚类

```http
GET /memory/clusters
```

**响应示例**:
```json
[
  {
    "topic": "编程",
    "count": 25,
    "observations": [
      "用户喜欢使用 Rust",
      "讨论了 TypeScript 类型系统",
      "询问了 Python 异步编程"
    ]
  },
  {
    "topic": "工具",
    "count": 15,
    "observations": [
      "使用了 agent-browser",
      "配置了 web_search",
      "安装了新的技能"
    ]
  }
]
```

**主题类别**:
- 编程 (Tools)
- 错误 (Errors)
- 配置 (Config)
- 界面 (UI)
- 数据 (Data)

## 错误响应

### 404 Not Found

```json
{
  "error": "资源未找到"
}
```

### 500 Internal Server Error

```json
{
  "error": "内部服务器错误"
}
```

## 性能指标

- 平均响应时间: < 50ms
- 并发请求: > 100 req/s
- 内存占用: < 50MB

## 使用示例

### JavaScript/TypeScript

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 获取所有会话
const sessions = await api.get('/sessions');

// 搜索观察
const results = await api.post('/search', {
  query: 'Rust',
  threshold: 0.7
});
```

### Python

```python
import requests

BASE_URL = 'http://localhost:3000/api'

# 获取所有会话
response = requests.get(f'{BASE_URL}/sessions')
sessions = response.json()

# 搜索观察
response = requests.post(f'{BASE_URL}/search', json={
    'query': 'Rust',
    'threshold': 0.7
})
results = response.json()
```

### cURL

```bash
# 获取所有会话
curl http://localhost:3000/api/sessions

# 搜索观察
curl -X POST http://localhost:3000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Rust","threshold":0.7}'
```

## 相关文档

- [README](README_CN.md)
- [架构文档](ARCHITECTURE.md)
- [更新日志](CHANGELOG_CN.md)
