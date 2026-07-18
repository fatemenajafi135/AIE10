# chat-app

A minimal chat web app: FastAPI backend, plain HTML/CSS/JS frontend, no
framework. `POST /api/chat` currently echoes the message back — the reply
logic lives entirely in `chat_logic.py`, ready to be swapped for a real
agent later.

## Run

```bash
uv sync
uv run uvicorn main:app --reload
```

Open http://localhost:8000 in a browser.

## Test the API directly

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "conversation_id": "1"}'
```
