from google import genai
from config import GEMINI_API_KEY
import json
import re

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def detect_intent(email_text):

    prompt = f"""
You are an AI email analysis agent.

Analyze the email and return ONLY valid JSON.

Required JSON format:
{{
  "intent": "",
  "priority": "",
  "action": ""
}}

Rules:
- intent must be one of:
  Meeting Request
  Complaint
  Support Request
  Information Request
  General Inquiry

- priority must be one of:
  Low
  Medium
  High

- action should be a short sentence describing what should be done.

Email:
{email_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Extract JSON from response safely
        json_match = re.search(r"\{[\s\S]*\}", text)

        if json_match:
            parsed_json = json.loads(json_match.group())

            # normalize priority
            priority = parsed_json.get("priority", "").lower()

            if priority not in ["low", "medium", "high"]:
                parsed_json["priority"] = "Medium"

            return parsed_json

        return {
            "intent": "Unknown",
            "priority": "Medium",
            "action": "Manual review required"
        }

    except Exception as e:

        return {
            "intent": "Error",
            "priority": "Medium",
            "action": str(e)
        }