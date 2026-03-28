from google import genai
from config import GEMINI_API_KEY
import json
import re

client = genai.Client(api_key=GEMINI_API_KEY)

def extract_task(email_text):

    prompt = f"""
Extract task details from the email.

Return ONLY JSON.

Format:
{{
 "task":"",
 "date":"",
 "time":"",
 "topic":""
}}

Email:
{email_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text

        json_match = re.search(r"\{.*\}", text, re.DOTALL)

        if json_match:
            return json.loads(json_match.group())

        return {"error": "No JSON returned"}

    except Exception as e:
        return {"error": str(e)}