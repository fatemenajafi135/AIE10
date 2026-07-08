"""Retrieval-Augmented Generation (RAG) utilities and tool.

This module builds an in-memory RAG pipeline that:
- Loads PDF documents from `RAG_DATA_DIR` (default: "data").
- Splits documents into chunks using a token-aware splitter.
- Embeds chunks (Fireworks-hosted embeddings, or OpenAI for the other providers)
  and stores vectors in an in-memory Qdrant store.
- Generates with Fireworks-hosted `gpt-oss-20b`, Groq-hosted `gpt-oss-20b`, or
  OpenAI `gpt-4.1-mini`.
- Exposes a LangChain Tool `retrieve_information` that retrieves relevant
  context and generates a response constrained to that context.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated, TypedDict

import tiktoken
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langgraph.graph import START, StateGraph


def _tiktoken_len(text: str) -> int:
    """Return token length using tiktoken; used for chunk length measurement."""
    tokens = tiktoken.encoding_for_model("gpt-4o").encode(text)
    return len(tokens)


class _RAGState(TypedDict):
    """State schema for the simple two-step RAG graph: retrieve then generate."""

    question: str
    context: list[Document]
    response: str


def _build_rag_graph(data_dir: str, provider: str = "fireworks"):
    """Construct and compile a minimal RAG graph.

    Steps:
    1) Load PDFs from `data_dir` recursively (best-effort).
    2) Split documents into token-aware chunks.
    3) Create embeddings and an in-memory Qdrant vector store retriever.
    4) Define a chat prompt and generation model.
    5) Wire a two-node graph: retrieve -> generate.

    `provider` selects which models back the graph: "fireworks" (default) uses
    Fireworks-hosted embeddings + `gpt-oss-20b`; "groq" uses Groq-hosted
    `gpt-oss-20b` for generation; "openai" uses `gpt-4.1-mini`. Groq has no
    embeddings API, so the groq and openai providers both use OpenAI
    embeddings.
    """
    # Load PDFs from data directory (recursive)
    try:
        directory_loader = DirectoryLoader(
            data_dir, glob="**/*.pdf", loader_cls=PyMuPDFLoader
        )
        documents = directory_loader.load()
    except Exception:
        documents = []

    # Split documents
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=750, chunk_overlap=0, length_function=_tiktoken_len
    )
    chunks = text_splitter.split_documents(documents) if documents else []

    # Embeddings and vector store (in-memory Qdrant). Groq has no embeddings API,
    # so it shares OpenAI embeddings with the openai provider.
    if provider == "fireworks":
        embedding_model = OpenAIEmbeddings(
            model=os.environ.get("FIREWORKS_EMBEDDING_MODEL", "accounts/fireworks/models/qwen3-embedding-8b"),
            openai_api_key=os.environ["FIREWORKS_API_KEY"],
            openai_api_base="https://api.fireworks.ai/inference/v1",
            check_embedding_ctx_length=False,
            dimensions=4096,
            timeout=60,
            max_retries=2,
        )
    elif provider in ("groq", "openai"):
        embedding_model = OpenAIEmbeddings()
    else:
        raise ValueError(f"Unknown provider: {provider!r}")
    qdrant_vectorstore = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        location=":memory:",
        collection_name="rag_collection",
    )
    retriever = qdrant_vectorstore.as_retriever()

    # Prompt and model
    human_template = (
        "\n#CONTEXT:\n{context}\n\nQUERY:\n{query}\n\n"
        "Use the provide context to answer the provided user query. "
        "Only use the provided context to answer the query. If you do not know the answer, or it's not contained in the provided context respond with \"I don't know\""
    )
    chat_prompt = ChatPromptTemplate.from_messages([("human", human_template)])
    if provider == "fireworks":
        generator_llm = ChatOpenAI(
            model=os.environ.get("FIREWORKS_CHAT_MODEL", "accounts/fireworks/models/gpt-oss-20b"),
            openai_api_key=os.environ["FIREWORKS_API_KEY"],
            openai_api_base="https://api.fireworks.ai/inference/v1",
            timeout=60,
            max_retries=2,
        )
    elif provider == "groq":
        generator_llm = ChatOpenAI(
            model=os.environ.get("GROQ_CHAT_MODEL", "openai/gpt-oss-20b"),
            openai_api_key=os.environ["GROQ_API_KEY"],
            openai_api_base="https://api.groq.com/openai/v1",
            timeout=60,
            max_retries=2,
        )
    else:
        generator_llm = ChatOpenAI(model="gpt-4.1-mini")

    def retrieve(state: _RAGState) -> _RAGState:
        retrieved_docs = retriever.invoke(state["question"]) if retriever else []
        return {"context": retrieved_docs}  # type: ignore

    def generate(state: _RAGState) -> _RAGState:
        generator_chain = chat_prompt | generator_llm | StrOutputParser()
        response_text = generator_chain.invoke(
            {"query": state["question"], "context": state.get("context", [])}
        )
        return {"response": response_text}  # type: ignore

    graph_builder = StateGraph(_RAGState)
    graph_builder = graph_builder.add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    return graph_builder.compile()


@lru_cache(maxsize=3)
def _get_rag_graph(provider: str = "fireworks"):
    """Return a cached compiled RAG graph built from RAG_DATA_DIR."""
    data_dir = os.environ.get("RAG_DATA_DIR", "data")
    return _build_rag_graph(data_dir, provider=provider)


def get_fireworks_rag_graph():
    """Return the Fireworks-backed RAG graph (Fireworks embeddings + gpt-oss-20b)."""
    return _get_rag_graph("fireworks")


def get_groq_rag_graph():
    """Return the Groq-backed RAG graph (OpenAI embeddings + Groq-hosted gpt-oss-20b)."""
    return _get_rag_graph("groq")


def get_openai_rag_graph():
    """Return the OpenAI-backed RAG graph (OpenAI embeddings + gpt-4.1-mini).

    Built with the same `data_dir`/chunking as the other providers so all
    three can be invoked side by side with identical questions for comparison.
    """
    return _get_rag_graph("openai")


@tool
def retrieve_information(
    query: Annotated[str, "query to ask the retrieve information tool"],
):
    """Use Retrieval Augmented Generation to retrieve information about feline health, including life stage care, nutrition, vaccinations, parasite control, behavior, diagnostics, and veterinary guidelines for cats."""
    graph = _get_rag_graph()
    result = graph.invoke({"question": query})
    # Prefer returning the response string if available
    if isinstance(result, dict) and "response" in result:
        return result["response"]
    return result
