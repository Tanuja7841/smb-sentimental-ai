from services.gemini_service import ask_gemini
from services.mongodb_memory_service import (
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

        context_text = "\n".join([
            f"Agent: {item['agent_name']}\nFinding: {item['finding']}"
            for item in context
        ])
    
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
    
    Generate:

    1. Immediate recovery plan
    2. Retention strategy
    3. Executive recommendation
    4. Revenue protection action

    Keep concise and strategic.

    """

    result = ask_gemini(prompt)

    for task in tasks:

        memory.complete_task(
            task["_id"]
        )

    return result