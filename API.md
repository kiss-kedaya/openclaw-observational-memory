# API Documentation

## Base URL

```
http://localhost:3000/api
```

## Endpoints

### Sessions

#### List Sessions

```http
GET /api/sessions
```

**Response:**
```json
[
  {
    "id": "session_123",
    "created_at": "2026-02-27T06:00:00Z",
    "updated_at": "2026-02-27T06:30:00Z",
    "message_count": 15,
    "token_count": 1234
  }
]
```

#### Get Session

```http
GET /api/sessions/:id
```

**Response:**
```json
{
  "id": "session_123",
  "created_at": "2026-02-27T06:00:00Z",
  "updated_at": "2026-02-27T06:30:00Z",
  "message_count": 15,
  "token_count": 1234
}
```

#### Create Session

```http
POST /api/sessions
```

**Request:**
```json
{
  "session_id": "session_123",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2026-02-27T06:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Hi there!",
      "timestamp": "2026-02-27T06:00:01Z"
    }
  ]
}
```

**Response:**
```json
{
  "session": {
    "id": "session_123",
    "created_at": "2026-02-27T06:00:00Z",
    "updated_at": "2026-02-27T06:00:00Z",
    "message_count": 2,
    "token_count": 10
  },
  "observations": [
    "User greeted",
    "Assistant responded"
  ]
}
```

### Observations

#### Get Observations

```http
GET /api/observations/:session_id
```

**Response:**
```json
[
  {
    "id": "obs_1",
    "session_id": "session_123",
    "content": "User greeted",
    "priority": "LOW",
    "created_at": "2026-02-27T06:00:00Z"
  }
]
```

### Search

#### Search Observations

```http
POST /api/search
```

**Request:**
```json
{
  "query": "greeting",
  "threshold": 0.3
}
```

**Response:**
```json
[
  {
    "id": "obs_1",
    "session_id": "session_123",
    "content": "User greeted",
    "priority": "LOW",
    "similarity": 0.85
  }
]
```

### Tool Suggestions

#### Get Tool Suggestions

```http
GET /api/tools/suggestions
```

**Response:**
```json
[
  {
    "tool": "agent-reach",
    "reason": "Detected pattern for agent-reach",
    "confidence": 0.8,
    "context": "Check this twitter.com link"
  }
]
```

### Memory Optimization

#### Compress Memory

```http
POST /api/memory/compress
```

**Response:**
```json
{
  "original_count": 100,
  "compressed_count": 85,
  "removed": 15,
  "ratio": 0.15
}
```

#### Get Clusters

```http
GET /api/memory/clusters
```

**Response:**
```json
[
  {
    "topic": "Tools",
    "count": 25,
    "observations": [
      "Installed agent-browser",
      "Configured web_search"
    ]
  }
]
```

## Error Responses

### 404 Not Found

```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

## Performance

- Average response time: < 50ms
- Concurrent requests: > 100 req/s
- Memory usage: < 50MB
