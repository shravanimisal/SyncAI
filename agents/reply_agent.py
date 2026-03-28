from google import genai
from config import GEMINI_API_KEY
from utils.user_profile import USER_STYLE

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_reply(email_text, intent, context=[]):

    history = ""
    for item in context:
        history += f"""
Previous Email: {item['email']}
Previous Reply: {item['reply']}
"""

    prompt = f"""
You are an intelligent email assistant.

Tone: {USER_STYLE['tone']}

Conversation history:
{history}

Current email:
{email_text}

Intent:
{intent}

Write a professional reply and include this signature:
{USER_STYLE['signature']}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text