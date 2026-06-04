import uuid
from agents.churn_agent import analyze_customer
from tools.sentiment_alert_tool import generate_sentiment_alert

from services.mongodb_memory_service import (
    MongoDBMemoryService
)

memory = MongoDBMemoryService()

from agents.root_cause_agent import (
    analyze_root_cause
)
from agents.recovery_agent import (
    generate_recovery_strategy
)

from agents.executive_agent import (
    generate_executive_brief
)

from tools.email_tool import (
    send_recovery_email
)

from tools.ticket_tool import (
    create_escalation_ticket
)

from tools.crm_tool import (
    create_followup_task
)

from tools.notification_tool import (
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
        churn_result = analyze_customer(
            customer_data,
            workflow_id,
            customer_data["customer_id"]
        )

        print("\n=========== CHURN ANALYSIS ===========\n")
        print(churn_result)

        memory.save_agent_memory(
            workflow_id=workflow_id,
            customer_id=customer_data["customer_id"],
            agent_name="churn_agent",
            finding=churn_result
        )

        # ROOT CAUSE ANALYSIS
        root_cause = analyze_root_cause(
            customer_data,
            sentiment_result,
            workflow_id,
            customer_data["customer_id"]
        )

        print("\n=========== ROOT CAUSE ANALYSIS ===========\n")
        print(root_cause)

        memory.save_agent_memory(
            workflow_id=workflow_id,
            customer_id=customer_data["customer_id"],
            agent_name="root_cause_agent",
            finding=root_cause
        )

        # RECOVERY STRATEGY

        recovery_strategy = generate_recovery_strategy(
            customer_data,
            churn_result,
            root_cause,
            workflow_id,
            customer_data["customer_id"]

        )

        print("\n=========== RECOVERY STRATEGY ===========\n")
        print(recovery_strategy)
        memory.save_agent_memory(
            workflow_id=workflow_id,
            customer_id=customer_data["customer_id"],
            agent_name="recovery_agent",
            finding=recovery_strategy
        )

        # EXECUTIVE BRIEF

        executive_brief = generate_executive_brief(

            customer_data,
            sentiment_result,
            churn_result,
            root_cause,
            recovery_strategy,
            workflow_id,
            customer_data["customer_id"]

        )

        print("\n=========== EXECUTIVE BRIEF ===========\n")
        print(executive_brief)
        memory.save_agent_memory(
            workflow_id=workflow_id,
            customer_id=customer_data["customer_id"],
            agent_name="executive_agent",
            finding=executive_brief
        )

        # AUTONOMOUS ACTIONS

        email_result = send_recovery_email(
            customer_data,
            recovery_strategy
        )

        ticket_result = create_escalation_ticket(
            customer_data,
            "Negative sentiment escalation"
        )

        crm_result = create_followup_task(
            customer_data
        )

        executive_alert = notify_executive(
            customer_data,
            churn_result["risk_level"]
        )

        # STEP 3 — Generate operational alert
        alert = generate_sentiment_alert(
            customer_data["name"],
            "High"
        )

        print("\n=========== ALERT ===========\n")
        print(alert)

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