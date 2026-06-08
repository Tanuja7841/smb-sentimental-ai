"""
Gemini Service — Google Gemini 2.5 Flash with exponential backoff.

Handles 503 UNAVAILABLE (rate limiting) gracefully with retries.
"""

import time
from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MAX_RETRIES = 4
BASE_DELAY = 2  # seconds


def ask_gemini(prompt, retries=MAX_RETRIES):
    """
    Call Gemini with exponential backoff on 503/429 errors.

    Retry delays: 2s → 4s → 8s → 16s (then gives up)
    """

    for attempt in range(retries):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            return response.text

        except Exception as e:

            error_str = str(e)

            # Retry on rate limit / overload errors
            if "503" in error_str or "429" in error_str or "UNAVAILABLE" in error_str:

                delay = BASE_DELAY * (2 ** attempt)

                if attempt < retries - 1:
                    print(f"  [Gemini] 503/429 — retrying in {delay}s (attempt {attempt + 1}/{retries})")
                    time.sleep(delay)
                else:
                    print(f"  [Gemini] Failed after {retries} attempts: {error_str[:100]}")
                    return None

            else:
                # Non-retryable error
                print(f"  [Gemini] Error: {error_str[:100]}")
                return None

    return None
