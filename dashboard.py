import streamlit as st
import json
import pandas as pd
from streamlit_autorefresh import st_autorefresh

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
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="AI SMB Command Center",
    layout="wide"
)

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

workflows = memory.get_workflows()

tasks = memory.get_agent_tasks()

agent_memory = memory.load_memory()

profiles = memory.get_all_customer_profiles()

# -----------------------------------
# TITLE
# -----------------------------------

st.title("🚀 AI SMB Survival Command Center")

# -----------------------------------
# BUSINESS KPIs
# -----------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

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

st.divider()

# -----------------------------------
# WORKFLOW TRACKING
# -----------------------------------

st.subheader("Workflow Tracking")

if workflows:
    st.dataframe(
        pd.DataFrame(workflows),
        use_container_width=True
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
        pd.DataFrame(tasks),
        use_container_width=True
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
    pd.DataFrame(customers),
    use_container_width=True
)

# -----------------------------------
# CUSTOMER 360
# -----------------------------------

st.divider()

st.subheader("Customer 360 Profiles")

if profiles:
    st.dataframe(
        pd.DataFrame(profiles),
        use_container_width=True
    )
else:
    st.info("No customer profiles found.")

# -----------------------------------
# AGENT MEMORY TIMELINE
# -----------------------------------

st.divider()

st.subheader("Agent Memory Timeline")

timeline_df = pd.DataFrame(agent_memory)

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
        use_container_width=True
    )

else:
    st.info("No agent memory found.")

# -----------------------------------
# EXECUTIVE INSIGHTS
# -----------------------------------

st.divider()

st.subheader("AI Executive Insights")

try:

    insight = load_latest_insight()

    st.success(insight)

except Exception as e:

    st.warning(
        f"No executive insights available: {e}"
    )

# -----------------------------------
# RECENT AGENT DECISIONS
# -----------------------------------

st.divider()

st.subheader("Recent Agent Decisions")

for item in reversed(agent_memory[-10:]):

    st.info(
        f"""
        Agent: {item.get('agent_name')}

        Workflow: {item.get('workflow_id')}

        Time: {item.get('timestamp')}
        """
    )

# -----------------------------------
# WORKFLOW TIMELINE
# -----------------------------------

st.divider()

st.subheader("Workflow Explorer")

workflow_ids = [
    w["workflow_id"]
    for w in workflows
]

if workflow_ids:

    selected_workflow = st.selectbox(
        "Select Workflow",
        workflow_ids
    )

    timeline = memory.get_workflow_timeline(
        selected_workflow
    )

    st.subheader("Workflow Timeline")

    for event in timeline:

        st.info(
            f"""
            Agent:
            {event.get('agent_name')}

            Time:
            {event.get('timestamp')}

            Finding:
            {str(event.get('finding'))[:300]}
            """
        )

    workflow_tasks = memory.get_workflow_tasks(
        selected_workflow
    )

    st.subheader("Workflow Tasks")

    if workflow_tasks:

        st.dataframe(
            pd.DataFrame(workflow_tasks),
            use_container_width=True
        )

else:

    st.warning(
        "No workflows available yet."
    )