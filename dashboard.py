"""
SMB Sentinel AI — Intelligent Business Command Center
Google Rapid Agent Hackathon | MongoDB MCP + Gemini Multi-Agent AI

Dual-purpose dashboard:
  1. SMB Owner View — Actionable business insights for daily operations
  2. AI Engine View — Technical showcase for hackathon judges
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from backend.demo.demo_runner import run_demo
from backend.services.business_health_service import calculate_business_health
from backend.mcp_client import MongoMCPClient


# ═══════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════

st.set_page_config(
    page_title="SMB Sentinel AI | Business Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google-inspired color theme
GOOGLE_BLUE = "#4285F4"
GOOGLE_RED = "#EA4335"
GOOGLE_YELLOW = "#FBBC05"
GOOGLE_GREEN = "#34A853"
GOOGLE_DARK = "#202124"
GOOGLE_GRAY = "#5F6368"
GOOGLE_LIGHT_GRAY = "#F8F9FA"
GOOGLE_BORDER = "#DADCE0"

st.markdown(f"""
<style>
    .stApp {{
        background: #ffffff;
    }}
    [data-testid="stMetric"] {{
        background: {GOOGLE_LIGHT_GRAY};
        border: 1px solid {GOOGLE_BORDER};
        border-radius: 8px;
        padding: 16px;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.8rem !important;
        font-weight: 600;
        color: {GOOGLE_DARK};
    }}
    [data-testid="stMetricLabel"] {{
        color: {GOOGLE_GRAY};
        font-weight: 500;
    }}
    .mcp-pulse {{
        display: inline-block;
        width: 8px;
        height: 8px;
        background: {GOOGLE_GREEN};
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 8px;
    }}
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(52, 168, 83, 0.6); }}
        70% {{ box-shadow: 0 0 0 8px rgba(52, 168, 83, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(52, 168, 83, 0); }}
    }}
    .hero-title {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {GOOGLE_DARK};
        margin-bottom: 0;
        font-family: 'Google Sans', 'Segoe UI', sans-serif;
    }}
    .action-card {{
        padding: 14px 16px;
        background: #f1f8f1;
        border: 1px solid #c8e6c9;
        border-radius: 8px;
        margin: 6px 0;
    }}
    .alert-card {{
        padding: 14px 16px;
        background: #fef0f0;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        margin: 6px 0;
    }}
    .insight-card {{
        padding: 18px;
        background: {GOOGLE_LIGHT_GRAY};
        border: 1px solid {GOOGLE_BORDER};
        border-radius: 8px;
        margin: 8px 0;
    }}
    [data-testid="stSidebar"] {{
        background: {GOOGLE_LIGHT_GRAY};
        border-right: 1px solid {GOOGLE_BORDER};
    }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# MCP CLIENT
# ═══════════════════════════════════════════

@st.cache_resource
def get_mcp_client():
    client = MongoMCPClient()
    client.connect()
    return client

mcp = get_mcp_client()


# ═══════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════

def safe_str(value, default=""):
    """Safely convert any value (including BSON dicts) to string."""
    if value is None:
        return default
    if isinstance(value, dict):
        for key in ("$date", "$oid", "$numberLong"):
            if key in value:
                return str(value[key])
        return str(value)
    return str(value)


# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="margin: 0; color: {GOOGLE_DARK}; font-weight: 600;">SMB Sentinel</h2>
        <p style="color: {GOOGLE_GRAY}; margin: 4px 0; font-size: 0.85rem;">AI Business Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(f"""
    <div style="padding: 10px 14px; background: #ffffff; border-radius: 8px; border: 1px solid {GOOGLE_BORDER};">
        <span class="mcp-pulse"></span>
        <strong style="color: {GOOGLE_GREEN};">MCP Connected</strong>
        <br><small style="color: {GOOGLE_GRAY};">MongoDB Atlas via MCP Protocol</small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown(f"#### Actions")

    if st.button("Analyze New Messages", use_container_width=True):
        run_demo(mcp)
        st.success("Analysis complete")
        st.rerun()

    if st.button("Refresh Dashboard", use_container_width=True):
        st.rerun()

    if st.button("Clear All Data", use_container_width=True):
        for coll in ["workflows", "agent_memory", "agent_tasks", "agent_messages", "customer_profiles"]:
            mcp.call_tool("delete-many", {
                "database": "smb_sentinel",
                "collection": coll,
                "filter": {}
            })
        st.success("Data reset complete")
        st.rerun()

    st.markdown("---")
    st.markdown("#### Technology Stack")
    st.markdown(f"""
    <div style="font-size: 0.85rem; color: {GOOGLE_GRAY}; line-height: 1.8;">
        Google Gemini 2.5 Flash<br>
        MongoDB Atlas (MCP)<br>
        Model Context Protocol<br>
        6 Autonomous AI Agents
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════

with open("backend/data/customers.json", "r") as file:
    customers = json.load(file)

metrics = calculate_business_health(customers)
workflows = mcp.get_workflows()
tasks = mcp.get_agent_tasks()
agent_memory = mcp.load_memory()
profiles = mcp.get_all_customer_profiles()
messages = mcp.get_agent_messages()

if not isinstance(workflows, list): workflows = []
if not isinstance(tasks, list): tasks = []
if not isinstance(agent_memory, list): agent_memory = []
if not isinstance(profiles, list): profiles = []
if not isinstance(messages, list): messages = []


# ═══════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════

st.markdown(f"""
<div style="padding: 10px 0 20px 0;">
    <p class="hero-title">SMB Sentinel AI</p>
    <p style="color: {GOOGLE_GRAY}; font-size: 1.05rem; margin-top: 4px;">
        AI-powered business guardian — monitoring customer health, predicting churn, and taking action automatically.
    </p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# SECTION 1: BUSINESS OWNER VIEW
# ═══════════════════════════════════════════

completed = len([w for w in workflows if isinstance(w, dict) and w.get("status") == "completed"])
high_risk_pct = round((metrics["high_risk_customers"] / max(metrics["total_customers"], 1)) * 100)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Customers", metrics["total_customers"])
k2.metric("At Risk", metrics["high_risk_customers"], delta=f"-{high_risk_pct}%", delta_color="inverse")
k3.metric("Revenue At Risk", f"₹{metrics['revenue_at_risk']:,}")
k4.metric("Business Health", f"{metrics['business_health_score']}/100")
k5.metric("Issues Resolved", f"{completed}/{len(workflows)}")


# --- TODAY'S PRIORITIES ---
st.markdown("")
st.markdown("### Today's Priorities")

executive_brief_doc = mcp.get_latest_executive_brief()
brief = {}
if isinstance(executive_brief_doc, list) and len(executive_brief_doc) > 0:
    brief = executive_brief_doc[0].get("finding", {}) if isinstance(executive_brief_doc[0], dict) else {}

priority_col, action_col = st.columns([1, 1])

with priority_col:
    if brief:
        priority = brief.get("priority", "N/A")
        colors = {"Critical": GOOGLE_RED, "High": "#E57373", "Medium": GOOGLE_YELLOW, "Low": GOOGLE_GREEN}
        color = colors.get(priority, GOOGLE_GRAY)

        st.markdown(f"""
        <div class="alert-card">
            <p style="color:{GOOGLE_RED}; font-size:0.8rem; margin:0; font-weight:600; text-transform:uppercase;">Highest Priority Alert</p>
            <p style="color:{color}; font-size:1.4rem; font-weight:700; margin:8px 0;">{priority} Risk</p>
            <p style="color:{GOOGLE_GRAY}; margin:0; font-size:0.9rem;">
                {safe_str(brief.get('executive_summary', 'No summary available.'))[:200]}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="action-card">
            <p style="color:{GOOGLE_GREEN}; font-size:1.1rem; margin:0; font-weight:600;">All Clear</p>
            <p style="color:{GOOGLE_GRAY}; margin:4px 0 0 0;">No critical issues. Click "Analyze New Messages" to process incoming customer feedback.</p>
        </div>
        """, unsafe_allow_html=True)

with action_col:
    st.markdown("**Recommended Actions:**")
    if brief and brief.get("recommended_actions"):
        for i, action in enumerate(brief.get("recommended_actions", [])[:3], 1):
            st.markdown(f"""
            <div class="action-card">
                <strong style="color:{GOOGLE_BLUE};">Action {i}:</strong>
                <span style="color:{GOOGLE_DARK};"> {safe_str(action)[:120]}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        pending = len([t for t in tasks if isinstance(t, dict) and t.get("status") == "pending"])
        st.markdown(f"""
        <div class="action-card">
            <p style="color:{GOOGLE_DARK}; margin:0;"><strong>{pending}</strong> pending follow-ups</p>
            <p style="color:{GOOGLE_DARK}; margin:4px 0 0 0;">Recovery emails sent automatically</p>
            <p style="color:{GOOGLE_DARK}; margin:4px 0 0 0;">Escalation tickets created</p>
        </div>
        """, unsafe_allow_html=True)


# --- CUSTOMER HEALTH ---
st.markdown("")
st.markdown("### Customer Health Monitor")

health_tab, timeline_tab = st.tabs(["Customer Overview", "Activity Timeline"])

with health_tab:
    if profiles:
        prof_data = []
        for p in profiles:
            if isinstance(p, dict):
                prof_data.append({
                    "Customer": safe_str(p.get("customer_name", "Unknown")),
                    "Risk Level": safe_str(p.get("last_risk_level", "Unknown")),
                    "Churn Score": p.get("last_churn_score", 0),
                    "Last Issue": safe_str(p.get("last_root_cause", "None")),
                    "Incidents": p.get("incident_count", 0),
                })

        if prof_data:
            df_prof = pd.DataFrame(prof_data)

            fig_gauge = go.Figure()
            for i, row in df_prof.iterrows():
                score = row["Churn Score"] if isinstance(row["Churn Score"], (int, float)) else 0
                fig_gauge.add_trace(go.Bar(
                    x=[score],
                    y=[row["Customer"]],
                    orientation='h',
                    marker_color=GOOGLE_RED if score >= 70 else GOOGLE_YELLOW if score >= 40 else GOOGLE_GREEN,
                    text=f"{score}%",
                    textposition="outside",
                    name=row["Customer"]
                ))

            fig_gauge.update_layout(
                title="Customer Churn Risk Score",
                xaxis=dict(range=[0, 100], title="Risk %", gridcolor="#E8EAED"),
                yaxis=dict(gridcolor="#E8EAED"),
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
                font=dict(color=GOOGLE_DARK, family="Google Sans, Segoe UI, sans-serif"),
                showlegend=False,
                height=200 + (len(prof_data) * 40),
                margin=dict(l=100, t=40)
            )
            st.plotly_chart(fig_gauge, key="churn_gauge")

            st.dataframe(df_prof, width="stretch", hide_index=True)
    else:
        st.info("No customer profiles yet. Click **Analyze New Messages** to start monitoring.")

with timeline_tab:
    if workflows:
        timeline_data = []
        for w in workflows:
            if isinstance(w, dict):
                timeline_data.append({
                    "Time": safe_str(w.get("created_at", ""))[:16].replace("T", " "),
                    "Customer": safe_str(w.get("customer_id", "Unknown")),
                    "Status": "Resolved" if w.get("status") == "completed" else "Active",
                })
        if timeline_data:
            st.dataframe(pd.DataFrame(timeline_data), width="stretch", hide_index=True)
    else:
        st.info("No activity yet.")


# --- AUTONOMOUS ACTIONS ---
st.markdown("")
st.markdown("### Autonomous Actions")

auto_col1, auto_col2, auto_col3, auto_col4 = st.columns(4)

email_count = len([m for m in agent_memory if isinstance(m, dict) and m.get("agent_name") == "autonomous_actions"])
ticket_count = len([t for t in tasks if isinstance(t, dict)])

auto_col1.metric("Recovery Emails", email_count)
auto_col2.metric("Tickets Created", ticket_count)
auto_col3.metric("CRM Tasks", email_count)
auto_col4.metric("Executive Alerts", email_count)

if email_count > 0:
    st.success(f"AI automatically sent {email_count} recovery email(s), created {ticket_count} escalation ticket(s), and notified executives without manual intervention.")


# ═══════════════════════════════════════════
# SECTION 2: AI ENGINE (For Judges)
# ═══════════════════════════════════════════

st.markdown("---")
st.markdown(f"""
<div style="padding: 10px 0;">
    <h3 style="color: {GOOGLE_BLUE}; font-weight: 600;">AI Engine — Under The Hood</h3>
    <p style="color: {GOOGLE_GRAY}; font-size: 0.9rem;">Technical architecture for hackathon judges — every operation below flows through the MongoDB MCP Server</p>
</div>
""", unsafe_allow_html=True)

engine_tab1, engine_tab2, engine_tab3, engine_tab4 = st.tabs([
    "Agent Pipeline",
    "Inter-Agent Messages",
    "Task Delegation",
    "MCP Operations"
])

with engine_tab1:
    agent_names = ["sentiment_agent", "supervisor_agent", "churn_agent", "root_cause_agent", "recovery_agent", "executive_agent"]
    agent_labels = ["Sentiment", "Supervisor", "Churn", "Root Cause", "Recovery", "Executive"]
    agent_colors = [GOOGLE_BLUE, "#7B1FA2", GOOGLE_RED, GOOGLE_YELLOW, GOOGLE_GREEN, "#00ACC1"]

    exec_counts = [
        len([m for m in agent_memory if isinstance(m, dict) and m.get("agent_name") == name])
        for name in agent_names
    ]

    if any(exec_counts):
        fig = go.Figure(data=[
            go.Bar(
                x=agent_labels,
                y=exec_counts,
                marker=dict(color=agent_colors, line=dict(width=0)),
                text=exec_counts,
                textposition="outside"
            )
        ])
        fig.update_layout(
            title="Agent Execution Count (stored in MongoDB via MCP)",
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font=dict(color=GOOGLE_DARK, family="Google Sans, Segoe UI, sans-serif"),
            xaxis=dict(gridcolor="#E8EAED"),
            yaxis=dict(gridcolor="#E8EAED"),
            height=300,
            margin=dict(t=40, b=20)
        )
        st.plotly_chart(fig, key="agent_chart")

        st.markdown("""
        ```
        Customer Message → [Sentiment Agent] → [Supervisor Agent] → [Churn | Root Cause | Recovery | Executive]
                                    ↓                    ↓                         ↓
                              MCP insert-many      MCP insert-many          MCP find + update-many
                                    ↓                    ↓                         ↓
                              MongoDB Atlas ←←←← All via MCP Protocol ←←←← mongodb-mcp-server
        ```
        """)
    else:
        st.info("Run a demo to see agent execution metrics.")

with engine_tab2:
    if messages:
        for msg in messages[:10]:
            if isinstance(msg, dict):
                st.markdown(f"""
                <div style="padding:12px; margin:6px 0; background:{GOOGLE_LIGHT_GRAY}; border-radius:8px; border-left:3px solid {GOOGLE_BLUE};">
                    <strong style="color:{GOOGLE_BLUE};">{safe_str(msg.get('from_agent', '?'))}</strong>
                    <span style="color:{GOOGLE_GRAY};"> → </span>
                    <strong style="color:#7B1FA2;">{safe_str(msg.get('to_agent', '?'))}</strong>
                    <span style="color:#9E9E9E; font-size:0.75rem;"> (via MCP insert-many)</span>
                    <br>
                    <small style="color:{GOOGLE_GRAY};">{safe_str(msg.get('message', ''))[:150]}...</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No inter-agent messages yet.")

with engine_tab3:
    if tasks:
        task_data = []
        for t in tasks:
            if isinstance(t, dict):
                task_data.append({
                    "Agent": safe_str(t.get("assigned_agent", "")),
                    "Type": safe_str(t.get("task_type", "")),
                    "Status": "Completed" if t.get("status") == "completed" else "Pending",
                    "Created": safe_str(t.get("created_at", ""))[:16]
                })
        if task_data:
            st.dataframe(pd.DataFrame(task_data), width="stretch", hide_index=True)

        completed_tasks = len([t for t in tasks if isinstance(t, dict) and t.get("status") == "completed"])
        if tasks:
            st.progress(completed_tasks / max(len(tasks), 1), text=f"{completed_tasks}/{len(tasks)} tasks completed")
    else:
        st.info("No tasks yet.")

with engine_tab4:
    st.markdown("#### MongoDB MCP Operations Log")
    st.markdown("""
    Every database operation in this system flows through the **Model Context Protocol**:
    
    | Operation | MCP Tool | Collection | Usage |
    |-----------|----------|------------|-------|
    | Save workflow | `insert-many` | workflows | Track orchestration runs |
    | Save agent finding | `insert-many` | agent_memory | Persist AI decisions |
    | Send agent message | `insert-many` | agent_messages | Inter-agent communication |
    | Create task | `insert-many` | agent_tasks | Task delegation |
    | Update profile | `update-many` | customer_profiles | Customer 360 (upsert) |
    | Query data | `find` | all collections | Dashboard reads |
    | Complete workflow | `update-many` | workflows | Mark done |
    | Reset data | `delete-many` | all collections | Dashboard reset |
    """)

    op_col1, op_col2, op_col3 = st.columns(3)
    op_col1.metric("Inserts (insert-many)", len(workflows) + len(agent_memory) + len(messages) + len(tasks))
    op_col2.metric("Queries (find)", "~" + str(6 + len(workflows)))
    op_col3.metric("Updates (update-many)", len(workflows) + len(profiles))


# ═══════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 20px; color: {GOOGLE_GRAY};">
    <p style="font-weight: 600; color: {GOOGLE_DARK};">SMB Sentinel AI</p>
    <p style="font-size: 0.8rem;">
        Google Rapid Agent Hackathon &nbsp;|&nbsp; Official MongoDB MCP Server &nbsp;|&nbsp; Google Gemini 2.5 Flash &nbsp;|&nbsp; 6 AI Agents &nbsp;|&nbsp; Zero PyMongo
    </p>
    <p style="font-size: 0.75rem; color: #9E9E9E;">
        Every database operation via Model Context Protocol (MCP) — Built for small & medium businesses
    </p>
</div>
""", unsafe_allow_html=True)
