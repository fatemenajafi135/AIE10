from __future__ import annotations

import os

from langchain_openai import ChatOpenAI

DEFAULT_CHAT_MODEL = "gpt-5.4-mini"
DEFAULT_JUDGE_MODEL = "gpt-5.4-mini"

def _build_model(default: str, env_var: str, model_name: str | None, temperature: float) -> ChatOpenAI:
    name = model_name or os.environ.get(env_var, default)
    return ChatOpenAI(
        model=name, 
        temperature=temperature,
        openai_api_key=os.environ["OPENAI_API_KEY"],
    )

def get_chat_model(model_name: str | None = None, *, temperature: float = 0.5) -> ChatOpenAI:
    return _build_model(DEFAULT_CHAT_MODEL, "OPENAI_CHAT_MODEL", model_name, temperature)

def get_judge_model(model_name: str | None = None, *, temperature: float = 0) -> ChatOpenAI:
    return _build_model(DEFAULT_JUDGE_MODEL, "OPENAI_JUDGE_MODEL", model_name, temperature)