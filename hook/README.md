# OpenClaw Hook: Observational Memory

Auto record all conversations to Observational Memory system.

## Installation

```bash
openclaw hooks install F:/GO/openclaw-observational-memory/hook
```

## Usage

The hook will automatically record all messages to Observational Memory.

## Requirements

- Observational Memory service running on http://localhost:3000

## Features

- Auto record all conversations
- Track message count and token count
- Extract observations from messages
- Support for all message roles (user, assistant, system)

## Events

- `message`: Triggered on every message
- `session:end`: Triggered when session ends

## Configuration

No configuration needed. The hook will automatically connect to Observational Memory service on http://localhost:3000.

## Troubleshooting

If messages are not being recorded:

1. Check if Observational Memory service is running:
   ```bash
   curl http://localhost:3000
   ```

2. Check hook status:
   ```bash
   openclaw hooks list
   ```

3. Check Gateway logs for errors

## Development

```bash
# Install dependencies
npm install

# Test locally
node index.js
```
