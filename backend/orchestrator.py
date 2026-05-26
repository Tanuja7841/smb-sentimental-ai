from agents.churn_agent import analyze_customer
from tools.sentiment_alert_tool import generate_sentiment_alert
from services.memory_service import add_memory


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
            "alert": alert
        }

    return {
        "workflow": "No escalation required"
    }