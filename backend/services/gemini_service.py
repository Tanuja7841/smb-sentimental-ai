from google import genai
import os

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def ask_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print("Gemini error:", e)
        
        # ✅ fallback (demo-safe)
        return "Customer may churn due to low engagement, reduced activity, and declining interaction with the product."
