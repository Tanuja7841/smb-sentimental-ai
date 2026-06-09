from backend.services.memory_service import load_memory


def calculate_business_health(customers):

    total_customers = len(customers)
    high_risk = 0
    revenue_at_risk = 0

    for customer in customers:
        if (
            customer.get("sentiment") == "negative"
            or customer.get("response_delay_days", 0) > 10
        ):
            high_risk += 1
            revenue_at_risk += customer.get("total_spent", 0)

    # Health score: percentage of customers NOT at risk
    safe_pct = (total_customers - high_risk) / max(total_customers, 1)
    health_score = round(safe_pct * 100)

    memory = load_memory()
    escalations = len(memory)

    return {
        "total_customers": total_customers,
        "high_risk_customers": high_risk,
        "revenue_at_risk": revenue_at_risk,
        "mrr_at_risk": revenue_at_risk,
        "business_health_score": health_score,
        "total_escalations": escalations
    }
