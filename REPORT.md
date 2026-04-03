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

**Files changed:**
- `nanobot/config.json` — Added CRITICAL RULE to system prompt: "When the user asks 'What went wrong?' or 'Check system health', you MUST NOT ask for clarification. You MUST immediately investigate by calling these tools in order..."
- `nanobot/workspace/skills/observability/SKILL.md` — Added "Multi-Step Investigation" section with 4-step workflow (error count → log search → trace fetch → synthesis)
- `nanobot/Dockerfile` — Rebuilt to include `mcp_observability` module that was missing

**Agent response to "What went wrong? Please check system health and investigate any errors.":**

```
Here's what I found:

## 🔴 System Health Summary

### LMS Backend: **UNHEALTHY**
- Status: `unhealthy` (HTTP 404)
- Item count: `unknown`

### Root Cause: **Database DNS Resolution Failure**

The Learning Management Service is failing to connect to its database. The error `[Errno -2] Name or service not known` on `db_query` (SELECT on `item` table) means the service **cannot resolve the database hostname**.

### Error Timeline (last hour)
| Time | Event | Detail |
|------|-------|--------|
| 18:47:54 | `db_query` ERROR | Name or service not known |
| 18:32:58 | `db_query` ERROR | Name or service not known |
| 18:07:51 | `db_query` ERROR | Name or service not known |

The errors occur roughly every 15–25 minutes, suggesting periodic retries or health checks. Each DB failure cascades into `unhandled_exception` errors.

### Additional Issue
The **VictoriaTraces** backend is also returning a `400 Bad Request`, so detailed trace investigation isn't available right now.

---

## Recommended Actions

1. **Check database hostname** — Verify the DB connection string/environment variable in the LMS service config. The hostname may be misspelled or the DB container/service may be down.
2. **Check DNS / Docker networking** — If running in Docker/Kubernetes, ensure the LMS service and database are on the same network and the DB service name is resolvable.
3. **Verify database is running** — Check if the database process/container is actually up and accepting connections.
4. **VictoriaTraces** — The traces backend needs attention too (400 errors on the Jaeger API endpoint).
```

The agent successfully chained evidence from:
- **Log evidence**: `logs_error_count` found 9 errors, `logs_search` identified `socket.gaierror` on DNS resolution
- **Trace evidence**: VictoriaTraces returned 400 (misconfigured), but log trace IDs were visible
- **Synthesis**: Identified root cause as database DNS resolution failure with timeline

---

## Task 4B — Proactive health check

**Cron job creation response:**

```
Done! ✅ The health check is scheduled to run every 2 minutes (job ID: `965e94f8`).

Each run will:
1. Check for backend errors in the last 2 minutes
2. Inspect traces if errors found
3. Post a short summary here
```

**Scheduled jobs list:**

```
Here are your scheduled jobs:

- **Health Check** (id: `965e94f8`) — runs every 2 minutes
  - Next run: 2026-04-03 18:56:31 UTC
```

**Proactive health report (captured from chat while PostgreSQL was stopped):**

```
## 🏥 Health Check Summary

**LMS Backend Status:** ❌ **UNHEALTHY** (HTTP 404)

**Errors in last 2 minutes:** 1

| Time | Method | Path | Status | Severity |
|------|--------|------|--------|----------|
| 19:02:56 | POST | `/interactions/` | **503** | ERROR |
| 19:03:06 | GET | `/items/` | **404** | INFO |

**Details:**
- The health check itself hit a **404** on `/items/`, suggesting the endpoint may be missing or misconfigured.
- A **503 Service Unavailable** error occurred on `POST /interactions/` about 10 seconds earlier — this is the actual backend error.

The backend appears to be having issues serving requests. The 503 could indicate a downstream dependency failure or the service being overloaded/unavailable.
```

**Cron job removal:** The agent successfully removed the test health check job via `cron(action="remove", job_id="965e94f8")`.

---

## Task 4C — Bug fix and recovery

### 1. Root Cause

**Planted bug location:** `backend/app/routers/interactions.py`, `post_interaction()` handler (lines 36-48).

**The bug:** The handler only caught `IntegrityError` exceptions but did not handle other database failures (connection errors, DNS resolution failures, pool exhaustion). When PostgreSQL was unavailable, the raw exception bubbled up to the global exception handler, which returned a 500 response with the full Python traceback — leaking internal implementation details.

### 2. Fix

**File:** `backend/app/routers/interactions.py`

**Change:** Added a broad `except Exception` clause after the `IntegrityError` handler:

```python
@router.post("/", response_model=InteractionLog, status_code=201)
async def post_interaction(
    body: InteractionLogCreate, session: AsyncSession = Depends(get_session)
):
    """Create a new interaction log."""
    try:
        return await create_interaction(
            session,
            learner_id=body.learner_id,
            item_id=body.item_id,
            kind=body.kind,
        )
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc.orig),
        )
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {exc}",
        ) from exc
```

**Before fix** (raw traceback leaked):
```json
{"detail":"[Errno -2] Name or service not known","type":"gaierror","path":"/interactions/","traceback":["  File \"...asyncpg/connect_utils.py\"...","  File \"uvloop/loop.pyx\"...","socket.gaierror: [Errno -2] Name or service not known\n"]}
```

**After fix** (clean 503):
```json
{"detail":"Database error: [Errno -2] Name or service not known"}
```

### 3. Post-fix response to "What went wrong?" (after redeploy, PostgreSQL stopped)

```
Here's what I found:

## 🔴 System Health Summary

### LMS Backend: **UNHEALTHY**
- Health check returns **HTTP 404**
- Item count: **unknown**

### Error Count: **11 errors in the last hour** (all from Learning Management Service)

---

## Root Cause: **Database DNS Resolution Failure**

The core issue is `socket.gaierror: [Errno -2] Name or service not known` — the LMS application **cannot resolve the hostname of its PostgreSQL database**.

### Error Flow:
1. A request hits `POST /interactions/`
2. The handler calls `create_interaction()` → `session.commit()`
3. SQLAlchemy tries to acquire a DB connection from the pool
4. `asyncpg` attempts to connect to the PostgreSQL server
5. **DNS lookup fails** → `socket.gaierror: [Errno -2] Name or service not known`

### Timeline:
| Time | Error |
|------|-------|
| 18:01 | `connection is closed` — DB was previously connected but dropped |
| 18:07 | DNS failure begins (`Name or service not known`) |
| 18:24 | 2 more unhandled exceptions (same DNS issue) |
| 18:32 | 2 more unhandled exceptions |
| 18:46 | 1 more unhandled exception |
| 18:47 | DB query failure on `SELECT` from `item` table |
| 18:50 | Most recent error |

### Likely Causes:
- **Database hostname misconfigured** in environment variables
- **Database container/service went down** or was restarted with a different hostname
- **Network/DNS issue** in the container environment
```

The agent now reports the **real underlying database failure** instead of a broken exception-handling path with raw tracebacks.

### 4. Healthy follow-up (after PostgreSQL restarted)

After restarting PostgreSQL with `docker compose start postgres`:

```
curl -X POST http://localhost:42001/interactions/ \
  -H "Authorization: Bearer 13" \
  -H "Content-Type: application/json" \
  -d '{"learner_id": 14, "item_id": 14, "kind": "attempt"}'

Response: {"id":14630,"item_id":14,"score":null,"external_id":null,"learner_id":14,"kind":"attempt","created_at":"2026-04-03T19:06:03.743694"}
```

✅ System fully recovered — interactions being created successfully, agent reports healthy status on subsequent health checks.
