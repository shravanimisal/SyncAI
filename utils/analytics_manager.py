import os
from dotenv import load_dotenv
from openai import OpenAI

from utils.memory_manager import (
    save_user_preferences,
    get_user_preferences,
    save_email_history
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "AI Email Agent"
    }
)

MODEL = "mistralai/mistral-7b-instruct"

# ✅ ALLOWED LANGUAGES ONLY
SUPPORTED_LANGUAGES = ["English", "Hindi", "Marathi"]


def get_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,   # 🔥 VERY IMPORTANT (low randomness)
            top_p=0.9
        )

        if response and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "❌ AI Error: No response from model"

    except Exception as e:
        return f"❌ AI Error: {str(e)}"


# 🚀 STRICT MULTILINGUAL EMAIL GENERATOR
def generate_ai_email(prompt, tone="professional", length="medium", language="English", user_id="default"):
    try:
        if language == "Hindi":
            lang_instruction = "ONLY Hindi language. Use Devanagari script."
        elif language == "Marathi":
            lang_instruction = "ONLY Marathi language. Use Devanagari script."
        else:
            lang_instruction = "ONLY English language."

        system_prompt = f"""
You are an email generator.

STRICT RULES:
- {lang_instruction}
- DO NOT use any other language
- DO NOT translate
- DO NOT explain anything
- NO placeholders like [Your Name]
- Output must be clean email

FORMAT:
Subject:
<subject>

<email>

<closing>
"""

        user_prompt = f"""
Write a {tone} and {length} email.

Topic:
{prompt}
"""

        response = get_ai_response([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        return response

    except Exception as e:
        return f"❌ AI Error: {str(e)}"