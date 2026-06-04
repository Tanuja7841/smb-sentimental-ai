from backend.services.memory_service import load_memory


def calculate_business_health(customers):

    total_customers = len(customers)

    high_risk = 0

    revenue_at_risk = 0

    for customer in customers:

        if (
            customer["sentiment"] == "negative"
            or customer["response_delay_days"] > 10
        ):

            high_risk += 1

            revenue_at_risk += customer["total_spent"]

    health_score = max(
        0,
        100 - (high_risk * 15)
    )

    memory = load_memory()

    escalations = len(memory)

    return {
        "total_customers": total_customers,
        "high_risk_customers": high_risk,
        "revenue_at_risk": revenue_at_risk,
        "business_health_score": health_score,
        "total_escalations": escalations
    }