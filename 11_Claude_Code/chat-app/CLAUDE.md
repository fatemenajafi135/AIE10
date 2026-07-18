# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Commands

```bash
uv sync                                # install dependencies
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
- `POST /api/chat` accepts `{message, conversation_id}` and returns `{reply}`.

Reply logic lives in `chat_logic.py`'s `generate_reply(message, conversation_id)`. It currently echoes the input. This is the seam: `chat_logic.py` has no FastAPI or HTTP knowledge, so wiring in the real Claude Agent SDK `query()` call later means editing only this one file. `main.py` and the frontend stay untouched.