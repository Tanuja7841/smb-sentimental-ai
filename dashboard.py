"""
SMB Sentinel AI — Multi-Tenant Customer Intelligence Platform
Google Rapid Agent Hackathon | MongoDB MCP + Gemini Multi-Agent AI

Each business owner logs in and sees THEIR OWN customer intelligence dashboard.
The AI analyzes THEIR customer messages and provides industry-specific insights.

Demo Accounts:
  - priya / demo123  → Glow Beauty Studio (Salon)
  - arjun / demo123  → Brew Culture Cafe (F&B)
  - rahul / demo123  → Sharma Electronics (Retail)
"""

import streamlit as st
import json
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

from backend.demo.demo_runner import run_demo
from backend.mcp_client import MongoMCPClient


# ═══════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════

st.set_page_config(page_title="SMB Sentinel AI", page_icon="◆", layout="wide", initial_sidebar_state="expanded")

G_BLUE = "#4285F4"
G_RED = "#EA4335"
G_YELLOW = "#FBBC05"
G_GREEN = "#34A853"
G_DARK = "#202124"
G_GRAY = "#5F6368"
G_LIGHT = "#F8F9FA"
G_BORDER = "#DADCE0"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    .stApp {{ background: #f5f7fa; font-family: 'Inter', sans-serif; }}
    [data-testid="stMetric"] {{
        background: white; border: 1px solid {G_BORDER}; border-radius: 12px;
        padding: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        transition: transform 0.2s ease;
    }}
    [data-testid="stMetric"]:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(66,133,244,0.1); }}
    [data-testid="stMetricValue"] {{ font-size: 1.6rem !important; font-weight: 700; color: {G_DARK}; }}
    [data-testid="stMetricLabel"] {{ color: {G_GRAY}; font-weight: 500; }}
    [data-testid="stSidebar"] {{ background: white; border-right: 1px solid {G_BORDER}; }}
    .mcp-pulse {{ display:inline-block; width:8px; height:8px; background:{G_GREEN}; border-radius:50%; animation:pulse 2s infinite; margin-right:8px; }}
    @keyframes pulse {{ 0%{{box-shadow:0 0 0 0 rgba(52,168,83,0.6)}} 70%{{box-shadow:0 0 0 8px rgba(52,168,83,0)}} 100%{{box-shadow:0 0 0 0 rgba(52,168,83,0)}} }}
    .hero {{ background:linear-gradient(135deg,{G_BLUE} 0%,#1a73e8 50%,#185abc 100%); border-radius:16px; padding:28px 36px; margin-bottom:20px; position:relative; overflow:hidden; }}
    .hero::before {{ content:''; position:absolute; top:-50%; right:-20%; width:400px; height:400px; background:rgba(255,255,255,0.04); border-radius:50%; animation:float 6s ease-in-out infinite; }}
    @keyframes float {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-20px)}} }}
    .section-title {{ font-size:1rem; font-weight:600; color:{G_DARK}; margin:20px 0 10px 0; padding-bottom:6px; border-bottom:2px solid {G_BLUE}; display:inline-block; }}
    .card {{ background:white; border:1px solid {G_BORDER}; border-radius:12px; padding:18px; margin:8px 0; }}
    .alert-critical {{ background:#FFEBEE; border:1px solid #FFCDD2; border-left:4px solid {G_RED}; border-radius:8px; padding:14px 18px; margin:8px 0; }}
    .alert-warning {{ background:#FFF3E0; border:1px solid #FFE0B2; border-left:4px solid #FF9800; border-radius:8px; padding:14px 18px; margin:8px 0; }}
    .alert-success {{ background:#E8F5E9; border:1px solid #C8E6C9; border-left:4px solid {G_GREEN}; border-radius:8px; padding:14px 18px; margin:8px 0; }}
    .login-box {{ max-width:400px; margin:80px auto; padding:40px; background:white; border-radius:16px; box-shadow:0 4px 24px rgba(0,0,0,0.08); }}
    .badge {{ display:inline-block; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:600; }}
    .badge-red {{ background:#FFEBEE; color:{G_RED}; }} .badge-green {{ background:#E8F5E9; color:{G_GREEN}; }} .badge-yellow {{ background:#FFF8E1; color:#F57F17; }}
    .action-done {{ background:{G_GREEN}; color:white; border:none; border-radius:6px; padding:4px 10px; font-size:0.68rem; font-weight:500; }}
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

def safe_str(value, default=""):
    if value is None: return default
    if isinstance(value, dict):
        for key in ("$date", "$oid", "$numberLong"):
            if key in value: return str(value[key])
        return str(value)
    return str(value)


# ═══════════════════════════════════════════
# LOAD REGISTRY
# ═══════════════════════════════════════════

with open("backend/data/business_config.json", "r") as f:
    registry = json.load(f)


# ═══════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════

def show_login():
    st.markdown(f"""
    <div style="text-align:center; padding:40px 0 20px 0;">
        <div style="width:60px; height:60px; background:{G_BLUE}; border-radius:14px; display:inline-flex; align-items:center; justify-content:center; margin-bottom:12px;">
            <span style="color:white; font-size:1.6rem; font-weight:800;">S</span>
        </div>
        <h1 style="color:{G_DARK}; font-size:1.8rem; margin:8px 0 4px 0;">SMB Sentinel AI</h1>
        <p style="color:{G_GRAY}; font-size:0.9rem;">Customer Intelligence Platform for Small Businesses</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f'<div style="background:white; padding:30px; border-radius:16px; border:1px solid {G_BORDER};">', unsafe_allow_html=True)
        st.markdown(f"**Sign in to your dashboard**")

        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")

        if st.button("Sign In", use_container_width=True, type="primary"):
            for biz in registry["businesses"]:
                if biz["username"] == username and password == registry["demo_password"]:
                    st.session_state["logged_in"] = True
                    st.session_state["business_file"] = biz["file"]
                    st.session_state["business_id"] = biz["id"]
                    st.rerun()
            st.error("Invalid credentials. Try: priya / demo123")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center; margin-top:20px; color:{G_GRAY}; font-size:0.8rem;">
            <p><strong>Demo Accounts:</strong></p>
            <p>priya / demo123 — Salon Owner</p>
            <p>arjun / demo123 — Cafe Owner</p>
            <p>rahul / demo123 — Electronics Store</p>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# MAIN DASHBOARD
# ═══════════════════════════════════════════

def show_dashboard():
    # Load business data
    biz_file = st.session_state["business_file"]
    with open(f"backend/data/businesses/{biz_file}", "r") as f:
        biz = json.load(f)

    mcp = get_mcp_client()
    customers = biz["customers"]
    messages_data = biz["messages"]

    # Calculate metrics
    total = len(customers)
    unhappy = len([c for c in customers if c["sentiment"] == "negative"])
    happy = len([c for c in customers if c["sentiment"] == "positive"])
    revenue = sum(c["total_spent"] for c in customers)
    at_risk_revenue = sum(c["total_spent"] for c in customers if c["sentiment"] == "negative" or c.get("response_delay_days", 0) > 10)
    health = round((total - unhappy) / max(total, 1) * 100)

    # Load MCP data
    workflows = mcp.get_workflows()
    agent_memory = mcp.load_memory()
    tasks = mcp.get_agent_tasks()
    profiles = mcp.get_all_customer_profiles()
    agent_msgs = mcp.get_agent_messages()

    if not isinstance(workflows, list): workflows = []
    if not isinstance(agent_memory, list): agent_memory = []
    if not isinstance(tasks, list): tasks = []
    if not isinstance(profiles, list): profiles = []
    if not isinstance(agent_msgs, list): agent_msgs = []

    completed_wf = len([w for w in workflows if isinstance(w, dict) and w.get("status") == "completed"])
    sentiment_data = [m for m in agent_memory if isinstance(m, dict) and m.get("agent_name") == "sentiment_agent"]
    recovery_data = [m for m in agent_memory if isinstance(m, dict) and m.get("agent_name") == "recovery_agent"]
    root_cause_data = [m for m in agent_memory if isinstance(m, dict) and m.get("agent_name") == "root_cause_agent"]
    exec_data = [m for m in agent_memory if isinstance(m, dict) and m.get("agent_name") == "executive_agent"]

    # ─── SIDEBAR ───
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding:16px 0;">
            <div style="width:42px; height:42px; background:{biz['color']}; border-radius:10px; display:inline-flex; align-items:center; justify-content:center; margin-bottom:6px;">
                <span style="color:white; font-size:1.2rem; font-weight:700;">{biz['logo_letter']}</span>
            </div>
            <h3 style="margin:6px 0 0 0; color:{G_DARK}; font-size:0.95rem;">{biz['business_name']}</h3>
            <p style="color:{G_GRAY}; margin:2px 0; font-size:0.72rem;">{biz['location']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"""
        <div style="padding:8px 12px; background:{G_LIGHT}; border-radius:8px; border:1px solid {G_BORDER};">
            <span class="mcp-pulse"></span>
            <strong style="color:{G_GREEN}; font-size:0.78rem;">AI Active</strong>
            <small style="color:{G_GRAY};"> — Monitoring {", ".join(biz['channels'][:2])}</small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        if st.button("Scan Messages", use_container_width=True, type="primary"):
            with st.spinner("AI analyzing customer messages..."):
                run_demo(mcp)
            st.rerun()

        if st.button("Refresh", use_container_width=True):
            st.rerun()

        if st.button("Reset Data", use_container_width=True):
            for coll in ["workflows", "agent_memory", "agent_tasks", "agent_messages", "customer_profiles", "executed_actions"]:
                mcp.call_tool("delete-many", {"database": "smb_sentinel", "collection": coll, "filter": {}})
            st.rerun()

        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.markdown(f"""
        <div style="font-size:0.72rem; color:{G_GRAY}; margin-top:12px;">
            <p style="margin:3px 0;"><strong>Industry:</strong> {biz['industry']}</p>
            <p style="margin:3px 0;"><strong>Channels:</strong> {", ".join(biz['channels'])}</p>
        </div>
        """, unsafe_allow_html=True)

    # ─── HERO ───
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

    st.markdown(f"""
    <div class="hero">
        <p style="color:rgba(255,255,255,0.95); font-size:1.5rem; font-weight:700; margin:0; position:relative; z-index:1;">
            {greeting}, {biz['owner']}
        </p>
        <p style="color:rgba(255,255,255,0.7); font-size:0.88rem; margin:6px 0 0 0; position:relative; z-index:1;">
            Here's how <strong>{biz['business_name']}</strong> is doing today — {total} customers monitored across {len(biz['channels'])} channels.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ─── KPIs ───
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Customers", total)
    k2.metric("Unhappy", unhappy, delta=f"{round(unhappy/max(total,1)*100)}%", delta_color="inverse")
    k3.metric("Revenue at Risk", f"₹{at_risk_revenue:,}")
    k4.metric("Health Score", f"{health}%")
    k5.metric("AI Actions", completed_wf)

    # ─── NEEDS ATTENTION ───
    st.markdown(f'<p class="section-title">Needs Your Attention</p>', unsafe_allow_html=True)

    unhappy_customers = [c for c in customers if c["sentiment"] == "negative"]
    unhappy_msgs = {m["customer"]: m for m in messages_data if m.get("severity") in ("High", "Critical")}

    if unhappy_customers:
        att1, att2 = st.columns([3, 2])
        with att1:
            for c in unhappy_customers[:5]:
                msg = unhappy_msgs.get(c["name"], {})
                severity = msg.get("severity", "High")
                alert_class = "alert-critical" if severity == "Critical" else "alert-warning"
                complaint = msg.get("message", "Negative sentiment detected")[:120]
                detail = c.get("preferred_service", c.get("preferred_item", c.get("last_purchase", "")))

                st.markdown(f"""
                <div class="{alert_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong style="color:{G_DARK};">{c['name']}</strong>
                            <span style="color:{G_GRAY}; font-size:0.78rem;"> — {detail} customer | ₹{c['total_spent']:,} lifetime</span>
                        </div>
                        <span class="badge badge-red">{severity}</span>
                    </div>
                    <p style="color:{G_GRAY}; margin:6px 0 0 0; font-size:0.8rem;">"{complaint}"</p>
                </div>
                """, unsafe_allow_html=True)

        with att2:
            # AI Recommendations — informational summary only
            exec_brief = {}
            if exec_data:
                latest = exec_data[-1]
                if isinstance(latest, dict) and isinstance(latest.get("finding"), dict):
                    exec_brief = latest["finding"]

            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<p style="font-weight:600; color:{G_DARK}; margin:0 0 10px 0; font-size:0.85rem;">AI Recommendations</p>', unsafe_allow_html=True)

            if exec_brief and exec_brief.get("recommended_actions"):
                actions = exec_brief.get("recommended_actions", [])
                for i, a in enumerate(actions[:3] if isinstance(actions, list) else [], 1):
                    action_text = safe_str(a)
                    st.markdown(f"""<div style="display:flex;gap:8px;margin:6px 0;"><div style="min-width:18px;height:18px;background:{G_BLUE};color:white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.6rem;font-weight:700;">{i}</div><p style="color:{G_GRAY};margin:0;font-size:0.76rem;">{action_text}</p></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<p style="color:{G_GRAY};font-size:0.8rem;">Click "Scan Messages" to get AI recommendations.</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-success">
            <strong style="color:{G_GREEN};">All customers look happy</strong>
            <p style="color:{G_GRAY}; margin:4px 0 0 0; font-size:0.82rem;">No complaints detected. Scan new messages to stay updated.</p>
        </div>
        """, unsafe_allow_html=True)

    # ─── CUSTOMER HEALTH ───
    st.markdown(f'<p class="section-title">Customer Health</p>', unsafe_allow_html=True)

    tab_overview, tab_feedback = st.tabs(["Overview", "Recent Feedback"])

    with tab_overview:
        rows = []
        for c in customers:
            rows.append({
                "Customer": c["name"],
                "Visits": c["visits"],
                "Last Visit": f"{c['last_visit_days']}d ago",
                "Avg Spend": f"₹{c['avg_spend']:,}",
                "Total Spent": f"₹{c['total_spent']:,}",
                "Status": "Happy" if c["sentiment"] == "positive" else "At Risk" if c["sentiment"] == "negative" else "Neutral"
            })
        df = pd.DataFrame(rows)

        chart_col, donut_col = st.columns([2, 1])
        with chart_col:
            fig = go.Figure()
            sorted_custs = sorted(customers, key=lambda x: x["total_spent"])
            for c in sorted_custs:
                color = G_RED if c["sentiment"] == "negative" else G_GREEN if c["sentiment"] == "positive" else G_YELLOW
                fig.add_trace(go.Bar(
                    x=[c["total_spent"]], y=[c["name"]], orientation='h',
                    marker_color=color, showlegend=False,
                    text=f"₹{c['total_spent']:,}", textposition="outside"
                ))
            fig.update_layout(
                title=dict(text="Customer Lifetime Value (colored by sentiment)", font=dict(size=13, color=G_DARK)),
                xaxis=dict(title="Total Spent (₹)", gridcolor="#E8EAED", zeroline=False),
                yaxis=dict(gridcolor="#E8EAED"),
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(color=G_DARK, family="Inter", size=11),
                height=max(250, total * 35 + 60), margin=dict(l=10, r=40, t=40, b=20), bargap=0.25
            )
            st.plotly_chart(fig, key="ltv_chart", width="stretch")

        with donut_col:
            sent_counts = pd.Series([c["sentiment"] for c in customers]).value_counts()
            fig_d = go.Figure(data=[go.Pie(
                labels=["Happy", "At Risk", "Neutral"][:len(sent_counts)],
                values=sent_counts.values.tolist(), hole=0.65,
                marker=dict(colors=[G_GREEN if "pos" in str(l) else G_RED if "neg" in str(l) else G_YELLOW for l in sent_counts.index]),
                textinfo="label+value", textfont=dict(size=10)
            )])
            fig_d.update_layout(
                title=dict(text="Sentiment Split", font=dict(size=13, color=G_DARK)),
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(color=G_DARK, family="Inter"), height=250,
                margin=dict(l=10, r=10, t=40, b=10), showlegend=False,
                annotations=[dict(text=f"{total}<br>total", x=0.5, y=0.5, font_size=13, showarrow=False)]
            )
            st.plotly_chart(fig_d, key="donut", width="stretch")

        st.dataframe(df, width="stretch", hide_index=True)

    with tab_feedback:
        if sentiment_data:
            for s in sentiment_data[:10]:
                finding = s.get("finding", {})
                if isinstance(finding, dict):
                    cid = safe_str(s.get("customer_id", ""))
                    sent = safe_str(finding.get("sentiment", "N/A"))
                    issue = safe_str(finding.get("primary_issue", finding.get("key_concern", "")))[:100]
                    color = G_RED if "neg" in sent.lower() else G_GREEN if "pos" in sent.lower() else G_YELLOW
                    badge = "badge-red" if "neg" in sent.lower() else "badge-green" if "pos" in sent.lower() else "badge-yellow"
                    st.markdown(f"""
                    <div style="padding:10px 14px; border-left:3px solid {color}; background:white; margin:6px 0; border-radius:0 8px 8px 0;">
                        <div style="display:flex;justify-content:space-between;"><strong style="color:{G_DARK};font-size:0.82rem;">{cid}</strong><span class="badge {badge}">{sent}</span></div>
                        <p style="color:{G_GRAY};margin:4px 0 0 0;font-size:0.76rem;">{issue}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Scan messages to see AI-analyzed customer feedback.")

    # ─── RECOVERY ACTIONS (with Send buttons) ───
    st.markdown(f'<p class="section-title">Recovery Actions</p>', unsafe_allow_html=True)

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Analyzed", len(sentiment_data))
    a2.metric("Recovery Plans", len(recovery_data))
    a3.metric("Tasks Created", len(tasks))
    a4.metric("Resolved", completed_wf)

    if recovery_data:
        # Bulk action bar
        st.markdown(f'<p style="font-weight:500; color:{G_DARK}; margin:12px 0 8px 0; font-size:0.82rem;">Send recovery messages to unhappy customers:</p>', unsafe_allow_html=True)
        bulk1, bulk2, bulk3 = st.columns([1, 1, 3])
        with bulk1:
            if st.button("Email All", key="bulk_email", use_container_width=True, type="primary"):
                for r in recovery_data:
                    cust_id = safe_str(r.get("customer_id", ""))
                    strategy = safe_str(r.get("finding", {}).get("immediate_recovery_plan", ""))[:300]
                    mcp.call_tool("insert-many", {
                        "database": "smb_sentinel",
                        "collection": "executed_actions",
                        "documents": [{
                            "customer_id": cust_id,
                            "action_type": "email",
                            "message": strategy,
                            "executed_by": biz["owner"],
                            "business_id": biz["business_id"],
                            "status": "sent",
                            "executed_at": datetime.utcnow().isoformat()
                        }]
                    })
                st.toast(f"Recovery emails sent to {len(recovery_data)} customers!", icon="✅")
                st.rerun()
        with bulk2:
            if st.button("WhatsApp All", key="bulk_whatsapp", use_container_width=True):
                for r in recovery_data:
                    cust_id = safe_str(r.get("customer_id", ""))
                    strategy = safe_str(r.get("finding", {}).get("immediate_recovery_plan", ""))[:300]
                    mcp.call_tool("insert-many", {
                        "database": "smb_sentinel",
                        "collection": "executed_actions",
                        "documents": [{
                            "customer_id": cust_id,
                            "action_type": "whatsapp",
                            "message": strategy,
                            "executed_by": biz["owner"],
                            "business_id": biz["business_id"],
                            "status": "sent",
                            "executed_at": datetime.utcnow().isoformat()
                        }]
                    })
                st.toast(f"WhatsApp messages sent to {len(recovery_data)} customers!", icon="✅")
                st.rerun()

        st.markdown("---")

        # Per-customer recovery cards with individual action buttons
        for idx, r in enumerate(recovery_data[:6]):
            finding = r.get("finding", {})
            if not isinstance(finding, dict):
                continue
            strategy = safe_str(finding.get("immediate_recovery_plan", finding.get("retention_strategy", "")))
            cust_id = safe_str(r.get("customer_id", ""))
            if not strategy:
                continue

            # Check if already sent
            sent_key = f"sent_{cust_id}_{idx}"

            # Card layout: text | buttons
            card_col, btn_col = st.columns([5, 1])
            with card_col:
                st.markdown(f"""
                <div style="padding:12px 16px; background:white; border:1px solid {G_BORDER}; border-left:4px solid {G_BLUE}; border-radius:0 10px 10px 0; margin:6px 0;">
                    <strong style="color:{G_DARK}; font-size:0.82rem;">{cust_id}</strong>
                    <p style="color:{G_GRAY}; margin:4px 0 0 0; font-size:0.76rem; line-height:1.4;">{strategy}</p>
                </div>
                """, unsafe_allow_html=True)
            with btn_col:
                if st.session_state.get(sent_key):
                    st.markdown(f'<div style="margin-top:20px;"><span class="action-done">Sent</span></div>', unsafe_allow_html=True)
                else:
                    if st.button("Email", key=f"email_{idx}", use_container_width=True):
                        mcp.call_tool("insert-many", {
                            "database": "smb_sentinel",
                            "collection": "executed_actions",
                            "documents": [{
                                "customer_id": cust_id,
                                "action_type": "email",
                                "message": strategy[:300],
                                "executed_by": biz["owner"],
                                "business_id": biz["business_id"],
                                "status": "sent",
                                "executed_at": datetime.utcnow().isoformat()
                            }]
                        })
                        st.session_state[sent_key] = True
                        st.toast(f"Email sent to {cust_id}!", icon="✅")
                        st.rerun()
                    if st.button("WhatsApp", key=f"wa_{idx}", use_container_width=True):
                        mcp.call_tool("insert-many", {
                            "database": "smb_sentinel",
                            "collection": "executed_actions",
                            "documents": [{
                                "customer_id": cust_id,
                                "action_type": "whatsapp",
                                "message": strategy[:300],
                                "executed_by": biz["owner"],
                                "business_id": biz["business_id"],
                                "status": "sent",
                                "executed_at": datetime.utcnow().isoformat()
                            }]
                        })
                        st.session_state[sent_key] = True
                        st.toast(f"WhatsApp sent to {cust_id}!", icon="✅")
                        st.rerun()

        # Root cause chart
        if root_cause_data:
            causes = [safe_str(rc.get("finding", {}).get("root_cause_category", "Unknown"))[:35] for rc in root_cause_data if isinstance(rc.get("finding"), dict)]
            if causes:
                st.markdown("")
                cc = pd.Series(causes).value_counts().head(5)
                fig_rc = go.Figure(data=[go.Bar(x=cc.values.tolist(), y=cc.index.tolist(), orientation='h', marker_color=[G_BLUE, G_RED, G_YELLOW, G_GREEN, "#7B1FA2"][:len(cc)])])
                fig_rc.update_layout(title=dict(text="Why customers are unhappy", font=dict(size=13)), plot_bgcolor="white", paper_bgcolor="white", font=dict(color=G_DARK, family="Inter", size=11), height=200, margin=dict(l=10, r=20, t=40, b=10))
                st.plotly_chart(fig_rc, key="causes", width="stretch")
    else:
        st.info("Click 'Scan Messages' to generate recovery plans. Then you can send them directly to customers.")

    # ─── TECHNICAL (FOR JUDGES) ───
    st.markdown("---")
    st.markdown(f'<p class="section-title" style="border-color:#7B1FA2;">Under The Hood</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{G_GRAY};font-size:0.8rem;">6 AI agents communicate via MongoDB MCP. Zero PyMongo. Zero direct DB calls.</p>', unsafe_allow_html=True)

    j1, j2 = st.tabs(["Agent Pipeline", "MCP Operations"])
    with j1:
        names = ["sentiment_agent", "supervisor_agent", "churn_agent", "root_cause_agent", "recovery_agent", "executive_agent"]
        labels = ["Sentiment", "Supervisor", "Churn", "Root Cause", "Recovery", "Executive"]
        colors = [G_BLUE, "#7B1FA2", G_RED, G_YELLOW, G_GREEN, "#00ACC1"]
        counts = [len([m for m in agent_memory if isinstance(m, dict) and m.get("agent_name") == n]) for n in names]
        if any(counts):
            fig = go.Figure(data=[go.Bar(x=labels, y=counts, marker=dict(color=colors), text=counts, textposition="outside")])
            fig.update_layout(title="Agent Executions", plot_bgcolor="white", paper_bgcolor="white", font=dict(color=G_DARK, family="Inter"), height=240, margin=dict(t=40, b=20))
            st.plotly_chart(fig, key="agents", width="stretch")
        else:
            st.info("Run scan to see agent activity.")

    with j2:
        st.markdown("""| Operation | MCP Tool | Collection |\n|---|---|---|\n| Save workflow | `insert-many` | workflows |\n| Save finding | `insert-many` | agent_memory |\n| Agent message | `insert-many` | agent_messages |\n| Create task | `insert-many` | agent_tasks |\n| Update profile | `update-many` | customer_profiles |\n| Send email/WhatsApp | `insert-many` | executed_actions |\n| Query | `find` | all |""")

    # ─── FOOTER ───
    st.markdown(f"""
    <div style="text-align:center; padding:20px; margin-top:30px; border-top:1px solid {G_BORDER}; color:{G_GRAY};">
        <p style="font-weight:600; color:{G_DARK}; margin:0; font-size:0.85rem;">SMB Sentinel AI</p>
        <p style="font-size:0.72rem; margin:4px 0;">Google Rapid Agent Hackathon | MongoDB MCP | Gemini 2.5 Flash | 6 AI Agents</p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# ROUTING
# ═══════════════════════════════════════════

if st.session_state.get("logged_in"):
    show_dashboard()
else:
    show_login()
