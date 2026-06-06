from backend.orchestrator import (
    orchestrate_customer_issue
)

from backend.agents.sentiment_agent import (
    analyze_message
)

import random

def run_demo():

    import json

    with open("backend/data/customers.json", "r") as f:
        customers = json.load(f)

    complaints = [

        "Support never responds.",
        "Product quality is terrible.",
        "Pricing is too expensive.",
        "Shipment delayed again.",
        "Technical issue unresolved."
    ]

    for i in range(1):

        customer = random.choice(
            customers
        )

        message = {

            "customer": customer["name"],
            "message": random.choice(complaints)
        }

        sentiment = analyze_message(
            message
        )

        orchestrate_customer_issue(
            customer,
            sentiment
        )

    print(
        "Demo completed."
    )