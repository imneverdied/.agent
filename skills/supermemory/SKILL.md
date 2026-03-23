---
name: supermemory
description: Store and retrieve memories using the SuperMemory API. Add content, search memories, and chat with your knowledge base.
metadata: {"moltbot":{"emoji":"memory","requires":{"env":["SUPERMEMORY_API_KEY"]},"primaryEnv":"SUPERMEMORY_API_KEY"},"user-invocable":true}
---

# SuperMemory

Store, search, and chat with your personal knowledge base using SuperMemory API.

## Setup

Set your API key before use:

```bash
# Linux / macOS
export SUPERMEMORY_API_KEY="YOUR_SUPERMEMORY_API_KEY"

# Windows PowerShell
$env:SUPERMEMORY_API_KEY = "YOUR_SUPERMEMORY_API_KEY"
```

## Usage

### Add a Memory

```bash
supermemory add "Your memory content here"
supermemory add "Important project details" --description "Project requirements"
```

### Search Memories

```bash
supermemory search "search query"
```

### Chat with Memories

```bash
supermemory chat "What do you know about my projects?"
```

## Implementation

Run scripts from this workspace:

```bash
bash .agent/skills/supermemory/scripts/add-memory.sh "content" "description (optional)"
bash .agent/skills/supermemory/scripts/search.sh "query"
bash .agent/skills/supermemory/scripts/chat.sh "question"
```

## Notes

- Never hardcode API keys in SKILL files or scripts.
- On Windows, run these shell scripts via Git Bash or WSL.
