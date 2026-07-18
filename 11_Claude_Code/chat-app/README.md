# chat-app

A chat web app: FastAPI backend, plain HTML/CSS/JS frontend, no framework.
The chat is powered by the Claude Agent SDK, configured as a read-only
codebase concierge that answers questions about the repo at
`TARGET_REPO_PATH`. It remembers each conversation (session resumption keyed
by `conversation_id`), has two custom tools (`count_lines`, `git_log`), and
streams its progress (each tool call) live to the browser via Server-Sent
Events. Reply logic lives entirely in `chat_logic.py`.

The agent is provably read-only: `permission_mode="dontAsk"` makes the tool
allowlist an exclusive gate, backed by an explicit blocklist of write/exec
tools, so it cannot run shell commands or edit files regardless of the prompt.

## Endpoints

- `GET /api/chat/stream?message=&conversation_id=` — SSE stream (used by the UI)
- `POST /api/chat` — non-streaming `{message, conversation_id}` -> `{reply}`

## Run

```bash
uv sync
export ANTHROPIC_API_KEY="sk-ant-..."
export TARGET_REPO_PATH="/path/to/repo"  # optional, defaults to cwd
uv run uvicorn main:app --reload
```

Open http://localhost:8000 in a browser.

## Test the API directly

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "what does this repo do?", "conversation_id": "1"}'
```
