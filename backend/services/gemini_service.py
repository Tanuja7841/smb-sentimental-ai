from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent / ".env"

load_dotenv(dotenv_path=env_path)

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask_gemini(prompt):

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        return f"Gemini Error: {str(e)}"