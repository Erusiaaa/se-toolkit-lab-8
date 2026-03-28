# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Question 1:** "What is the agentic loop?"

```
The agentic loop is the fundamental operating cycle that enables AI agents to act as active problem 
solvers rather than passive question-answerers.

Core Pattern: Think → Act → Observe → Repeat

 Phase    What Happens                                                                               
 ─────────────────────────────────────────────────────────────────────────────────────────────────── 
 Think    The agent evaluates context, considers available tools, and decides what step to take next 
 Act      The agent takes action—calling tools, executing code, querying APIs, reading files         
 Observe  The agent receives feedback about what actually happened (success, error, data)            
 Repeat   The observation informs the next thought/action cycle until the task is complete          

Why It Matters

Traditional AI: Single input → single output. No verification, no adaptation.

Agentic AI: Continuous iteration. The agent can recognize when it needs more information, course-correct
when something goes wrong, and break complex goals into smaller steps.
```

**Question 2:** "What labs are available in our LMS?" (bare agent, no tools yet)

```
The agent answered based on training data, describing Lab 08 tasks and previous labs from the lab plan.
It did not have access to real LMS backend data at this stage.
```

## Task 1B — Agent with LMS tools

**Question 1:** "What labs are available?" (with MCP tools)

```
Here are all the labs available in your LMS:

 ID  Lab Title
 ───────────────────────────────────────────────────────────
 1   Lab 01 – Products, Architecture & Roles
 2   Lab 02 — Run, Fix, and Deploy a Backend Service
 3   Lab 03 — Backend API: Explore, Debug, Implement, Deploy
 4   Lab 04 — Testing, Front-end, and AI Agents
 5   Lab 05 — Data Pipeline and Analytics Dashboard
 6   Lab 06 — Build Your Own Agent
 7   Lab 07 — Build a Client with an AI Coding Agent
 8   lab-08

You're currently working on Lab 08 ("The Agent is the Interface"), which focuses on deploying nanobot as
an AI agent interface with MCP tools, observability integration, and proactive health checks.
```

**Question 2:** "Describe the architecture of the LMS system"

```
The Learning Management Service (LMS) is a Docker Compose-based educational platform following the C4
architecture model.

🏗️ Container Architecture (7 Services)

 Container     Port        Technology                 Purpose
 ───────────────────────────────────────────────────────────────────────────────────────
 Caddy         42002       Go                         Reverse proxy + static file server
 FastAPI       42001       Python, SQLModel, Uvicorn  REST API with Swagger UI
 PostgreSQL    42004       PostgreSQL                 Relational database
 pgAdmin       42003       pgAdmin 4                  Database management UI
 Nanobot       8765/18790  Python, nanobot-ai         AI agent gateway
 Telegram Bot  -           Python, aiogram            Telegram relay to Nanobot

🗃️ Data Model (OBER-Compatible)

Three core entities:
 • Item — Learning content in a tree hierarchy (course → lab → task → step)
 • Learner — Students enrolled in the system
 • Interacts — Interaction logs linking learners to items (view, attempt, complete)

🔧 FastAPI Components

 HTTP Routers → Auth Middleware → Database Access → PostgreSQL
    ├─ /items         (Bearer token)    ├─ items.py
    ├─ /learners                        ├─ learners.py
    └─ /interactions                    └─ interactions.py

🔐 Security
 • API: Bearer token via Authorization header
 • WebSocket: Query parameter ?access_key=SECRET
 • Feature flags: Optional endpoints via env vars

🔄 Request Flow
 1 Web: Browser → Caddy (static files) → Caddy (API proxy) → FastAPI → PostgreSQL
 2 AI: Nanobot → MCP tools → FastAPI → PostgreSQL
 3 Telegram: Telegram → Bot → WebSocket → Nanobot → LLM → MCP tools → FastAPI

Current Status: ✅ Healthy (56 items in database)
```

## Task 1C — Skill prompt

**Question:** "Show me the scores" (without specifying a lab)

```
The agent asked for clarification and listed available labs, then provided a completion rate summary:

 Lab     Completion Rate  Passed  Total
 ──────────────────────────────────────
 lab-01  ✅ 100.0%        258     258
 lab-02  ⚠️ 89.1%         131     147
 lab-03  ⚠️ 89.1%         156     175
 lab-04  ✅ 96.7%         238     246
 lab-05  ✅ 98.4%         246     250
 lab-06  ✅ 98.4%         241     245
 lab-07  ✅ 99.6%         236     237
 lab-08  🆕 0.0%          0       0

Key Insights
 • Highest completion: Lab 01 (100%) - foundational lab, everyone passes
 • Lowest completion: Labs 02 & 03 (~89%) - these involve hands-on deployment and debugging
 • Strong recovery: Labs 04-07 all above 96% - students gain momentum after the initial hurdles
 • Lab 08: Just launched (0 submissions yet)
```

## Task 2A — Deployed agent

**Nanobot startup log excerpt:**

```
[entrypoint] Using resolved config: /app/nanobot/config.resolved.json
[entrypoint] Using workspace: /app/nanobot/workspace
🐈 Starting nanobot gateway version 0.1.4.post6 on port 18790...
2026-03-28 10:54:10.280 | INFO | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
✓ Channels enabled: webchat
✓ Heartbeat: every 1800s
2026-03-28 10:54:10.739 | INFO | nanobot.channels.manager:start_all:91 - Starting webchat channel...
2026-03-28 10:54:12.486 | INFO | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'lms': connected, 9 tools registered
2026-03-28 10:54:12.486 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```

**Verification:**
- `docker compose ps` shows nanobot service running
- WebChat channel enabled in logs
- MCP tools registered (9 LMS tools)

## Task 2B — Web client

**Flutter client accessible at:** `http://localhost:42002/flutter/`

**WebSocket endpoint:** `/ws/chat` (proxied through Caddy to nanobot:8765)

**Access key:** `nano-web-pass-789` (configured in `.env.docker.secret`)

**Test results:**
- Flutter web client loads successfully at `/flutter`
- WebSocket channel enabled and listening
- Agent ready to receive connections

**Files created/modified:**
- `nanobot/entrypoint.py` — Runtime config resolver for Docker deployment
- `nanobot/Dockerfile` — Multi-stage build with uv
- `nanobot/config.json` — Added webchat channel config
- `nanobot/pyproject.toml` — Added nanobot-webchat dependency
- `docker-compose.yml` — Uncommented nanobot, client-web-flutter services
- `caddy/Caddyfile` — Uncommented `/ws/chat` and `/flutter` routes
- `nanobot-websocket-channel/` — Git submodule for webchat channel

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
