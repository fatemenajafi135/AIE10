import json

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chat_logic import generate_reply, generate_reply_stream

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str
    conversation_id: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse("static/index.html")


@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Non-streaming endpoint. Kept for curl testing and simple clients."""
    reply = await generate_reply(request.message, request.conversation_id)
    return ChatResponse(reply=reply)


@app.get("/api/chat/stream")
async def chat_stream(message: str, conversation_id: str) -> StreamingResponse:
    """Server-Sent Events endpoint (Activity #1).

    Streams the agent's progress - each tool call as it happens, then the
    final reply - so the browser can show live activity instead of a spinner.
    EventSource in the browser only issues GET requests, so the message and
    conversation_id come in as query params.
    """

    async def event_source():
        async for event in generate_reply_stream(message, conversation_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
