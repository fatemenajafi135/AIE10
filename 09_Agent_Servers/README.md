<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 9: Agent Servers</h1>

### [Quicklinks]()

| Session Sheet | Recording | Slides | Repo | Homework | Feedback |
|:--------------|:----------|:-------|:-----|:---------|:---------|
| [Session 9: Agent Servers & E2E Agents](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/09_Agent_servers_%26_E2E_Agents) |[Recording!](https://us02web.zoom.us/rec/share/ByhPGNz-CQ4C9k859VnRIoGPfkS4AdBzLPQiCIgEafYiDjYxtNXUjidTI1dM-79R.oCxzwNn0SyVAWj88) <br> passcode: `r14dvS$V`| [Session 9 Slides](https://canva.link/yqymnzjmzhpnyiy) | You are here! | [Session 9 Assignment](https://forms.gle/PMmqBBLZ8d8fGg1L8) | [Feedback 7/1](https://forms.gle/36tnHPpeS562DD3fA) |

## Useful Resources

**LangSmith Deployment & Studio**
- [LangSmith Deployment docs](https://docs.langchain.com/langsmith/deployments) — Deploy, manage, and monitor agent APIs
- [LangGraph Studio](https://docs.langchain.com/langgraph-platform/langgraph-studio) — Visualize, debug, and test agents locally and in production
- [Agent Server API](https://docs.langchain.com/langsmith/agent-server) — Threads, runs, assistants, and streaming
- [You don't know what your agent will do until it's in production](https://blog.langchain.com/you-dont-know-what-your-agent-will-do-until-its-in-production/)

**Frontend Integration**
- [`@langchain/react` — `useStream` hook](https://www.npmjs.com/package/@langchain/react) — Stream agent responses in React/Next.js
- [`langgraph-nextjs-api-passthrough`](https://www.npmjs.com/package/langgraph-nextjs-api-passthrough) — Secure Next.js API routes that proxy to your deployed agent without exposing keys in the browser
- [Next.js on Vercel](https://vercel.com/docs/frameworks/nextjs) — Deploy the frontend

## What You Are Building

In earlier sessions, you built LangGraph agents in notebooks. In this session, you take that agent to production in two parts:

1. **Deploy the agent** as an API backend on LangSmith (via LangGraph Studio and `langgraph deploy`)
2. **Build a website** that talks to that agent, then **deploy the site on Vercel**

```mermaid
flowchart LR
  User[User in browser] --> Vercel[Next.js frontend on Vercel]
  Vercel -->|"/api proxy route"| LangSmith[LangSmith Agent API]
  LangSmith --> Agent[Your LangGraph agent]
  Agent --> Tools[Tools + RAG + memory]
  LangSmith --> Traces[LangSmith tracing & evals]
```

> **Important:** LangSmith deploys your agent as an **API backend only**. It does not serve a frontend. Vercel hosts the UI; LangSmith hosts the agent.

## Main Assignment

You will package a LangGraph agent into a production-ready Python project, test it in **LangGraph Studio**, deploy it to **LangSmith**, then build a **Next.js chat UI** that streams responses from your deployed agent and ship that UI to **Vercel**.

Expected agent project layout:

```text
09_Agent_Servers/
├── langgraph.json          # Manifest — how LangGraph discovers your graphs
├── app/
│   ├── state.py            # Shared state schema
│   ├── models.py           # Model factory
│   ├── tools.py            # Tool belt
│   ├── rag.py              # Optional RAG pipeline
│   └── graphs/
│       └── simple_agent.py
├── data/
│   └── cat-health-guide.pdf
└── frontend/               # Next.js app (you create this)
    └── app/
        ├── page.tsx
        └── api/[...path]/route.ts
```

## Prerequisites

In addition to tools from earlier sessions, you will need:

1. A [LangSmith](https://smith.langchain.com/) account
2. **Docker** installed locally (needed for `langgraph up` and some deploy paths)
3. Your agent code pushed to a **GitHub** repository (needed for LangSmith cloud deploys)
4. A [Vercel](https://vercel.com/) account
5. *(Optional)* **LangSmith Plus** (~$40/month) for one-click cloud deploys via `langgraph deploy`

## Quick Command Reference

Two servers run **locally** (the agent API and the frontend), and two things deploy **online** (the agent to LangSmith, the frontend to Vercel). Run commands from `09_Agent_Servers/` unless noted. The detailed walkthrough for each step is in Parts 1–4 below.

### Run locally

**1. Agent server (LangGraph) — terminal 1**

```bash
uv sync                            # install Python deps (first time only)
cp .env.example .env               # then fill in OPENAI_API_KEY and TAVILY_API_KEY
uv run langgraph dev               # API at http://localhost:2024 + opens LangGraph Studio
```

**2. Frontend (Next.js) — terminal 2**

```bash
cd frontend
npm install                        # install JS deps (first time only)
cp .env.local.example .env.local   # defaults already point at http://localhost:2024
npm run dev                        # chat UI at http://localhost:3000
```

Open `http://localhost:3000` and chat. The browser hits the Next.js `/api` proxy, which forwards to your local agent server.

### Deploy online

**3. Agent → LangSmith** (push your repo to GitHub first; run from `09_Agent_Servers/`)

```bash
uv run langgraph deploy            # LangSmith cloud build + host (requires LangSmith Plus)
# or self-host in Docker on your own VPS instead:
uv run langgraph up
```

Then copy the **Deployment URL** and **LangSmith API key** from the LangSmith Deployments tab.

**4. Frontend → Vercel** (run from `frontend/`)

```bash
npm install -g vercel              # install the Vercel CLI (first time only)
cd frontend
vercel                             # first run links/creates the project (preview deploy)
vercel --prod                      # production deploy
```

Set these in the Vercel project (Settings → Environment Variables, or `vercel env add`), then run `vercel --prod` again:

```text
LANGGRAPH_API_URL=https://your-deployment.us.langgraph.app
LANGSMITH_API_KEY=lsv2_pt_...
NEXT_PUBLIC_API_URL=https://your-app.vercel.app/api
```

## Setup

From this folder, install the agent environment:

```bash
uv sync
```

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

Typical variables:

```text
OPENAI_API_KEY=
TAVILY_API_KEY=
LANGSMITH_API_KEY=
LANGSMITH_TRACING=true
```

## Part 1: Run Locally and Use LangGraph Studio

Package your agent so it can be served as an API — not as a notebook cell.

### 1. Define your graphs in `langgraph.json`

Register each compiled graph and the assistants you want to expose:

```json
{
  "dependencies": ["."],
  "env": ".env",
  "graphs": {
    "simple_agent": "app.graphs.simple_agent:graph"
  },
  "assistants": {
    "agent": {
      "graph_id": "simple_agent",
      "name": "Simple Agent",
      "description": "Agent with tools using conditional tool-calling."
    }
  }
}
```

Each graph file should export a compiled graph named `graph`.

### 2. Start the local agent server

```bash
uv run langgraph dev
```

This starts the agent API at `http://localhost:2024` and opens **LangGraph Studio** in your browser (Chromium-based browsers work best).

### 3. Explore and debug in Studio

Use Studio to:

- Visualize graph topology — nodes, edges, and conditional branches
- Step through execution and inspect tool calls and results
- Fork conversations to test alternate paths
- Switch between assistants defined in `langgraph.json`

Studio and the SDK stream the same events. Studio is for debugging; the SDK (and your frontend) is for production integration.

### 4. Smoke-test with the SDK

```python
from langgraph_sdk import get_client

client = get_client(url="http://localhost:2024")

for chunk in client.runs.stream(
    None,
    "agent",
    input={"messages": [{"role": "human", "content": "How often should I deworm my cat?"}]},
    stream_mode="updates",
):
    print(chunk)
```

If this works locally, you are ready to deploy.

## Part 2: Deploy the Agent on LangSmith

Push your agent repo to GitHub, then deploy.

### Option A: LangSmith cloud deploy (recommended for this session)

```bash
uv run langgraph deploy
```

Requires LangSmith Plus. LangSmith builds and hosts the agent API for you. After deploy, copy your **Deployment URL** and **LangSmith API key** from the LangSmith Deployments tab — you will need both for the frontend.

Enable **auto-update on push** so every commit to your main branch triggers a redeploy.

### Option B: Self-hosted with Docker

```bash
uv run langgraph up
```

Runs a production-ready container you can host on any VPS. You manage scaling, uptime, and auth yourself.

### What you get

A hosted API endpoint with standard routes for threads, runs, and assistants. Your agent runs behind that API; LangSmith traces and monitors execution.

## Part 3: Build a Website That Uses Your Agent

Create a Next.js frontend that streams chat responses from your deployed agent.

### Recommended architecture

Never put `LANGSMITH_API_KEY` in client-side code. Use a **Next.js API route** as a secure proxy:

```text
Browser  →  /api/* on Vercel  →  LangSmith Deployment URL
              (injects API key server-side)
```

### 1. Scaffold the frontend

From this folder:

```bash
npx create-next-app@latest frontend
cd frontend
npm install @langchain/react langgraph-nextjs-api-passthrough
```

### 2. Add the API passthrough route

Create `frontend/app/api/[...path]/route.ts`:

```typescript
import { initApiPassthrough } from "langgraph-nextjs-api-passthrough";

export const { GET, POST, PUT, PATCH, DELETE, OPTIONS, runtime } =
  initApiPassthrough({
    apiUrl: process.env.LANGGRAPH_API_URL,
    apiKey: process.env.LANGSMITH_API_KEY,
    runtime: "edge",
  });
```

### 3. Build the chat UI with `useStream`

In a client component (e.g. `frontend/app/page.tsx`), connect to your local proxy or deployed passthrough:

```typescript
"use client";

import { useStream } from "@langchain/react";

export default function ChatPage() {
  const { messages, submit, isLoading } = useStream({
    apiUrl: process.env.NEXT_PUBLIC_API_URL ?? "/api",
    assistantId: "agent",
  });

  // Render messages and a form that calls submit({ messages: [...] })
}
```

Use the `assistantId` that matches your `langgraph.json` assistants block.

### 4. Test locally

In `frontend/.env.local`:

```text
# Point at your local agent server (uv run langgraph dev):
LANGGRAPH_API_URL=http://localhost:2024
LANGSMITH_API_KEY=

# ...or point at your deployed LangSmith agent instead:
# LANGGRAPH_API_URL=https://your-deployment.us.langgraph.app
# LANGSMITH_API_KEY=lsv2_pt_...

NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

Install deps (first time) and run the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`, send a message, and confirm you see streamed responses from your LangSmith deployment.

## Part 4: Deploy the Frontend on Vercel

### 1. Push the frontend to GitHub

Commit the `frontend/` directory (either in the same repo as your agent or a separate repo).

### 2. Import the project in Vercel

1. Go to [vercel.com/new](https://vercel.com/new) and import your repository
2. Set the **Root Directory** to `frontend` if the Next.js app is not at the repo root
3. Add environment variables in the Vercel project settings:

```text
LANGGRAPH_API_URL=https://your-deployment.us.langgraph.app
LANGSMITH_API_KEY=lsv2_pt_...
NEXT_PUBLIC_API_URL=https://your-app.vercel.app/api
```

4. Deploy

### 3. Verify end-to-end

Visit your Vercel URL, send a chat message, and confirm:

- The UI streams agent responses
- Tool calls work against your deployed agent
- Traces appear in LangSmith for each run

## Outline

### Breakout Room #1: Agent Packaging & LangGraph Studio

- Restructure a notebook agent into a Python package (`app/`, `langgraph.json`)
- Run `langgraph dev` and explore the agent in LangGraph Studio
- Test with the LangGraph SDK locally

### Breakout Room #2: Deploy Agent + Build & Ship Frontend

- Deploy the agent to LangSmith with `langgraph deploy`
- Scaffold a Next.js chat UI with `useStream`
- Add a secure API passthrough route
- Deploy the frontend to Vercel and connect it to your LangSmith deployment

## Ship

A deployed agent on LangSmith **and** a live website on Vercel that uses it.

### Deliverables

- A short Loom of either:
  - LangGraph Studio debugging your agent, then your Vercel site chatting with the deployed agent; or
  - your Advanced Activity below

## Share

Make a social media post about shipping your first production agent + frontend!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I just deployed a LangGraph agent to LangSmith and built a website on Vercel that streams responses from it! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in agent engineering. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#LangGraph #LangSmith #NextJS #Vercel #AgentEngineering #Innovation #AI

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

## Submitting Your Homework

Follow these steps to prepare and submit your homework assignment:

1. Package your agent with `langgraph.json` and run it locally with `langgraph dev`
2. Debug and demo the agent in LangGraph Studio
3. Deploy the agent to LangSmith and note your deployment URL
4. Build a Next.js frontend that streams from the deployed agent via a secure API route
5. Deploy the frontend to Vercel
6. Record a Loom video reviewing what you learned from this session

## Questions

### Question #1

Why does LangSmith deploy your agent as an API backend only, and why do you still need a separate frontend deployment like Vercel?

#### Answer

_LangSmith deploys only the agent as an API because the agent and the frontend have different jobs and different infrastructure needs. The API needs a Python runtime, Postgres for state, and Redis for streaming, heavy, stateful backend work. The frontend just needs to render a chat UI, which is lightweight and works best on an edge platform like Vercel. Keeping them separate also means the API isn't locked to one UI, the same backend could serve a web app, a Slack bot, or any other client. And it lets each side deploy and iterate independently, I redeployed my frontend several times without touching the Railway agent at all._

### Question #2

Why should the LangSmith API key live in a Next.js API route (server-side) instead of in the browser?

#### Answer

_The API key has to stay server-side because anything sent to the browser is visible to anyone who opens dev tools. The `route.ts` file runs on Vercel's server, not in the browser, it receives the request from the client, attaches the real `LANGSMITH_API_KEY` itself, then forwards it to the Railway agent. The browser only ever talks to my own `/api` route, never to LangSmith directly, so the key is never exposed. This matches Next.js's own convention: only variables prefixed `NEXT_PUBLIC_` get bundled into client-side code, everything else, like this key, stays server-only by default._

## Activity 1: Build a Helpfulness Loop in Production

Build an `agent_with_helpfulness` graph that adds a post-response helpfulness check: after the agent answers, a judge model decides whether the response is helpful, and if not, the graph loops back for another attempt (with a safe loop limit). Register it in `langgraph.json`, deploy it, then compare LangSmith traces for queries that pass vs. fail the helpfulness check. Does the retry loop behave differently in Studio vs. production?

### 📝 Activity Notes

*Graph:* `agent_with_helpfulness`, wraps `simple_agent` as a subgraph node with a judge node and conditional loop-back, registered in `langgraph.json`.

**Turn 1 > "What are signs of feline dehydration?"**

Agent answers directly using the retrieval tool. Judge passes it on the first attempt.

- `retry_count`: 1, `is_helpful`: true
- Judge reason: *"The answer is relevant, accurate, and complete for the question. It lists common signs of feline dehydration, adds useful caveats and when to seek veterinary care, and stays within cat health."*

**Turn 2 > "tell me more"**

Vague follow-up, no clear topic. The agent's first two attempts get rejected internally (shown on the frontend as "Attempt 1 was not helpful" / "Attempt 2 was not helpful"), before it lands on asking "Could you tell me what you want more information about?" on the third and final allowed attempt.

- `retry_count`: 3 (the retry ceiling), `is_helpful`: true, but only on that last attempt
- Judge reason: *"The reply appropriately asks for clarification because the topic was not established. It stays within cat-health context and does not assume an unsupported condition."*
- Notable: this hit the max retry limit exactly on the attempt that passed. One more failed attempt and it would have hit the `UNHELPFUL_NOTE` fallback instead of a real answer.

**Turn 3 > "tell me about each in detail:"**

Still ambiguous ("each" has no clear referent). One retry before the agent recognizes this and asks for clarification instead of guessing.

- `retry_count`: 2, `is_helpful`: true
- Judge reason: *"The response correctly identifies the ambiguity, offers the intended cat-health topic (feline dehydration signs) to explain in detail, and invites the user to clarify if they meant something else. It is relevant, safe, and appropriately redirects."*

**Turn 4 > "go with Poor appetite"**

User picks a concrete topic from the earlier list. Agent answers directly with a grounded, detailed response. Passes immediately.

- `retry_count`: 1, `is_helpful`: true
- Judge reason: *"The response is relevant to 'poor appetite,' explains that it can be a sign of dehydration, gives common causes, warning signs, and when to call a vet, and offers follow-up options. It is complete and appropriately cat-health focused."*

**Comparing pass vs. fail traces**

Passing traces (turns 1 and 4) show a single agent → judge cycle: one call to `simple_agent`, one call to `judge_node`, then straight to `END`. Nothing loops back.

Retry traces (turns 2 and 3) show the graph actually cycling: `agent → judge → agent → judge`, repeated once (turn 3) or twice (turn 2), with each rejected answer swapped in as an internal message rather than shown to the user, and a feedback message injected before the next `agent` call. The trace depth and node-call count is what separates a pass from a retry, not just the final `is_helpful` value.

**Trace vs. UI (Studio/LangSmith vs. production)**

The LangSmith trace captures every step of the flow: each `agent` call, each `judge_node` call, the retry count at each cycle, and every message in state, including ones tagged `internal`. That's where the loop's real mechanics are visible.

The chat UI, standing in for production, doesn't show all of that. The rejected answer and the synthetic retry-feedback message are both tagged `internal`, so the frontend filters them out of the rendered conversation. The user only sees a placeholder like "Attempt 1 was not helpful," not the rejected answer itself or the feedback the agent received before retrying. The UI shows *that* a retry happened; the trace shows *why*, the judge's reasoning, the exact retry prompt, and the full unfiltered message history.

## Advanced Activity: Auth and Custom Routes

Research [LangSmith Deployments custom routes](https://github.com/langchain-samples/lsd-custom-route-react-ui) and describe how you could add authentication so each user only sees their own threads. Optionally implement a simple auth gate on your Vercel frontend.

Include your findings and a demo in your Loom video.
