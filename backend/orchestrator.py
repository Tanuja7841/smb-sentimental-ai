from backend.agents.churn_agent import analyze_customer
from backend.tools.sentiment_alert_tool import generate_sentiment_alert
from backend.services.memory_service import add_memory
from backend.agents.root_cause_agent import (
    analyze_root_cause
)
from backend.agents.recovery_agent import (
    generate_recovery_strategy
)

from backend.agents.executive_agent import (
    generate_executive_brief
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

    sentiment = sentiment_result.get("sentiment", "")

    urgency = sentiment_result.get("urgency", "")

    # STEP 1 — Check escalation need
    negative_sentiments = [
    "Negative",
    "Extremely Negative",
    "Very Negative"
    ]

    high_urgencies = [
        "High",
        "Immediate",
        "Critical"
    ]

    sentiment = sentiment.lower()
    urgency = urgency.lower()
    if sentiment in negative_sentiments or urgency in high_urgencies:

        print("High-risk sentiment detected.")

        # STEP 2 — Run churn analysis
        churn_result = analyze_customer(customer_data)

        print("\n=========== CHURN ANALYSIS ===========\n")
        print(churn_result)

        # ROOT CAUSE ANALYSIS
        root_cause = analyze_root_cause(
            customer_data,
            sentiment_result
        )

        print("\n=========== ROOT CAUSE ANALYSIS ===========\n")
        print(root_cause)

        # RECOVERY STRATEGY

        recovery_strategy = generate_recovery_strategy(

            customer_data,
            churn_result,
            root_cause

        )

        print("\n=========== RECOVERY STRATEGY ===========\n")
        print(recovery_strategy)

        # EXECUTIVE BRIEF

        executive_brief = generate_executive_brief(

            customer_data,
            sentiment_result,
            churn_result,
            root_cause,
            recovery_strategy

        )

        print("\n=========== EXECUTIVE BRIEF ===========\n")
        print(executive_brief)

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
        add_memory(
            agent="Orchestrator",
            customer=customer_data["name"],
            event="Full escalation workflow triggered",
            severity="Critical"
        )

        return {
            "workflow": "Escalation Triggered",
            "churn_analysis": churn_result,
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
        "workflow": "No escalation required"
    }