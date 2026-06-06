import json

from backend.services.gemini_service import ask_gemini
from backend.services.mongodb_memory_service import (
    MongoDBMemoryService
)

memory = MongoDBMemoryService()


def generate_recovery_strategy(

    customer,
    churn_analysis,
    root_cause,
    workflow_id=None,
    customer_id=None

):

    tasks = []

    if workflow_id:

        tasks = memory.get_tasks_for_agent(
            workflow_id,
            "recovery_agent"
        )

    print("\n===== RECOVERY TASKS =====")
    print(tasks)

    context_text = ""

    if workflow_id and customer_id:

        context = memory.get_customer_context(
            workflow_id,
            customer_id
        )

        context_text = "\n".join(
            [
                f"Agent: {item['agent_name']}\nFinding: {item['finding']}"
                for item in context
            ]
        )

    messages = memory.get_agent_messages(
        workflow_id,
        "recovery_agent"
    )

    prompt = f"""
    You are an AI customer recovery strategist.

    Assigned Tasks:
    {tasks}

    Previous Agent Findings:
    {context_text}

    Customer:
    {customer}

    Churn Analysis:
    {churn_analysis}

    Root Cause:
    {root_cause}

    Agent Messages:
    {messages}

    Return ONLY valid JSON.

    {{
        "immediate_recovery_plan":"",
        "retention_strategy":"",
        "executive_recommendation":"",
        "revenue_protection_action":""
    }}

    Do not return markdown.
    """

    result = ask_gemini(prompt)

    # Gemini unavailable
    if result is None:

        parsed_result = {

            "immediate_recovery_plan":
                "Contact customer immediately.",

            "retention_strategy":
                "Assign dedicated account manager.",

            "executive_recommendation":
                "Monitor closely.",

            "revenue_protection_action":
                "Offer retention discount."

        }

    else:

        try:

            cleaned = result.strip()

            if cleaned.startswith("```json"):

                cleaned = cleaned.replace(
                    "```json",
                    ""
                ).replace(
                    "```",
                    ""
                )

            parsed_result = json.loads(cleaned)

        except Exception:

            parsed_result = {

                "immediate_recovery_plan":
                    "Unable to parse Gemini response.",

                "retention_strategy":
                    "Manual follow-up required.",

                "executive_recommendation":
                    "Review manually.",

                "revenue_protection_action":
                    "Escalate to customer success."

            }

    # Complete pending tasks
    for task in tasks:

        if "_id" in task:

            memory.complete_task(
                task["_id"]
            )

    print("=" * 50)
    print("Recovery Agent Finished")
    print("=" * 50)

    return parsed_result