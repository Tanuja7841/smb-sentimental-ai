# 🚀 SMB Sentinel AI — Multi-Agent Customer Churn Prevention

> **Google Rapid Agent Hackathon Project**
> All MongoDB operations powered by the **Model Context Protocol (MCP)**

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        main.py (Entry Point)                      │
│                   with MongoMCPClient() as mcp:                   │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (orchestrator.py)                  │
│         Routes workflow through agents, passes MCP client         │
└──┬──────────┬──────────┬──────────┬──────────┬───────────────────┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────────┐
│Sentiment││Churn   ││Root    ││Recovery││Executive   │
│Agent    ││Agent   ││Cause   ││Agent   ││Agent       │
│(Gemini) ││(Gemini)││Agent   ││(Gemini)││(Gemini)    │
└────┬────┘└────┬───┘└───┬────┘└───┬────┘└─────┬──────┘
     │          │         │         │           │
     └──────────┴─────────┴─────────┴───────────┘
                          │
                    ┌─────▼─────┐
                    │ MCP Client │  (backend/mcp_client.py)
                    │  (stdio)   │
                    └─────┬─────┘
                          │
                    ┌─────▼─────────────────┐
                    │ Official MongoDB MCP   │
                    │ Server (Node.js)       │
                    │ mongodb-mcp-server     │
                    └─────┬─────────────────┘
                          │
                    ┌─────▼─────┐
                    │ MongoDB   │
                    │ Atlas     │
                    └───────────┘
```

## 🔑 Key Features

- **MongoDB MCP Integration** — All database operations flow through the official MongoDB MCP Server via the Model Context Protocol
- **Multi-Agent AI** — 6 specialized agents powered by Google Gemini 2.5 Flash
- **Inter-Agent Communication** — Agents share context and messages through MCP
- **Persistent Memory** — Agent findings stored in MongoDB via MCP for cross-workflow learning
- **Supervisor Routing** — Intelligent agent selection using Gemini + deterministic business rules
- **Autonomous Actions** — Auto-triggers emails, tickets, CRM tasks, executive alerts
- **Real-time Dashboard** — Streamlit command center reading all data via MCP
- **Exponential Backoff** — Graceful handling of Gemini rate limits (503/429)

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for the official MongoDB MCP Server)
- **MongoDB Atlas** cluster (free tier works)
- **Google Gemini API Key**

## ⚡ Quick Start

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

# 7. Run the full pipeline
python -m backend.main

# 8. Launch the dashboard
streamlit run dashboard.py
```

## 🧠 Agents

| Agent | Role | MCP Operations |
|-------|------|----------------|
| **Sentiment Agent** | Analyzes customer messages via Gemini | `insert-many` (save finding) |
| **Supervisor Agent** | Routes to downstream agents | `insert-many` (save decision) |
| **Churn Agent** | Predicts churn risk score | `find` (context), `update-many` (profile) |
| **Root Cause Agent** | Identifies operational issues | `find` (context), `insert-many` (message) |
| **Recovery Agent** | Creates recovery strategies | `find` (tasks, messages), `update-many` (complete task) |
| **Executive Agent** | Generates executive briefs | `insert-many` (save brief) |

## 🔧 MongoDB MCP Tools Used

All operations use the **official MongoDB MCP Server** tools:

| Tool | Purpose |
|------|---------|
| `find` | Query documents (agent memory, profiles, workflows) |
| `insert-many` | Insert documents (workflows, findings, messages, tasks) |
| `update-many` | Update documents (complete workflows, upsert profiles) |
| `delete-many` | Clean up (dashboard reset) |
| `count` | Count documents |
| `aggregate` | Complex queries |
| `list-collections` | Inspect database structure |

## 📁 Project Structure

```
smb-sentimental-ai/
├── backend/
│   ├── main.py                 # Entry point — MCP lifecycle
│   ├── orchestrator.py         # Multi-agent workflow engine
│   ├── mcp_client.py           # MongoDB MCP client (persistent session)
│   ├── agents/
│   │   ├── sentiment_agent.py  # Gemini sentiment analysis
│   │   ├── supervisor_agent.py # Agent routing (Gemini + rules)
│   │   ├── churn_agent.py      # Churn prediction
│   │   ├── root_cause_agent.py # Root cause identification
│   │   ├── recovery_agent.py   # Recovery strategy generation
│   │   └── executive_agent.py  # Executive brief generation
│   ├── services/
│   │   ├── gemini_service.py   # Gemini API with retry logic
│   │   ├── analytics_service.py# Churn scoring algorithms
│   │   ├── business_health_service.py
│   │   ├── insight_service.py
│   │   ├── live_metric_services.py
│   │   └── correlation_service.py
│   ├── tools/
│   │   ├── email_tool.py       # Recovery emails
│   │   ├── ticket_tool.py      # Escalation tickets
│   │   ├── crm_tool.py         # CRM follow-up tasks
│   │   ├── notification_tool.py# Executive alerts
│   │   └── sentiment_alert_tool.py
│   ├── data/
│   │   ├── customers.json      # Sample customer data
│   │   └── whatsapp_messages.json
│   └── demo/
│       └── demo_runner.py      # Demo data generator
├── dashboard.py                # Streamlit dashboard (MCP-powered)
├── test_mcp_connection.py      # MCP connection test
├── requirements.txt
└── .env                        # MONGO_URI + GEMINI_API_KEY
```

## 🔄 How MCP Works Here

1. **`main.py`** creates a single `MongoMCPClient()` with a persistent session
2. The client spawns the official `mongodb-mcp-server` as a subprocess (stdio transport)
3. All agents receive the MCP client and call tools like `find`, `insert-many`, `update-many`
4. The MongoDB MCP Server translates MCP tool calls into MongoDB operations
5. Results flow back through the MCP protocol to the agents
6. The Streamlit dashboard reads the same data via MCP `find` queries

## 🏆 Hackathon Highlights

- **Zero direct PyMongo calls** in the agent/orchestration layer — everything goes through MCP
- **Official MongoDB MCP Server** — not a custom wrapper
- **Persistent MCP session** — server starts once, all calls reuse the connection (~0.1s per call)
- **Production-grade patterns** — retry logic, dependency injection, graceful degradation
- **6 AI agents** working collaboratively through shared MCP memory

## 📊 MongoDB Collections (via MCP)

| Collection | Purpose |
|-----------|---------|
| `workflows` | Tracks orchestration runs |
| `agent_memory` | Agent findings & decisions |
| `agent_tasks` | Task delegation between agents |
| `agent_messages` | Inter-agent communication |
| `customer_profiles` | Evolving customer 360 profiles |

---

**Built for the Google Rapid Agent Hackathon** | MongoDB MCP + Gemini 2.5 Flash + Multi-Agent AI
