import streamlit as st
import json
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import graphviz
import matplotlib.pyplot as plt

from backend.demo.demo_runner import (
    run_demo
)

from backend.services.business_health_service import (
    calculate_business_health
)

from backend.services.mongodb_memory_service import (
    MongoDBMemoryService
)

from backend.services.insight_service import (
    load_latest_insight
)

# -----------------------------------
# HELPER
# -----------------------------------

from bson import ObjectId
import json
import pandas as pd


def safe_dataframe(data):

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    for col in df.columns:

        df[col] = df[col].apply(
            lambda x:
                json.dumps(x, indent=2)
                if isinstance(x, (dict, list))
                else str(x)
                if isinstance(x, ObjectId)
                else x
        )

    datetime_cols = [
        "created_at",
        "updated_at",
        "timestamp",
        "completed_at"
    ]

    for col in datetime_cols:

        if col in df.columns:
            df[col] = df[col].astype(str)

    return df

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="AI SMB Command Center",
    layout="wide"
)

AUTO_REFRESH = False

if AUTO_REFRESH:
    st_autorefresh(
        interval=5000,
        key="dashboard_refresh"
    )

memory = MongoDBMemoryService()

# -----------------------------------
# LOAD DATA
# -----------------------------------

with open("backend/data/customers.json", "r") as file:
    customers = json.load(file)

metrics = calculate_business_health(customers)

try:

    workflows = memory.get_workflows()

except Exception as e:

    st.error(
        f"MongoDB Error: {e}"
    )

    workflows = []

try:

    tasks = memory.get_agent_tasks()

except Exception as e:

    st.error(
        f"MongoDB Error: {e}"
    )

    tasks = []

try:

    agent_memory = memory.load_memory()

except Exception as e:

    st.error(
        f"MongoDB Error: {e}"
    )

    agent_memory = []

try:

    profiles = memory.get_all_customer_profiles()

except Exception as e:

    st.error(
        f"MongoDB Error: {e}"
    )

    profiles = []

try:

    messages = memory.get_agent_messages()

except Exception as e:

    st.error(
        f"MongoDB Error: {e}"
    )

    messages = []

# -----------------------------------
# TITLE
# -----------------------------------

st.title("🚀 AI SMB Survival Command Center")

col_a, col_b = st.columns(2)

with col_a:

    if st.button("Generate Demo Data"):

        run_demo()

        st.success("Demo data generated.")

with col_b:

    if st.button("Reset Demo"):

        memory.workflow_collection.delete_many({})
        memory.memory_collection.delete_many({})
        memory.task_collection.delete_many({})
        memory.message_collection.delete_many({})
        memory.customer_profile_collection.delete_many({})

        st.success("Database cleared.")
    
# -----------------------------------
# EXECUTIVE BRIEF
# -----------------------------------

st.divider()

st.subheader("Executive Brief")

executive_brief_doc = memory.get_latest_executive_brief()

if executive_brief_doc:

    brief = executive_brief_doc.get("finding", {})

    c1, c2 = st.columns(2)

    c1.metric(
        "Priority",
        brief.get("priority", "N/A")
    )

    c2.metric(
        "Revenue At Risk",
        f"${brief.get('revenue_at_risk', 0)}"
    )

    st.write("### Executive Summary")

    st.info(
        brief.get(
            "executive_summary",
            "No summary available."
        )
    )

    st.write("### Recommended Actions")

    for action in brief.get("recommended_actions", []):

        st.write(f"\u2705 {action}")

else:

    st.info("No Executive Brief Available.")

# -----------------------------------
# BUSINESS KPIs
# -----------------------------------

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

col1.metric(
    "Total Customers",
    metrics["total_customers"]
)

col2.metric(
    "High Risk Customers",
    metrics["high_risk_customers"]
)

col3.metric(
    "Revenue At Risk",
    f"${metrics['revenue_at_risk']}"
)

col4.metric(
    "Business Health Score",
    metrics["business_health_score"]
)

col5.metric(
    "Escalations",
    metrics["total_escalations"]
)

col6.metric(
    "Agent Messages",
    len(messages)
)

completed = len(
    [
        w
        for w in workflows
        if w.get("status") == "completed"
    ]
)

col7.metric(
    "Completed Workflows",
    completed
)

st.divider()

# -----------------------------------
# WORKFLOW TRACKING
# -----------------------------------

st.subheader("Workflow Tracking")

if workflows:
    st.dataframe(
        safe_dataframe(workflows),
        width="stretch"
    )
else:
    st.info("No workflows found.")

# -----------------------------------
# AGENT TASKS
# -----------------------------------

st.divider()

st.subheader("Agent Task Delegation")

if tasks:
    st.dataframe(
        safe_dataframe(tasks),
        width="stretch"
    )
else:
    st.info("No agent tasks found.")

# -----------------------------------
# AGENTIC AI METRICS
# -----------------------------------

completed_tasks = len([
    t for t in tasks
    if t.get("status") == "completed"
])

supervisor_count = len([
    x for x in agent_memory
    if x.get("agent_name") == "supervisor_agent"
])

st.divider()

st.subheader("Agentic AI Metrics")

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric(
    "Workflows",
    len(workflows)
)

m2.metric(
    "Agent Decisions",
    len(agent_memory)
)

m3.metric(
    "Tasks Delegated",
    len(tasks)
)

m4.metric(
    "Completed Tasks",
    completed_tasks
)

m5.metric(
    "Supervisor Decisions",
    supervisor_count
)

# -----------------------------------
# CUSTOMER TABLE
# -----------------------------------

st.divider()

st.subheader("Customer Risk Table")

st.dataframe(
    safe_dataframe(customers),
    width="stretch"
)

# -----------------------------------
# CUSTOMER 360
# -----------------------------------

st.divider()

st.subheader("Customer 360 Profiles")

if profiles:

    customer_names = [
        p.get("customer_name", "Unknown")
        for p in profiles
    ]

    selected_customer = st.selectbox(
        "Select Customer",
        customer_names,
        key="customer_360_select"
    )

    selected_profile = next(
        (
            p for p in profiles
            if p.get("customer_name") == selected_customer
        ),
        {}
    )

    if selected_profile:

        p1, p2, p3 = st.columns(3)

        p1.metric(
            "Risk Level",
            selected_profile.get("last_risk_level", "N/A")
        )

        p2.metric(
            "Churn Score",
            selected_profile.get("last_churn_score", "N/A")
        )

        p3.metric(
            "Incidents",
            selected_profile.get("incident_count", 0)
        )

        st.write(
            "**Customer ID:**",
            selected_profile.get("customer_id", "N/A")
        )

        st.caption(
            f"Last Updated: {selected_profile.get('updated_at', 'N/A')}"
        )

else:
    st.info("No customer profiles found.")

# -----------------------------------
# AGENT MEMORY TIMELINE
# -----------------------------------

st.divider()

st.subheader("Agent Memory Timeline")

timeline_df = safe_dataframe(agent_memory)

if not timeline_df.empty:

    display_cols = [
        col
        for col in [
            "workflow_id",
            "customer_id",
            "agent_name",
            "timestamp"
        ]
        if col in timeline_df.columns
    ]

    st.dataframe(
        timeline_df[display_cols],
        width="stretch"
    )

else:
    st.info("No agent memory found.")

# -----------------------------------
# AUTONOMOUS ACTIONS
# -----------------------------------

st.divider()

st.subheader("Autonomous Actions")

autonomous_entries = [
    x for x in agent_memory
    if x.get("agent_name") == "autonomous_actions"
]

if autonomous_entries:

    latest_actions = autonomous_entries[-1].get("finding", {})

    if isinstance(latest_actions, dict):

        ac1, ac2, ac3 = st.columns(3)

        with ac1:
            st.write("**Email**")
            if latest_actions.get("email"):
                st.success("✅ Sent")
            else:
                st.warning("⏸ Not Sent")

        with ac2:
            st.write("**Ticket**")
            if latest_actions.get("ticket"):
                st.success("✅ Created")
            else:
                st.warning("⏸ Not Created")

        with ac3:
            st.write("**CRM Task**")
            if latest_actions.get("crm"):
                st.success("✅ Scheduled")
            else:
                st.warning("⏸ Not Scheduled")

else:
    st.info("No autonomous actions recorded yet.")

# -----------------------------------
# EXECUTIVE INSIGHTS
# -----------------------------------

st.divider()

st.subheader("AI Executive Insights")

churn_findings = [
    x for x in agent_memory
    if x.get("agent_name") == "churn_agent"
]

root_findings = [
    x for x in agent_memory
    if x.get("agent_name") == "root_cause_agent"
]

recovery_findings = [
    x for x in agent_memory
    if x.get("agent_name") == "recovery_agent"
]

if churn_findings or root_findings:

    ei1, ei2, ei3, ei4 = st.columns(4)

    highest_risk = max(
        churn_findings,
        key=lambda x: x.get("finding", {}).get("churn_score", 0)
        if isinstance(x.get("finding"), dict) else 0,
        default=None
    ) if churn_findings else None

    ei1.metric(
        "Revenue At Risk",
        f"${metrics['revenue_at_risk']}"
    )

    ei2.metric(
        "Highest Risk Customer",
        highest_risk.get("finding", {}).get("customer_name", "N/A")
        if highest_risk and isinstance(highest_risk.get("finding"), dict)
        else "N/A"
    )

    latest_root = root_findings[-1] if root_findings else {}
    root_finding = latest_root.get("finding", {})
    issue = (
        root_finding.get("root_cause_category", "N/A")
        if isinstance(root_finding, dict) else "N/A"
    )
    ei3.metric("Most Common Issue", issue)

    latest_recovery = recovery_findings[-1] if recovery_findings else {}
    rec_finding = latest_recovery.get("finding", {})
    rec = (
        rec_finding.get("immediate_action", "See Recovery Plan")
        if isinstance(rec_finding, dict) else "See Recovery Plan"
    ) or "N/A"
    ei4.metric(
        "Recommendation",
        str(rec)[:25] if rec else "N/A"
    )

else:
    st.info(
        "No executive insights available yet. Run a workflow first."
    )

# -----------------------------------
# RECENT AGENT DECISIONS
# -----------------------------------

st.divider()

st.subheader("Recent Agent Decisions")

for item in reversed(agent_memory[-10:]):

    with st.container():

        st.markdown(
            f"### {item.get('agent_name')}"
        )

        st.caption(
            str(item.get("timestamp"))
        )

        st.json(
            item.get("finding") or {}
        )

# -----------------------------------
# WORKFLOW TIMELINE
# -----------------------------------

st.divider()

st.subheader("Workflow Explorer")

selected_workflow = None

workflow_ids = [
    w["workflow_id"]
    for w in workflows
]

if workflow_ids:

    selected_workflow = st.selectbox(
        "Select Workflow",
        workflow_ids
    )

    workflow = next(
        (w for w in workflows if w["workflow_id"] == selected_workflow),
        None
    )

    if workflow:
        st.success(f"Workflow Status: {workflow['status']}")

    timeline = memory.get_workflow_timeline(
        selected_workflow
    )

    expected_agents = [
        "sentiment_agent",
        "supervisor_agent",
        "churn_agent",
        "root_cause_agent",
        "recovery_agent",
        "executive_agent"
    ]

    ran_agents = set(
        e.get("agent_name") for e in timeline
    )

    completed_count = len(
        [a for a in expected_agents if a in ran_agents]
    )

    st.write(
        f"**Workflow Progress:** {completed_count}/{len(expected_agents)} agents completed"
    )

    st.progress(completed_count / len(expected_agents))

    st.subheader("Workflow Timeline")

    for event in timeline:

        with st.expander(
            f"\u2705 {event.get('agent_name')}"
        ):

            st.json(
                event.get("finding") or {}
            )

            st.caption(
                str(event.get("timestamp"))
            )

    workflow_tasks = memory.get_workflow_tasks(
        selected_workflow
    )

    st.write("Total Tasks:", len(workflow_tasks))

    st.subheader("Workflow Tasks")

    if workflow_tasks:

        st.dataframe(
            safe_dataframe(workflow_tasks),
            width="stretch"
        )

else:

    st.warning(
        "No workflows available yet."
    )

# -----------------------------------
# AGENT COMMUNICATION NETWORK
# -----------------------------------

st.divider()

st.subheader(
    "Agent Communication Network"
)

if workflow_ids:

    messages = memory.get_agent_messages(
        selected_workflow
    )

    communication_graph = graphviz.Digraph()

    communication_graph.attr(
        rankdir="LR",
        bgcolor="white"
    )

    communication_graph.attr(
        "node",
        shape="box",
        style="filled",
        fillcolor="lightblue",
        fontsize="11"
    )

    if messages:

        for msg in messages:

            snippet = msg.get("message", "").strip()[:35]

            communication_graph.edge(
                msg["from_agent"],
                msg["to_agent"],
                label=snippet
            )

        st.graphviz_chart(
            communication_graph,
            width="stretch"
        )

        st.subheader(
            "Agent Messages"
        )

        for msg in messages:

            with st.expander(
                f"{msg['from_agent']} ➜ {msg['to_agent']}"
            ):

                st.write(
                    msg["message"]
                )
                
                if "created_at" in msg:

                    st.caption(
                        str(msg["created_at"])
                    )

    else:

        st.info(
            "No agent communication found for this workflow."
        )

# -----------------------------------
# ANALYTICS CHARTS
# -----------------------------------

st.divider()

st.subheader("Analytics Charts")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    st.write("**Customer Risk Distribution**")

    risk_counts = {}
    for c in customers:
        risk = c.get("risk_level", "Unknown")
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

    if risk_counts:
        fig1, ax1 = plt.subplots(figsize=(4, 3))
        ax1.pie(
            risk_counts.values(),
            labels=risk_counts.keys(),
            autopct="%1.0f%%",
            colors=["#e74c3c", "#f39c12", "#2ecc71", "#95a5a6"]
        )
        ax1.set_title("Customer Risk Levels")
        st.pyplot(fig1)
        plt.close(fig1)

with chart_col2:

    st.write("**Agent Execution Count**")

    agent_counts = {}
    for x in agent_memory:
        name = x.get("agent_name", "unknown")
        agent_counts[name] = agent_counts.get(name, 0) + 1

    if agent_counts:
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.barh(
            list(agent_counts.keys()),
            list(agent_counts.values()),
            color="#3498db"
        )
        ax2.set_xlabel("Executions")
        ax2.set_title("Agent Executions")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:

    st.write("**Churn Score by Customer**")

    churn_data = {
        x.get("customer_id", "?"): x.get("finding", {}).get("churn_score", 0)
        for x in agent_memory
        if x.get("agent_name") == "churn_agent"
        and isinstance(x.get("finding"), dict)
    }

    if churn_data:
        fig3, ax3 = plt.subplots(figsize=(5, 3))
        ax3.bar(
            list(churn_data.keys()),
            list(churn_data.values()),
            color="#e67e22"
        )
        ax3.set_ylabel("Churn Score")
        ax3.set_title("Churn Scores")
        ax3.set_ylim(0, 100)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)
    else:
        st.info("No churn data yet.")

with chart_col4:

    st.write("**Workflow Status Breakdown**")

    wf_status = {}
    for w in workflows:
        s = w.get("status", "unknown")
        wf_status[s] = wf_status.get(s, 0) + 1

    if wf_status:
        fig4, ax4 = plt.subplots(figsize=(4, 3))
        ax4.pie(
            wf_status.values(),
            labels=wf_status.keys(),
            autopct="%1.0f%%",
            colors=["#27ae60", "#e74c3c", "#3498db"]
        )
        ax4.set_title("Workflow Status")
        st.pyplot(fig4)
        plt.close(fig4)
    else:
        st.info("No workflow data yet.")

# -----------------------------------
# MULTI-AGENT ARCHITECTURE
# -----------------------------------

st.divider()

st.subheader(
    "Multi-Agent Architecture"
)

architecture_graph = graphviz.Digraph()

architecture_graph.attr(
    rankdir="LR"
)

architecture_graph.node(
    "Customer"
)

architecture_graph.node(
    "Sentiment Agent"
)

architecture_graph.node(
    "Supervisor Agent"
)

architecture_graph.node(
    "MongoDB Memory"
)

architecture_graph.node(
    "Churn Agent"
)

architecture_graph.node(
    "Root Cause Agent"
)

architecture_graph.node(
    "Task Delegation"
)

architecture_graph.node(
    "Recovery Agent"
)

architecture_graph.node(
    "Executive Agent"
)

architecture_graph.node(
    "Autonomous Actions"
)

architecture_graph.edge(
    "Customer",
    "Sentiment Agent"
)

architecture_graph.edge(
    "Sentiment Agent",
    "Supervisor Agent"
)

architecture_graph.edge(
    "Supervisor Agent",
    "MongoDB Memory"
)

architecture_graph.edge(
    "MongoDB Memory",
    "Churn Agent"
)

architecture_graph.edge(
    "MongoDB Memory",
    "Root Cause Agent"
)

architecture_graph.edge(
    "Root Cause Agent",
    "Task Delegation"
)

architecture_graph.edge(
    "Task Delegation",
    "Recovery Agent"
)

architecture_graph.edge(
    "Recovery Agent",
    "Executive Agent"
)

architecture_graph.edge(
    "Executive Agent",
    "Autonomous Actions"
)

st.graphviz_chart(
    architecture_graph,
    width="stretch"
)