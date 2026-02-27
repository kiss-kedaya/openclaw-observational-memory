---
name: observational-memory
description: "Auto record all conversations to Observational Memory"
homepage: https://github.com/kiss-kedaya/openclaw-observational-memory
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "events": ["message:received", "message:sent"],
        "requires": {},
        "install": [{ "id": "managed", "kind": "managed", "label": "Managed Installation" }],
      },
  }
---

# Observational Memory Hook

Automatically records all conversations to the Observational Memory system.

## Features

- Auto record every message (received and sent)
- Extract observations from messages
- Support for all message roles (user, assistant, system)
- Real-time conversation tracking

## Requirements

- Observational Memory service running on http://localhost:3000

## Events

- `message:received`: Triggered when a message is received
- `message:sent`: Triggered when a message is sent

## Installation

```bash
openclaw hooks install F:/GO/openclaw-observational-memory/hook
```

## Usage

The hook will automatically record all messages to Observational Memory once installed and enabled.
