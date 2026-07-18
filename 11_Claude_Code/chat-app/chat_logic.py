"""Chat reply generation - the seam where the real agent is wired in.

This module knows nothing about HTTP or FastAPI. generate_reply_stream()
is the core async generator; generate_reply() is a non-streaming wrapper
over it. main.py and the frontend consume these; the seam kept them small.

Task 6: replaced the echo stub with a Claude Agent SDK query() call,
configured as a read-only codebase concierge.
Task 7: added session resumption so each browser conversation_id maps to
its own SDK session_id, giving the agent memory across messages.
Task 8: added a custom in-process tool, count_lines, alongside the
built-in Read/Glob/Grep tools.
Activity #1: added a second custom tool, git_log, for browsing recent
commit history in the target repo, and live progress streaming - the
agent's tool calls are streamed to the browser via Server-Sent Events.
"""

import os
import logging
import subprocess

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Task 6:
TARGET_REPO = os.environ.get("TARGET_REPO_PATH", os.getcwd())

SYSTEM_PROMPT = (
    f"You are Concierge, an assistant that answers questions about the "
    f"codebase at {TARGET_REPO}. Answer concisely and always cite the "
    f"specific file paths you looked at. If you're not sure, say so instead "
    f"of guessing."
)


# Task 8: 
@tool("count_lines", "Count the lines of code in a given file", {"file_path": str})
async def count_lines(args: dict) -> dict:
    file_path = args["file_path"]
    # Resolve relative to the target repo, not wherever this process happens
    # to be running from. Previously this silently counted lines in the
    # wrong file whenever TARGET_REPO_PATH pointed somewhere else.
    resolved_path = (
        file_path if os.path.isabs(file_path) else os.path.join(TARGET_REPO, file_path)
    )
    try:
        with open(resolved_path, encoding="utf-8") as f:
            n = sum(1 for _ in f)
        return {"content": [{"type": "text", "text": f"{file_path}: {n} lines"}]}
    except OSError as exc:
        return {
            "content": [{"type": "text", "text": f"Could not read {file_path}: {exc}"}]
        }


# Activity #1, option 3
@tool("git_log", "Show the N most recent git commits in the target repo", {"n": int})
async def git_log(args: dict) -> dict:
    n = args.get("n", 10)
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--oneline"],
            cwd=TARGET_REPO,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            text = f"git log failed: {result.stderr.strip()}"
        else:
            text = result.stdout.strip() or "No commits found."
        return {"content": [{"type": "text", "text": text}]}
    except Exception as exc:
        return {"content": [{"type": "text", "text": f"Could not run git log: {exc}"}]}


_concierge_server = create_sdk_mcp_server(
    name="concierge", version="1.0.0", tools=[count_lines, git_log]
)

# Task 7:
_sessions: dict[str, str] = {}


def _build_options(resume: str | None) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        cwd=TARGET_REPO,
        # Read-only allowlist: this agent runs headless on a server with no
        # human in the loop to approve tool calls.
        allowed_tools=[
            "Read",
            "Glob",
            "Grep",
            "mcp__concierge__count_lines",
            "mcp__concierge__git_log",
        ],
        permission_mode="dontAsk",
        disallowed_tools=["Bash", "Write", "Edit", "NotebookEdit", "WebFetch", "WebSearch"],
        mcp_servers={"concierge": _concierge_server},
        max_turns=25,
        resume=resume,
    )


def _tool_label(name: str, tool_input: dict) -> str:
    """Human-friendly progress label for a tool call, shown live in the UI."""
    short = name.split("__")[-1]  # strip the mcp__concierge__ prefix
    if short == "Read":
        return f"Reading {os.path.basename(tool_input.get('file_path', ''))}…"
    if short == "Glob":
        return f"Searching files ({tool_input.get('pattern', '')})…"
    if short == "Grep":
        return f"Searching for \"{tool_input.get('pattern', '')}\"…"
    if short == "count_lines":
        return f"Counting lines in {os.path.basename(tool_input.get('file_path', ''))}…"
    if short == "git_log":
        return "Reading recent commits…"
    return f"Using {short}…"


# Activity #1, option 1
async def generate_reply_stream(message: str, conversation_id: str):
    """Core agent loop, exposed as an async generator of progress events.

    Yields dicts:
      {"type": "tool",   "name": ..., "label": ...}  - a tool call started
      {"type": "result", "reply": ...}               - the final answer
      {"type": "error",  "reply": ...}               - something went wrong

    Both the streaming SSE endpoint and the plain /api/chat endpoint run
    through this one path, so there's no duplicated query() loop.
    """
    resume = _sessions.get(conversation_id)
    options = _build_options(resume)

    reply = "Sorry, I didn't get a clear answer that time. Please try again."
    try:
        async for msg in query(prompt=message, options=options):
            if isinstance(msg, SystemMessage) and msg.subtype == "init":
                _sessions[conversation_id] = msg.data["session_id"]
            elif isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        logger.info("tool call: %s args=%s", block.name, block.input)
                        yield {
                            "type": "tool",
                            "name": block.name,
                            "label": _tool_label(block.name, block.input),
                        }
            elif isinstance(msg, ResultMessage):
                reply = msg.result
            logger.debug(type(msg).__name__)
        yield {"type": "result", "reply": reply}
    except Exception:
        # Task 6 requirement: 
        logger.exception("agent run failed for conversation_id=%s", conversation_id)
        yield {
            "type": "error",
            "reply": "Sorry, something went wrong on my end. Please try again in a moment.",
        }


async def generate_reply(message: str, conversation_id: str) -> str:
    """Non-streaming reply: drain the event stream, return the final text.

    Kept so POST /api/chat (used by curl and the CLAUDE.md docs) still works
    unchanged.
    """
    reply = "Sorry, I didn't get a clear answer that time. Please try again."
    async for event in generate_reply_stream(message, conversation_id):
        if event["type"] in ("result", "error"):
            reply = event["reply"]
    return reply
