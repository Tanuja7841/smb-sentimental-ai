from backend.orchestrator import orchestrate_customer_issue
from backend.agents.sentiment_agent import analyze_message
from backend.mcp_client import MongoMCPClient

import json
import os
import streamlit as st


def run_demo(mcp=None):
    """
    Run demo pipeline using the logged-in business's data.
    Reads from the business-specific JSON file based on session state.
    Falls back to old customers.json if no session.
    """

    # Determine which business data to use
    biz_file = None
    if hasattr(st, "session_state") and st.session_state.get("business_file"):
        biz_file = st.session_state["business_file"]

    if biz_file and os.path.exists(f"backend/data/businesses/{biz_file}"):
        with open(f"backend/data/businesses/{biz_file}", "r") as f:
            biz_data = json.load(f)
        customers = biz_data["customers"]
        messages = biz_data["messages"]
    else:
        # Fallback for CLI usage
        with open("backend/data/customers.json", "r") as f:
            customers = json.load(f)
        with open("backend/data/whatsapp_messages.json", "r") as f:
            messages = json.load(f)

    # Build lookup by customer name
    customer_lookup = {c["name"]: c for c in customers}

    # Use provided MCP client or create a new one
    if mcp:
        _run_pipeline(customer_lookup, messages, mcp)
    else:
        with MongoMCPClient() as client:
            _run_pipeline(customer_lookup, messages, client)

    print("Demo completed.")


def _run_pipeline(customer_lookup, messages, mcp):
    """Execute the pipeline for all customer messages."""

    for item in messages:
        customer = customer_lookup.get(item.get("customer"))

        if not customer:
            continue

        print(f"\n  Processing: {item['customer']} ({item.get('severity', 'Unknown')})")

        sentiment = analyze_message(item)

        orchestrate_customer_issue(
            customer,
            sentiment,
            mcp
        )
