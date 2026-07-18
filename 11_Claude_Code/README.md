<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 11: Claude Code & the Claude Agent SDK</h1>

| 📰 Session Sheet | ⏺️ Recording | 🖼️ Slides | 👨‍💻 Repo | 📝 Homework | 📁 Feedback |
|:-----------------|:-------------|:----------|:----------|:------------|:------------|
| [Session 11: Claude Code & Claude Agent SDK ](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/11_Claude_Code) |[Recording!](https://us02web.zoom.us/rec/share/2I5HA6DwVFgmtyjPaq1SJDgkaVEuYZoWYyMCK8DOAZ99Zm6f7dTi0IGONXj6mRel.YHFzKF03mI5v6JAM) <br> passcode: `&Qhi!cf0`| [Session 11 Slides](https://canva.link/uw1cl42x84tm6zh) |You are here! <br><br> [Certification Challenge](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Certification%20Challenge) | [Optional Session 11 Assignment](https://forms.gle/sAyr5BgBLTfgJV8EA) <br><br>  [Cert Challenge Submission Form](https://forms.gle/xtM9F38nfRKcdjH97)| [Feedback 7/7](https://forms.gle/oDrguLDNvva65mtM8) |

## Useful Resources

**Claude Code**
- [Claude Code Documentation](https://code.claude.com/docs) — official docs: setup, workflows, settings
- [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) — from install to first session
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) — Anthropic engineering guide

**Claude Agent SDK**
- [Agent SDK Overview](https://docs.anthropic.com/en/api/agent-sdk/overview) — what the SDK is and when to use it
- [Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — Anthropic engineering deep dive

## Main Assignment

**Build a chat web app powered by the Claude Agent SDK** — and build it *with* Claude Code.

This session is markdown-only on purpose. There is no starter code and no notebook: every line of code in your final app will be written in collaboration with Claude Code. The session has one build arc across a single breakout room:

```text
you → Claude Code → chat app skeleton → wire in Agent SDK query()
      (FastAPI + chat UI, echo stub)      ├─ tools: Read / Glob / Grep
                                           └─ your custom tool
```

The finished product: a **codebase concierge** — a chat interface in the browser where an agent (with real tools) answers questions about any repository you point it at. In Session 10 you served models behind endpoints; today you serve an *agent* behind one.

Work through the three guides in order:

```text
01_Installing_Claude_Code.md   # install, authenticate, verify
02_Using_Claude_Code.md        # drive Claude Code; scaffold the chat app skeleton
03_Claude_Agent_SDK.md         # add the agent and connect it to your website
```

## Outline

### Breakout Room #1: Claude Code, the Agent SDK, and the Connection

- Task 1: Install Claude Code and authenticate ([guide](./01_Installing_Claude_Code.md))
- Task 2: Learn the loop — explore a repo you didn't write ([guide](./02_Using_Claude_Code.md))
- Task 3: Scaffold the chat app skeleton with Claude Code (plan → implement → verify)
- Task 4: Write the project's `CLAUDE.md`
- Question #1 and Question #2
- Task 5: Install the Agent SDK and run your first `query()` ([guide](./03_Claude_Agent_SDK.md))
- Task 6: Wire the agent into `/api/chat` — replace the echo stub
- Task 7: Conversation memory — resume sessions across messages
- Task 8: Give the agent a custom tool
- Question #3 and Question #4
- Activity #1: Level Up the Chat App

## Questions

### ❓ Question #1

While scaffolding in Task 3 you used **plan mode** before letting Claude Code write anything. Why does an agent that can execute shell commands need a permission system at all, and why is plan mode particularly valuable when starting a project from an empty directory?

#### ✅ Answer


_An agent that can run shell commands and edit files can also break things, irreversibly and fast, with no human reviewing each step. The permission system keeps a human in the loop: it turns “the agent decided to do X” into “the agent proposed X, I approved it.” Starting from an empty directory is the highest-risk moment. There is no existing structure or test suite to catch a bad decision, and a wrong assumption made early (wrong framework, wrong file layout) is expensive to unwind later. Plan mode is read-only, so Claude can explore and propose a full plan before a single file is written, right when steering is cheapest._ 


### ❓ Question #2

`CLAUDE.md` is loaded into context at the start of every session. What belongs in it — and what *doesn't*? How does this relate to what you learned about context management and memory in Session 3?

#### ✅ Answer


**Belongs**: *run and test commands, the one architecture decision that isn’t obvious from reading the code (here, that the chat logic is isolated in one swappable function), and conventions worth enforcing (plain JS, no frameworks, keep the stub isolated).*

**Doesn’t belong**: *anything discoverable by reading the code itself, long prose, or stale information. Every line costs context tokens in every future session.*

*This is the same lesson as Session 3’s context management: context is scarce, so you only load what earns its keep. CLAUDE.md is functionally a standing system message injected at the start of every session, the same way a curated system prompt beats dumping everything you know into it.*


### ❓ Question #3

The Agent SDK gives you the same agent loop that powers Claude Code. Compare this to the agent loops you hand-built with LangGraph in Sessions 2–4: what does the SDK give you for free, and what control do you give up?

#### ✅ Answer

**Free**: a battle-tested agent loop with retries and error handling, production file/shell/search tools, the permission system and hooks, automatic context compaction, MCP client support, subagents, and session persistence. That’s most of what I hand-assembled piece
by piece since Session 2. 

**Given up**: *fine-grained control over each loop iteration (no intercepting and rewriting a reasoning step the way a custom LangGraph node lets you), choice of model provider (Claude only), and arbitrary custom state graph topologies, everything runs through one fixed loop shape.* 

*In short, the SDK trades control for velocity. It’s a great fit when the task looks like “coding agent answering questions about a repo,” less of a fit when the workflow needs a genuinely custom multi-branch graph.* 

### ❓ Question #4

Your chat app could have called a chat completions API directly, the way you did early in the course. What do you gain by routing every message through the Agent SDK's `query()` instead — and what new risks does an agent with tools introduce that a plain chat completion doesn't have? How did your tool allowlist and permission mode address them?

#### ✅ Answer

**Gain**: *query() gives the whole agent loop for free, tool use, retries, context management, permissions, instead of one text completion. The app can genuinely answer questions about a codebase, not just chat about it in the abstract.* 

**New risk**: *an agent with tools can act, not just talk. A plain completion can only generate text; an agent with Read/Glob/Grep (or worse, Bash) could read or touch things it shouldn’t, especially since this agent runs headless on a server with no human clicking “approve” on each step.* 

**How it’s addressed**: *the allowlist (Read, Glob, Grep, plus the two explicitly named custom tools) is the intended boundary — but I learned the hard way that `allowed_tools` alone is only a pre-approval list, not an exclusive gate: in a first test the agent happily ran `Bash` even though it wasn’t on the list, because in headless mode there’s no human to prompt. The fix was `permission_mode="dontAsk"`, which denies anything not pre-approved, backed by an explicit `disallowed_tools` blocklist (Bash, Write, Edit, …). With those in place the agent structurally cannot run shell commands or edit files no matter what a user types. `max_turns=25` caps runaway loops, and errors are caught and returned as a polite chat reply instead of a stack trace or a hung request.* 

## Activity 1: Level Up the Chat App

Extend your working chat app with **at least one** of the following (built with Claude Code, of course):

1. **Live progress streaming** — stream the agent's activity to the browser (e.g. via Server-Sent Events) so users see tool calls ("reading `app.py`…") while the agent works, instead of a spinner
2. **Multi-conversation support** — a sidebar of separate conversations, each mapped to its own SDK session
3. **A second custom tool** — something genuinely useful for your target repo (e.g. `git_log` for recent changes, or a test-runner summary tool)

Whichever you pick, demo it in your Loom video and explain the design decision in one paragraph.

#### ✅ What I built

I did two of these: **#3 (a second custom tool)** and **#1 (live progress streaming)**.

*Design decision:* I refactored the core agent loop into a single async generator, `generate_reply_stream()`, that yields typed events — one per tool call as it happens (`{"type": "tool", "label": "Reading main.py…"}`) and a final `{"type": "result", "reply": …}`. Both endpoints run through this one path: the browser UI consumes it over Server-Sent Events (`GET /api/chat/stream`) via `EventSource`, and the plain `POST /api/chat` just drains the same generator and returns the last event, so there's no duplicated `query()` loop. I chose SSE over WebSockets because the data only flows one direction (server → browser) and EventSource is a few lines with automatic reconnection; the trade-off is that EventSource only does GET, so the message rides in the query string, which is fine for this app's short prompts. The second tool, `git_log`, is read-only like `count_lines`, so it fits the same safety story — it can report commit history but can't change it.

## Advanced Activity: The Cat Shop Concierge

Connect your Session 8 cat shop MCP server to your chat app's agent via the SDK's `mcp_servers` option. Your chat app becomes a shopping concierge: users can browse the catalog, fill a cart, and check out — in natural language, through the UI you built, hitting the OAuth-protected server you wrote in Session 8.

Include your findings and a demo in your Loom video.

## Ship 🚢

The working chat app!

### Deliverables

- A short Loom showing:
  - Claude Code scaffolding or extending the app (plan → implement → verify — show the plan!); and
  - the chat app answering real questions about a repository, including at least one visible custom-tool use

## Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped a chat app powered by the Claude Agent SDK — scaffolded entirely with Claude Code! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI agents. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#ClaudeCode #AgentSDK #AIAgents #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

## Submitting Your Homework (Optional For Extra Mark)

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your repo:

```bash
git checkout main
git pull upstream main
git push origin main
```

2. Work through `01_Installing_Claude_Code.md`, `02_Using_Claude_Code.md`, and `03_Claude_Agent_SDK.md` in order.
3. Build your chat app in a new `chat-app/` folder inside this session directory (include its `CLAUDE.md` — we want to see it!).
4. Fill in your answers to Questions #1–#4 in this README.
5. Complete Activity #1 and record your Loom video.
6. Add, commit, and push your work to your origin repository. Remove `.env` files and API keys before committing.

When submitting your homework, provide the GitHub URL to your repo.
