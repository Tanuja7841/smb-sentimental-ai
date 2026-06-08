"""
SMB Sentinel AI — Multi-Agent Customer Churn Prevention System
Google Rapid Agent Hackathon

All MongoDB operations go through the official MongoDB MCP Server
via the Model Context Protocol (MCP).

Architecture:
    main.py → MongoMCPClient → [MCP Protocol / stdio] → mongodb-mcp-server → MongoDB Atlas

Agents:
    1. Sentiment Agent    → Analyzes customer messages (Gemini)
    2. Supervisor Agent   → Routes to downstream agents
    3. Churn Agent        → Predicts churn risk
    4. Root Cause Agent   → Identifies operational issues
    5. Recovery Agent     → Creates recovery strategies
    6. Executive Agent    → Generates executive briefs
"""

import json

from backend.mcp_client import MongoMCPClient
from backend.agents.sentiment_agent import analyze_message
from backend.orchestrator import orchestrate_customer_issue


def main():

    # Load customer and message data
    with open("backend/data/customers.json", "r") as file:
        customers = json.load(file)

    with open("backend/data/whatsapp_messages.json", "r") as file:
        messages = json.load(file)

    customer_lookup = {
        customer["name"]: customer
        for customer in customers
    }

    # Single MCP connection for the entire pipeline
    with MongoMCPClient() as mcp:

        print("\n" + "=" * 60)
        print("  SMB SENTINEL AI — MongoDB MCP Multi-Agent System")
        print("  All DB operations via Model Context Protocol (MCP)")
        print("=" * 60)

        for item in messages:

            print(f"\n{'='*60}")
            print(f"  CUSTOMER MESSAGE: {item['customer']}")
            print(f"{'='*60}")

            # STEP 1: AI Sentiment Analysis (Gemini)
            sentiment_result = analyze_message(item)

            print("\n--- SENTIMENT ANALYSIS (Gemini) ---")
            print(json.dumps(sentiment_result, indent=2))

            # STEP 2: Full orchestration pipeline via MCP
            customer_data = customer_lookup.get(item["customer"])

            if customer_data:

                result = orchestrate_customer_issue(
                    customer_data,
                    sentiment_result,
                    mcp
                )

                print("\n--- ORCHESTRATION RESULT ---")
                print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
