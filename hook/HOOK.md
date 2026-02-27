---
name: observational-memory
description: "Auto record all conversations to Observational Memory"
homepage: https://github.com/kiss-kedaya/openclaw-observational-memory
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "events": ["message", "session:end"],
        "install": [{ "id": "local", "kind": "local", "label": "Local Development" }],
      },
  }
---

# Observational Memory Hook

Auto record all conversations to Observational Memory system.

## Features

- Auto record all conversations
- Track message count and token count
- Extract observations from messages
- Support for all message roles (user, assistant, system)

## Requirements

- Observational Memory service running on http://localhost:3000

## Events

- `message`: Triggered on every message
- `session:end`: Triggered when session ends
