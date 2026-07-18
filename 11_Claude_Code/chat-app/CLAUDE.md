# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Commands

```bash
uv sync                                # install dependencies
export ANTHROPIC_API_KEY="sk-ant-..."  # required, the agent calls the Claude API
export TARGET_REPO_PATH="/path/to/repo"  # optional, defaults to cwd; the repo the concierge answers about
uv run uvicorn main:app --reload       # run the dev server on http://localhost:8000
```

Test the API directly:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "conversation_id": "1"}'
```

No test suite, linter, or build step exists yet.

## Architecture

FastAPI backend (`main.py`) + static HTML/CSS/JS frontend (`static/`), no
frontend framework.

- `GET /` serves `static/index.html`; `/static/*` is mounted for CSS/JS.
- `POST /api/chat` accepts `{message, conversation_id}` and returns `{reply}` (non-streaming).
- `GET /api/chat/stream?message=&conversation_id=` streams the agent's tool calls then the final reply as Server-Sent Events; the browser UI uses this one.

Reply logic lives in `chat_logic.py`'s `generate_reply_stream(message, conversation_id)` async generator (with `generate_reply()` as a non-streaming wrapper over it). It calls the Claude Agent SDK's `query()`, configured as a read-only codebase concierge (`allowed_tools=["Read", "Glob", "Grep", "mcp__concierge__count_lines", "mcp__concierge__git_log"]`, `max_turns=25`, `cwd=TARGET_REPO_PATH`). `chat_logic.py` has no FastAPI or HTTP knowledge.

Safety enforcement: `allowed_tools` alone is only a pre-approval list, not an exclusive gate, so `permission_mode="dontAsk"` is set to deny any tool not on the allowlist, backed by an explicit `disallowed_tools` blocklist (`Bash`, `Write`, `Edit`, etc.). This is what actually stops the headless agent from running shell commands.

`conversation_id` (from the browser) is mapped to the SDK's `session_id` in an in-memory dict, so follow-up messages in the same conversation resume the same agent session.