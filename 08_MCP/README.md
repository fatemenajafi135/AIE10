<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 8: Model Context Protocol (MCP)</h1>

### [Quicklinks]()

| Session Sheet | Recording | Slides | Repo | Homework | Feedback |
|:--------------|:----------|:-------|:-----|:---------|:---------|
| [Session 8: MCP](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/08_MCP) |[Recording!](https://us02web.zoom.us/rec/share/rqw5I5hwbOOHy8TrGjnu0IjDJi53ykHb0k897jYfyHqZpgRhUuFP4A18d4NrcEKS.18sNk6Do9XwyaVUy) <br> passcode: `E56&^V+8`| [Session 8 Slides](https://canva.link/k8cixqgkfeghdsn) |You are here! | [Session 8 Assignment](https://forms.gle/TcjjChq38ydMjuqn8) | [Feedback 6/25](https://forms.gle/DvcWDgBXatBWCXqi7) |

## Useful Resources

**MCP (Model Context Protocol)**
- [MCP Official Docs](https://modelcontextprotocol.io/) — Spec, tutorials, and guides
- [MCP-UI](https://mcpui.dev/) — Official standard for interactive UI in MCP
- [MCP Auth Guide (Auth0)](https://auth0.com/blog/mcp-specs-update-all-about-auth/) — Deep dive into MCP auth spec updates

## Main Assignment

In this session, you will build an MCP server with OAuth authentication — a cat
shop application that exposes tools for browsing products, managing a cart, and
checking out.

The main entry point is:

```text
server.py
```

The server implementation lives in:

```text
app/
```

Available MCP tools:

- `list_products`
- `get_product`
- `add_to_cart`
- `view_cart`
- `remove_from_cart`
- `checkout`

## Setup

From this folder:

```bash
uv sync
```

Copy the example env file and fill in your OpenAI API key:

```bash
cp .env.example .env
```

## Running the MCP Server

Run the server locally:

```bash
uv run server.py
```

The server starts on `http://localhost:8000`.

### Expose the server with ngrok

In a separate terminal, start an ngrok tunnel:

```bash
ngrok http 8000
```

Copy the ngrok forwarding URL (e.g. `https://xxxx-xx-xx-xx-xx.ngrok-free.app`) and
restart the server with it:

```bash
ISSUER_URL=https://xxxx-xx-xx-xx-xx.ngrok-free.app uv run server.py
```

> **Note:** The `ISSUER_URL` must match the public URL clients use to reach the
> server, otherwise OAuth authentication will fail.

## Outline

### Breakout Room #1

- Set up the MCP server with OAuth and the product database
- Explore the MCP tools: `list_products`, `get_product`, `add_to_cart`, `view_cart`, `remove_from_cart`, `checkout`

### Breakout Room #2

- Connect an MCP client to the server
- Build an end-to-end interaction flow using the MCP tools

## Ship

The completed MCP server and client integration!

### Deliverables

- A short Loom of either:
  - the MCP server you built and a demo of the client interacting with it; or
  - the notebook you created for the Advanced Build

## Share

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped an MCP server with OAuth authentication! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI and tool integration. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#MCP #ModelContextProtocol #OAuth #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

## Submitting Your Homework 

Follow these steps to prepare and submit your homework assignment:

1. Review the MCP server code in `server.py` and the `app/` directory
2. Run the MCP server locally using `uv run server.py`
3. Connect to the server using an MCP client (e.g., Claude Desktop, or a custom client)
4. Test all available tools: browsing products, adding to cart, viewing cart, removing items, and checkout
5. Record a Loom video reviewing what you have learned from this session

## Questions

### Question #1

Why is OAuth important for MCP servers, and what security considerations should you keep in mind when exposing tools to AI clients?

#### Answer

*MCP servers are a significant security risk if left unprotected. They expose tools that can take real-world actions like modifying data, placing orders, calling external APIs, and without authentication, any client (including a malicious AI agent) can call them freely and anonymously.*

*OAuth addresses this at multiple levels:*

- *Authorization via scopes: defines what each client is allowed to do. For example, separating read (browsing) from write (modifying state) means we can issue limited-access tokens when full access isn't needed.*

- *Per-user identity: tools that act on behalf of a user like a shopping cart, a personal inbox, or a user profile, can only work correctly if the server knows who is making the call. OAuth ties every request to an identity via the access token.*

- *Token revocation: if a client or agent misbehaves, we can revoke its token immediately without affecting other users. Without auth, there's no selective way to cut off one bad actor.*

- *Rate limiting per identity: once we have identity, we can enforce per-user limits fairly. This also makes it harder to abuse the server with bulk unauthenticated requests.*

- *Client accountability and auditability: registered clients have IDs, so every call can be traced back to a specific client. It's useful for debugging, billing, or security investigations.*

*Additional security considerations: We can use HTTPS in production, keep token lifetimes short, validate token expiry on every request, and apply the principle of least privilege when assigning scopes.*

### Question #2

What is Streamable HTTP transport in MCP, and why might you expose a server publicly with OAuth instead of using a local stdio connection?

#### Answer

***What is Streamable HTTP transport:***

*Streamable HTTP is one of MCP's transport options. It runs the server as a real HTTP server that clients connect to over the network. The "streamable" part means responses can flow back incrementally using server-sent events, rather than as a single blocking response. This is what `uv run server.py` starts: a proper HTTP server on port 8000, not a local pipe.*

*The alternative is stdio transport, where the server runs as a child process tied to a single terminal session, communicating through standard input/output. It only works when a human is running it locally.*

***Why expose publicly with OAuth instead of using stdio:***

- *Remote clients can't reach localhost: if the AI agent is a hosted service (like Claude.ai or a cloud deployment), it has no access to our local machine. A public URL via ngrok or a real deployment is the only way to bridge that gap.*

- *Multi-user support: stdio is inherently one client per process. An HTTP server can handle many concurrent clients, each with their own OAuth token, identity, and isolated state.*

- *Always-on availability: a locally running stdio server dies when we close the terminal. A deployed HTTP server is available 24/7 without a human keeping it alive.*

- *OAuth becomes necessary here: because the server is now reachable by anyone on the internet, we need authentication to control who can call our tools. stdio relied on OS-level process isolation; HTTP has no such built-in protection.*

*In short, Streamable HTTP is what makes MCP servers shareable and production-ready and OAuth is what makes that safe.*


## Activity 1: Extend the MCP Server

Add at least one new tool to the cat shop MCP server (e.g., `search_products`, `update_cart_quantity`, or `get_order_history`). Ensure the new tool integrates properly with the existing database and OAuth authentication. Demo the new tool through an MCP client and include it in your Loom video.

## Advanced Activity: Build a Custom MCP Client

Build a custom MCP client that connects to the cat shop server over Streamable HTTP, authenticates via OAuth, and orchestrates a multi-step shopping flow (browse → add to cart → checkout). Compare the developer experience of MCP-based tool integration vs. traditional REST API calls.

Include your findings and a demo in your Loom video.
