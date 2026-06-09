# SMB Sentinel AI — Multi-Tenant Customer Intelligence Platform

> **Google Rapid Agent Hackathon** | MongoDB MCP + Gemini 2.5 Flash + 6 AI Agents

AI-powered customer churn prevention platform for small businesses. Each business owner logs in and gets their own personalized dashboard with real-time customer sentiment analysis, churn prediction, and one-click recovery actions — all powered by a multi-agent system communicating through the Model Context Protocol (MCP).

## What It Does

A salon owner, cafe owner, or electronics store owner logs in and instantly sees:
- Which customers are unhappy and why
- AI-generated recovery plans for each at-risk customer
- One-click "Email" / "WhatsApp" buttons to execute recovery actions
- Root cause analysis of customer complaints
- Full visibility into the AI agent pipeline working behind the scenes

**Zero PyMongo. Zero direct DB calls. Every MongoDB operation flows through MCP.**

## Demo Accounts

| Username | Password | Business | Industry |
|----------|----------|----------|----------|
| `priya` | `demo123` | Glow Beauty Studio | Salon & Wellness |
| `arjun` | `demo123` | Brew Culture Cafe | Food & Beverage |
| `rahul` | `demo123` | Sharma Electronics | Electronics Retail |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT DASHBOARD (dashboard.py)                 │
│          Login → Per-Business View → Action Buttons                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                    ORCHESTRATOR (orchestrator.py)                     │
│         Routes workflow through 6 AI agents, passes MCP client       │
└──┬──────────┬──────────┬──────────┬──────────┬──────────┬───────────┘
   │          │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼          ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌──────────┐
│Sentiment││Super-  ││Churn   ││Root    ││Recovery││Executive │
│Agent    ││visor   ││Agent   ││Cause   ││Agent   ││Agent     │
│(Gemini) ││(Gemini)││(Gemini)││(Gemini)││(Gemini)││(Gemini)  │
└────┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘└────┬─────┘
     │         │          │         │         │          │
     └─────────┴──────────┴─────────┴─────────┴──────────┘
                              │
                     ┌────────▼────────┐
                     │  MCP Client     │ (backend/mcp_client.py)
                     │  Persistent     │ (stdio transport)
                     │  Session        │
                     └────────┬────────┘
                              │
                     ┌────────▼────────────────┐
                     │  Official MongoDB MCP    │
                     │  Server v1.12.0          │
                     │  (mongodb-mcp-server)    │
                     └────────┬────────────────┘
                              │
                     ┌────────▼────────┐
                     │  MongoDB Atlas   │
                     │  (smb_sentinel)  │
                     └─────────────────┘
```

## Key Features

- **Multi-Tenant Platform** — Each business owner gets their own login, data, and dashboard
- **MongoDB MCP Integration** — All DB operations via the official MongoDB MCP Server (zero PyMongo)
- **6 AI Agents** — Sentiment, Supervisor, Churn, Root Cause, Recovery, Executive (Gemini 2.5 Flash)
- **Inter-Agent Communication** — Agents share findings and messages through MCP memory
- **One-Click Actions** — "Email" / "WhatsApp" buttons on each recovery plan, logged to MongoDB
- **Industry-Specific Insights** — Salon sees appointment data, cafe sees menu insights, electronics sees warranty issues
- **Autonomous Actions** — Auto-generates recovery emails, escalation tickets, CRM tasks, executive alerts
- **Real-Time Dashboard** — Animated Streamlit dashboard with Google-style design

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for the official MongoDB MCP Server)
- **MongoDB Atlas** cluster (free tier works)
- **Google Gemini API Key** (Gemini 2.5 Flash)

## Quick Start

```bash
# 1. Clone and enter the project
cd smb-sentimental-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install the official MongoDB MCP Server
npm install -g mongodb-mcp-server

# 5. Create .env file
cat > .env << EOF
MONGO_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/?retryWrites=true&w=majority
GEMINI_API_KEY=your_gemini_api_key
EOF

# 6. Test MCP connection
python test_mcp_connection.py

# 7. Launch the dashboard
streamlit run dashboard.py
```

## How To Demo (Step by Step)

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the full recording script.

**Quick version:**
1. `streamlit run dashboard.py`
2. Login as `arjun / demo123` (Brew Culture Cafe)
3. Click "Scan Messages" — watch AI analyze 10 customers in real-time
4. Show the dashboard sections: alerts, health chart, recovery plans
5. Click "Email" on a recovery card — shows action logged via MCP
6. Scroll to "Under The Hood" — show agent pipeline and MCP operations
7. Logout → Login as `priya / demo123` — show different business, different data

## Agents

| Agent | Role | MCP Operations |
|-------|------|----------------|
| **Sentiment Agent** | Analyzes customer messages via Gemini | `insert-many` (save finding) |
| **Supervisor Agent** | Routes to downstream agents based on severity | `insert-many` (save routing decision) |
| **Churn Agent** | Predicts churn risk score | `find` (context), `update-many` (profile) |
| **Root Cause Agent** | Identifies operational root cause | `find` (context), `insert-many` (message to recovery) |
| **Recovery Agent** | Creates personalized recovery strategy | `find` (tasks), `update-many` (complete task) |
| **Executive Agent** | Generates executive brief + priority | `insert-many` (save brief) |

## MongoDB Collections (via MCP)

| Collection | Purpose |
|-----------|---------|
| `workflows` | Tracks orchestration runs (active/completed) |
| `agent_memory` | All agent findings & decisions |
| `agent_tasks` | Task delegation between agents |
| `agent_messages` | Inter-agent communication |
| `customer_profiles` | Evolving customer 360 profiles |
| `executed_actions` | Email/WhatsApp actions triggered by owner |

## MCP Tools Used

All operations use the **official MongoDB MCP Server** (not a custom wrapper):

| Tool | Purpose |
|------|---------|
| `find` | Query documents (memory, profiles, workflows) |
| `insert-many` | Insert documents (workflows, findings, messages, actions) |
| `update-many` | Update documents (complete workflows, upsert profiles) |
| `delete-many` | Clean up (dashboard reset) |
| `count` | Count documents |
| `aggregate` | Complex queries |

## Project Structure

```
smb-sentimental-ai/
├── dashboard.py                    # Multi-tenant Streamlit dashboard
├── backend/
│   ├── main.py                     # CLI entry point
│   ├── orchestrator.py             # Multi-agent workflow engine
│   ├── mcp_client.py               # MongoDB MCP client (persistent session)
│   ├── agents/
│   │   ├── sentiment_agent.py      # Gemini sentiment analysis
│   │   ├── supervisor_agent.py     # Agent routing
│   │   ├── churn_agent.py          # Churn prediction
│   │   ├── root_cause_agent.py     # Root cause identification
│   │   ├── recovery_agent.py       # Recovery strategy generation
│   │   └── executive_agent.py      # Executive brief
│   ├── services/
│   │   ├── gemini_service.py       # Gemini API with exponential backoff
│   │   ├── analytics_service.py    # Churn scoring algorithms
│   │   └── business_health_service.py
│   ├── tools/
│   │   ├── email_tool.py           # Recovery emails
│   │   ├── ticket_tool.py          # Escalation tickets
│   │   ├── crm_tool.py             # CRM follow-up tasks
│   │   └── notification_tool.py    # Executive alerts
│   ├── data/
│   │   ├── business_config.json    # Business registry
│   │   └── businesses/
│   │       ├── salon.json          # Glow Beauty Studio (10 customers)
│   │       ├── cafe.json           # Brew Culture Cafe (10 customers)
│   │       └── electronics.json    # Sharma Electronics (10 customers)
│   └── demo/
│       └── demo_runner.py          # Pipeline runner (loads per-business data)
├── test_mcp_connection.py
├── requirements.txt
├── DEMO_SCRIPT.md                  # Demo recording instructions
└── .env                            # MONGO_URI + GEMINI_API_KEY
```

## How MCP Works Here

1. `dashboard.py` creates a persistent `MongoMCPClient()` session (cached via Streamlit)
2. The client spawns the official `mongodb-mcp-server` as a subprocess (stdio transport)
3. All agents receive the MCP client and call tools like `find`, `insert-many`, `update-many`
4. The MongoDB MCP Server translates MCP calls into actual MongoDB operations
5. Results flow back through the MCP protocol to the agents
6. The dashboard reads the same data via MCP `find` queries (limit=100)
7. Action buttons (Email/WhatsApp) write to `executed_actions` collection via MCP

## Hackathon Highlights

- **Zero direct PyMongo calls** — everything goes through MCP protocol
- **Official MongoDB MCP Server v1.12.0** — not a custom wrapper
- **Persistent MCP session** — server starts once, all calls reuse the connection
- **Multi-tenant SaaS** — 3 businesses with separate logins and industry-specific data
- **One-click actions** — business owner can send recovery emails/WhatsApp directly
- **Production patterns** — exponential backoff, auto-reconnect, graceful degradation
- **6 AI agents** collaborating through shared MCP memory

---

**Built for the Google Rapid Agent Hackathon** | MongoDB MCP + Gemini 2.5 Flash + Multi-Agent AI
