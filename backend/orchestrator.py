import uuid
from backend.agents.churn_agent import analyze_customer
from backend.tools.sentiment_alert_tool import generate_sentiment_alert
from backend import agents as agents
from backend.services.mongodb_memory_service import (
    MongoDBMemoryService
)
import json

memory = MongoDBMemoryService()

from backend.agents.supervisor_agent import (
    decide_agents
)

from backend.agents.root_cause_agent import (
    analyze_root_cause
)
from backend.agents.recovery_agent import (
    generate_recovery_strategy
)

from backend.agents.executive_agent import (
    executive_agent
)

from backend.tools.email_tool import (
    send_recovery_email
)

from backend.tools.ticket_tool import (
    create_escalation_ticket
)

from backend.tools.crm_tool import (
    create_followup_task
)

from backend.tools.notification_tool import (
    notify_executive
)

def orchestrate_customer_issue(customer_data, sentiment_result):

    print("\n=========== ORCHESTRATION STARTED ===========\n")
    workflow_id = f"wf_{uuid.uuid4()}"

    print(f"Workflow Created: {workflow_id}")

    memory.save_workflow(
        workflow_id=workflow_id,
        customer_id=customer_data["customer_id"]
    )
    memory.save_agent_memory(
        workflow_id=workflow_id,
        customer_id=customer_data["customer_id"],
        agent_name="sentiment_agent",
        finding=sentiment_result
    )

    agent_plan = decide_agents(
    customer_data,
    sentiment_result
    )

    selected_agents = agent_plan.get(
        "agents",
        []
    )

    print(
        f"Supervisor Selected: {selected_agents}"
    )

    memory.save_supervisor_decision(
        workflow_id=workflow_id,
        customer_id=customer_data["customer_id"],
        selected_agents=selected_agents
    )

    print("="*50)
    print("Selected Agents")
    print(selected_agents)
    print("="*50)

    churn_result = {}
    root_cause = {}
    recovery_strategy = {}
    executive_brief = {}

    sentiment = sentiment_result.get("sentiment", "")

    urgency = sentiment_result.get("urgency", "")

    # STEP 1 — Check escalation need
    negative_sentiments = [
    "negative",
    "extremely negative",
    "very negative"
    ]

    high_urgencies = [
        "high",
        "immediate",
        "critical"
    ]

    sentiment = sentiment.lower()
    urgency = urgency.lower()
    if sentiment in negative_sentiments or urgency in high_urgencies:

        print("High-risk sentiment detected.")

        # STEP 2 — Run churn analysis
        if "churn_agent" in selected_agents:

            churn_result = analyze_customer(
                customer_data,
                workflow_id,
                customer_data["customer_id"]
            )

            memory.upsert_customer_profile(

                customer_id=customer_data["customer_id"],

                customer_name=customer_data["name"],

                churn_score=churn_result["churn_score"],

                risk_level=churn_result["risk_level"]

            )

            memory.save_agent_memory(
                workflow_id=workflow_id,
                customer_id=customer_data["customer_id"],
                agent_name="churn_agent",
                finding=churn_result
            )

        print("\n=========== CHURN ANALYSIS ===========\n")
        print(churn_result)

        print("="*50)
        print("Churn Agent Finished")
        print("="*50)

        # ROOT CAUSE ANALYSIS
        if "root_cause_agent" in selected_agents:

            root_cause = analyze_root_cause(
                customer_data,
                sentiment_result,
                workflow_id,
                customer_data["customer_id"]
            )

            memory.send_agent_message(
                workflow_id=workflow_id,
                from_agent="root_cause_agent",
                to_agent="recovery_agent",
                message=json.dumps(root_cause, indent=2)
            )

            memory.save_agent_memory(
                workflow_id=workflow_id,
                customer_id=customer_data["customer_id"],
                agent_name="root_cause_agent",
                finding=root_cause
            )

        print("\n=========== ROOT CAUSE ANALYSIS ===========\n")
        print(root_cause)

        print("="*50)
        print("Root Cause Finished")
        print("="*50)

        memory.create_task(
            workflow_id=workflow_id,
            assigned_agent="recovery_agent",
            task_type="customer_recovery",
            task_details=root_cause
        )

        print("Recovery task created.")

        # RECOVERY STRATEGY

        if "recovery_agent" in selected_agents:

            recovery_strategy = generate_recovery_strategy(
                customer_data,
                churn_result,
                root_cause,
                workflow_id,
                customer_data["customer_id"]
            )

            memory.save_agent_memory(
                workflow_id=workflow_id,
                customer_id=customer_data["customer_id"],
                agent_name="recovery_agent",
                finding=recovery_strategy
            )

            tasks = memory.get_tasks_for_agent(
                workflow_id,
                "recovery_agent"
            )

            for task in tasks:

                memory.complete_task(
                    task["_id"]
                )

            memory.send_agent_message(
                workflow_id=workflow_id,
                from_agent="recovery_agent",
                to_agent="executive_agent",
                message=json.dumps(recovery_strategy, indent=2)
            )
                        

        print("\n=========== RECOVERY STRATEGY ===========\n")
        print(recovery_strategy)

        print("="*50)
        print("Recovery Finished")
        print("="*50)

        # EXECUTIVE BRIEF

        if "executive_agent" in selected_agents:

            executive_brief = executive_agent(
                customer_data,
                sentiment_result,
                churn_result,
                root_cause,
                recovery_strategy
            )

            memory.save_agent_memory(
                workflow_id=workflow_id,
                customer_id=customer_data["customer_id"],
                agent_name="executive_agent",
                finding=executive_brief
            )

            print("\n=========== EXECUTIVE BRIEF ===========\n")
            print(executive_brief)

            print("="*50)
            print("Executive Finished")
            print("="*50)

        else:

            executive_brief = None

        # AUTONOMOUS ACTIONS

        email_result = None
        ticket_result = None
        crm_result = None
        executive_alert = None

        if recovery_strategy:

            email_result = send_recovery_email(
                customer_data,
                recovery_strategy
            )

        if root_cause:

            ticket_result = create_escalation_ticket(
                customer_data,
                root_cause.get(
                    "root_cause_category",
                    "Negative sentiment escalation"
                )
            )

        crm_result = create_followup_task(
            customer_data
        )

        memory.save_agent_memory(
            workflow_id=workflow_id,
            customer_id=customer_data["customer_id"],
            agent_name="autonomous_actions",
            finding={
                "email": email_result,
                "ticket": ticket_result,
                "crm": crm_result
            }
        )

        risk_level = churn_result.get(
            "risk_level",
            "Unknown"
        )

        if executive_brief:

            executive_alert = notify_executive(
                customer_data,
                risk_level
            )

        # STEP 3 — Generate operational alert
        alert = generate_sentiment_alert(
            customer_data["name"],
            "High"
        )

        print("\n=========== ALERT ===========\n")
        print(alert)

        memory.complete_workflow(
            workflow_id
        )

        # STEP 4 — Store orchestration memory
        # add_memory(
        #     agent="Orchestrator",
        #     customer=customer_data["name"],
        #     event="Full escalation workflow triggered",
        #     severity="Critical"
        # )


        return {
            "workflow": "Escalation Triggered",
            "workflow_id": workflow_id,
            "root_cause": root_cause,
            "recovery_strategy": recovery_strategy,
            "executive_brief": executive_brief,
            "email_result": email_result,
            "ticket_result": ticket_result,
            "crm_result": crm_result,
            "executive_alert": executive_alert,
            "alert": alert
        }

    return {
        "workflow": "No escalation required",
        "workflow_id": workflow_id
    }