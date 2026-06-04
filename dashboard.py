import streamlit as st
import json
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="AI SMB Command Center",
    layout="wide"
)

st_autorefresh(interval=5000, key="dashboard_refresh")
from backend.services.business_health_service import (
    calculate_business_health
)

from backend.services.memory_service import (
    load_memory
)

from backend.services.insight_service import (
    load_latest_insight
)

st.set_page_config(
    page_title="AI SMB Command Center",
    layout="wide"
)


st.title("AI SMB Survival Command Center")


# LOAD CUSTOMER DATA

with open("backend/data/customers.json", "r") as file:

    customers = json.load(file)


# BUSINESS HEALTH

metrics = calculate_business_health(customers)


# TOP KPI ROW

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


# CUSTOMER TABLE

st.subheader("Customer Risk Table")

df = pd.DataFrame(customers)

st.dataframe(df)


st.divider()


# MEMORY EVENTS

st.subheader("Operational Memory Events")

memory = load_memory()

st.json(memory)

st.subheader("AI Root Cause Monitoring")

for item in memory:

    if item["severity"] in ["High", "Critical"]:

        st.error(
            f"""
            Customer: {item['customer']}

            Event: {item['event']}

            Severity: {item['severity']}
            """
        )

st.divider()

st.subheader("AI Executive Insights")

insight = load_latest_insight()

st.success(insight)

st.subheader("Autonomous AI Actions")
for item in reversed(memory[-10:]):

    st.success(
        f"""
        Agent: {item['agent']}

        Action:
        {item['event']}
        """
    )
