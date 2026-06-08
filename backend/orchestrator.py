"""
Orchestrator — Multi-Agent Workflow Engine

Receives the MCP client from main.py and passes it to all agents.
Every MongoDB operation flows through the MCP protocol.
"""

import uuid
import json

from backend.agents.churn_agent import analyze_customer
from backend.agents.supervisor_agent import decide_agents
from backend.agents.root_cause_agent import analyze_root_cause
from backend.agents.recovery_agent import generate_recovery_strategy
from backend.agents.executive_agent import executive_agent

from backend.tools.sentiment_alert_tool import generate_sentiment_alert
from backend.tools.email_tool import send_recovery_email
from backend.tools.ticket_tool import create_escalation_ticket
from backend.tools.crm_tool import create_followup_task
from backend.tools.notification_tool import notify_executive


def orchestrate_customer_issue(customer_data, sentiment_result, mcp):
    """
    Full multi-agent orchestration pipeline.

    All MongoDB operations go through the MCP client (mcp).
    The mcp client is passed to each agent for memory persistence.

    Args:
        customer_data: Customer profile dict
        sentiment_result: Sentiment analysis from Gemini
        mcp: MongoMCPClient instance (persistent session)
    """

    workflow_id = f"wf_{uuid.uuid4()}"

    print(f"\n[MCP] Workflow Created: {workflow_id}")

    # Save workflow via MCP
    mcp.save_workflow(
        workflow_id=workflow_id,
        customer_id=customer_data["customer_id"]
    )

    # Save sentiment finding via MCP
    mcp.save_agent_memory(
        workflow_id=workflow_id,
        customer_id=customer_data["customer_id"],
        agent_name="sentiment_agent",
        finding=sentiment_result
    )

    # SUPERVISOR: Decide which agents to run
    agent_plan = decide_agents(customer_data, sentiment_result)
    selected_agents = agent_plan.get("agents", [])

    print(f"[MCP] Supervisor Selected: {selected_agents}")

    # Save supervisor decision via MCP
    mcp.save_supervisor_decision(
        workflow_id=workflow_id,
        customer_id=customer_data["customer_id"],
        selected_agents=selected_agents
    )

    churn_result = {}
    root_cause = {}
    recovery_strategy = {}
    executive_brief = {}

    sentiment = str(sentiment_result.get("sentiment", "")).lower()
    urgency = str(sentiment_result.get("urgency", "")).lower()

    negative_sentiments = ["negative", "extremely negative", "very negative"]
    high_urgencies = ["high", "immediate", "critical"]

    if sentiment in negative_sentiments or urgency in high_urgencies:

        # ─── CHURN AGENT ───
        if "churn_agent" in selected_agents:

            churn_result = analyze_customer(
                customer_data, mcp,
                workflow_id, customer_data["customer_id"]
            )

            mcp.upsert_customer_profile(
                customer_id=customer_data["customer_id"],
                customer_name=customer_data["name"],
                churn_score=churn_result.get("churn_score", 0),
                risk_level=churn_result.get("risk_level", "")
            )

            mcp.save_agent_memory(
                workflow_id=workflow_id,
                customer_id=customer_data["customer_id"],
                agent_name="churn_agent",
                finding=churn_result
            )

            print(f"[MCP] Churn Agent → Score: {churn_result.get('churn_score')}, Risk: {churn_result.get('risk_level')}")

        # ─── ROOT CAUSE AGENT ───
        if "root_cause_agent" in selected_agents:

            root_cause = analyze_root_cause(
                customer_data, sentiment_result, mcp,
                workflow_id, customer_data["customer_id"]
            )

            # Inter-agent message via MCP
            mcp.send_agent_message(
                workflow_id=workflow_id,
                from_agent="root_cause_agent",
                to_agent="recovery_agent",
                message=json.dumps(root_cause, indent=2)
            )

            mcp.save_agent_memory(
                workflow_id=workflow_id,
                customer_id=customer_data["customer_id"],
                agent_name="root_cause_agent",
                finding=root_cause
            )

            print(f"[MCP] Root Cause Agent → {root_cause.get('root_cause_category', 'Unknown')}")

        # Create recovery task via MCP
        mcp.create_task(
            workflow_id=workflow_id,
            assigned_agent="recovery_agent",
            task_type="customer_recovery",
            task_details=root_cause
        )

        # ─── RECOVERY AGENT ───
        if "recovery_agent" in selected_agents:

            recovery_strategy = generate_recovery_strategy(
                customer_data, churn_result, root_cause, mcp,
                workflow_id, customer_data["customer_id"]
            )

            mcp.save_agent_memory(
                workflow_id=workflow_id,
                customer_id=customer_data["customer_id"],
                agent_name="recovery_agent",
                finding=recovery_strategy
            )

            # Inter-agent message via MCP
            mcp.send_agent_message(
                workflow_id=workflow_id,
                from_agent="recovery_agent",
                to_agent="executive_agent",
                message=json.dumps(recovery_strategy, indent=2)
            )

            print(f"[MCP] Recovery Agent → Plan generated")

        # ─── EXECUTIVE AGENT ───
        if "executive_agent" in selected_agents:

            executive_brief = executive_agent(
                customer_data, sentiment_result,
                churn_result, root_cause, recovery_strategy
            )

            mcp.save_agent_memory(
                workflow_id=workflow_id,
                customer_id=customer_data["customer_id"],
                agent_name="executive_agent",
                finding=executive_brief
            )

            print(f"[MCP] Executive Agent → Priority: {executive_brief.get('priority', 'N/A')}")

        # ─── AUTONOMOUS ACTIONS ───
        email_result = send_recovery_email(customer_data, recovery_strategy) if recovery_strategy else None

        ticket_result = create_escalation_ticket(
            customer_data,
            root_cause.get("root_cause_category", "Negative sentiment")
        ) if root_cause else None

        crm_result = create_followup_task(customer_data)

        executive_alert = notify_executive(
            customer_data, churn_result.get("risk_level", "Unknown")
        ) if executive_brief else None

        # Save autonomous actions via MCP
        mcp.save_agent_memory(
            workflow_id=workflow_id,
            customer_id=customer_data["customer_id"],
            agent_name="autonomous_actions",
            finding={
                "email": email_result,
                "ticket": ticket_result,
                "crm": crm_result,
                "executive_alert": executive_alert
            }
        )

        # Complete workflow via MCP
        mcp.complete_workflow(workflow_id)

        print(f"[MCP] Workflow {workflow_id} COMPLETED ✓")

        return {
            "workflow_id": workflow_id,
            "status": "escalation_triggered",
            "agents_executed": selected_agents,
            "churn_score": churn_result.get("churn_score"),
            "risk_level": churn_result.get("risk_level"),
            "root_cause": root_cause.get("root_cause_category"),
            "recovery_plan": recovery_strategy.get("immediate_recovery_plan") if isinstance(recovery_strategy, dict) else None,
            "executive_priority": executive_brief.get("priority") if isinstance(executive_brief, dict) else None
        }

    # Low-risk: no escalation needed
    mcp.complete_workflow(workflow_id)

    return {
        "workflow_id": workflow_id,
        "status": "no_escalation",
        "agents_executed": selected_agents
    }
