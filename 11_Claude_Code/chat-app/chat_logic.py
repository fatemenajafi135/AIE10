"""Chat reply generation — the seam where a real agent gets wired in later.

generate_reply() is the only function this module exposes. It knows nothing
about HTTP or FastAPI, so swapping the echo stub for a Claude Agent SDK
query() call later means editing only this file.
"""


def generate_reply(message: str, conversation_id: str) -> str:
    return f"You said: {message}"
