import json
import random
import time

from backend.agents.sentiment_agent import analyze_message

from backend.orchestrator import (
    orchestrate_customer_issue
)

from backend.services.business_health_service import (
    calculate_business_health
)

from backend.services.insight_service import (
    generate_executive_insight
)

from backend.services.live_metric_services import (
    update_metrics
)

from backend.services.correlation_service import (
    track_incident,
    detect_pattern
)

# LOAD DATA

with open("backend/data/customers.json", "r") as file:

    customers = json.load(file)


with open("backend/data/whatsapp_messages.json", "r") as file:

    messages = json.load(file)


customer_lookup = {
    customer["name"]: customer
    for customer in customers
}


print("\n=========== LIVE EVENT ENGINE STARTED ===========\n")


while True:

    # RANDOM MESSAGE

    item = random.choice(messages)

    print("\n====================================")
    print(f"NEW CUSTOMER EVENT: {item['customer']}")

    # AI SENTIMENT ANALYSIS

    sentiment_result = analyze_message(item)

    print("\nSENTIMENT RESULT:")
    print(sentiment_result)

    customer_data = customer_lookup.get(item["customer"])

    # ORCHESTRATION

    if customer_data:

        result = orchestrate_customer_issue(
            customer_data,
            sentiment_result
        )

        print("\nWORKFLOW RESULT:")
        print(result)
    
    update_metrics(
            item["severity"],
            customer_data["total_spent"]

        )

    print("\nWaiting for next event...\n")
    # GENERATE NEW EXECUTIVE INSIGHT

    metrics = calculate_business_health(customers)

    generate_executive_insight(metrics)

    track_incident(item["incident_type"])

    patterns = detect_pattern()

    print("\nTOP INCIDENT PATTERNS:")
    print(patterns)
    time.sleep(10)