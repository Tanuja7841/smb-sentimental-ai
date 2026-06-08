from backend.orchestrator import orchestrate_customer_issue
from backend.agents.sentiment_agent import analyze_message
from backend.mcp_client import MongoMCPClient

import random
import json


def run_demo(mcp=None):
    """
    Run demo pipeline. If mcp client is passed, uses it.
    Otherwise creates its own MCP session.
    """

    with open("backend/data/customers.json", "r") as f:
        customers = json.load(f)

    complaints = [
        "Support never responds.",
        "Product quality is terrible.",
        "Pricing is too expensive.",
        "Shipment delayed again.",
        "Technical issue unresolved."
    ]

    # Use provided MCP client or create a new one
    if mcp:
        _run_pipeline(customers, complaints, mcp)
    else:
        with MongoMCPClient() as client:
            _run_pipeline(customers, complaints, client)

    print("Demo completed.")


def _run_pipeline(customers, complaints, mcp):
    """Execute the demo pipeline with the given MCP client."""

    for i in range(1):

        customer = random.choice(customers)

        message = {
            "customer": customer["name"],
            "message": random.choice(complaints)
        }

        sentiment = analyze_message(message)

        orchestrate_customer_issue(
            customer,
            sentiment,
            mcp
        )
