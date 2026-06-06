from backend.services.gemini_service import ask_gemini
import json


def analyze_message(message_data):

    prompt = f"""
    You are an AI customer sentiment analyst.

    Analyze this message.

    Message:
    {message_data}

    Return ONLY valid JSON.

    JSON format:

    {{
        "sentiment": "",
        "urgency": "",
        "frustration_level": "",
        "business_risk": "",
        "recommended_action": ""
    }}

    Do not return markdown.
    Do not explain anything outside JSON.
    """

    result = ask_gemini(prompt)

    if result is None:

        return {
            "sentiment": "negative",
            "urgency": "high",
            "frustration_level": "high",
            "business_risk": "high",
            "recommended_action": "Escalate immediately"
        }

    try:

        cleaned = result.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "")
            cleaned = cleaned.replace("```", "")

        parsed_result = json.loads(cleaned)

        return parsed_result

    except Exception as e:

        return {
            "error": str(e),
            "raw_response": result
        }