import json

from backend.services.gemini_service import ask_gemini


def generate_recovery_strategy(customer, churn_analysis, root_cause, mcp, workflow_id=None, customer_id=None):
    """
    Recovery Agent — Creates customer recovery strategy.

    Uses MCP client to:
    - Retrieve assigned tasks
    - Get context from previous agents
    - Read inter-agent messages
    - Complete tasks when done

    Args:
        customer: Customer data dict
        churn_analysis: Churn agent result
        root_cause: Root cause agent result
        mcp: MongoMCPClient instance
        workflow_id: Current workflow ID
        customer_id: Customer identifier
    """

    # Get tasks assigned via MCP
    tasks = []
    if workflow_id:
        tasks = mcp.get_tasks_for_agent(workflow_id, "recovery_agent")
        if not isinstance(tasks, list):
            tasks = []

    # Get previous agent context via MCP
    context_text = ""
    if workflow_id and customer_id:
        context = mcp.get_customer_context(workflow_id, customer_id)
        if isinstance(context, list):
            context_text = "\n".join([
                f"Agent: {item.get('agent_name')}\nFinding: {item.get('finding')}"
                for item in context
            ])

    # Get inter-agent messages via MCP
    messages = mcp.get_agent_messages(workflow_id, "root_cause_agent") if workflow_id else []

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

    if result is None:
        parsed_result = {
            "immediate_recovery_plan": "Contact customer immediately.",
            "retention_strategy": "Assign dedicated account manager.",
            "executive_recommendation": "Monitor closely.",
            "revenue_protection_action": "Offer retention discount."
        }
    else:
        try:
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned.replace("```json", "").replace("```", "")
            parsed_result = json.loads(cleaned)
        except Exception:
            parsed_result = {
                "immediate_recovery_plan": "Unable to parse Gemini response.",
                "retention_strategy": "Manual follow-up required.",
                "executive_recommendation": "Review manually.",
                "revenue_protection_action": "Escalate to customer success."
            }

    # Complete all pending tasks for this agent in this workflow via MCP
    if workflow_id and tasks:
        mcp.complete_task(workflow_id, "recovery_agent")

    return parsed_result
