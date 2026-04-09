import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from langdetect import detect

from utils.memory_manager import (
    save_user_preferences,
    get_user_preferences,
    save_email_history
)

# =========================
# ✅ LOAD ENV
# =========================
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# =========================
# 🔹 OpenRouter Setup
# =========================
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "meta-llama/llama-3-8b-instruct"


# =========================
# 🔹 AI RESPONSE FUNCTION
# =========================
def get_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3
        )

        if response and response.choices:
            return response.choices[0].message.content
        else:
            return "❌ AI Error: No response"

    except Exception as e:
        return f"❌ AI Error: {str(e)}"


# =========================
# 🌍 LANGUAGE HELPER
# =========================
def get_language_instruction(lang_code):
    if lang_code == "hi":
        return "Write ONLY in Hindi using Devanagari script."
    elif lang_code == "mr":
        return "Write ONLY in Marathi using Devanagari script."
    else:
        return "Write ONLY in English."


# =========================
# 🧹 CLEAN FORMAT FUNCTION
# =========================
def clean_email_format(text):
    return text.replace("\\n", "\n").strip()


# =========================
# 🚀 EMAIL GENERATION
# =========================
def generate_ai_email(prompt, tone="professional", length="medium", language="English", user_id="default"):
    try:
        prefs = get_user_preferences(user_id)
        tone = prefs.get("tone", tone)
        language = prefs.get("language", language)

        # Language detect
        try:
            detected_lang = detect(prompt)
        except:
            detected_lang = "en"

        lang_instruction = get_language_instruction(detected_lang)

        # 🔥 PERFECT COPY-PASTE PROMPT
        system_prompt = f"""
You are an AI email writer.

STRICT RULES:
- {lang_instruction}
- Do NOT add explanation
- Do NOT add extra text
- Output must be clean and copy-paste ready

PLACEHOLDER RULES:
- Use only:
  [Manager Name], [Your Name], [Start Date], [End Date]

FORMAT STRICTLY LIKE THIS:

Subject: <subject line>

Dear [Manager Name],

<email body>

Sincerely,
[Your Name]
"""

        user_prompt = f"Write a leave email: {prompt}"

        raw_response = get_ai_response([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        clean_response = clean_email_format(raw_response)

        # Save memory
        save_user_preferences(user_id, tone, language)
        save_email_history(user_id, clean_response)

        return clean_response

    except Exception as e:
        return f"❌ AI Error: {str(e)}"


# =========================
# 🤖 CHATBOT
# =========================
def chat_with_ai(message):
    try:
        detected_lang = detect(message)
    except:
        detected_lang = "en"

    lang_instruction = get_language_instruction(detected_lang)

    return get_ai_response([
        {"role": "system", "content": f"You are an AI assistant. {lang_instruction}"},
        {"role": "user", "content": message}
    ])


# =========================
# ✨ IMPROVE EMAIL
# =========================
def improve_email(email_text):
    return get_ai_response([
        {"role": "system", "content": "Improve the email professionally."},
        {"role": "user", "content": email_text}
    ])


# =========================
# 👤 PERSONALIZE EMAIL
# =========================
def personalize_email(email_text, name):
    return get_ai_response([
        {"role": "system", "content": f"Personalize this email for {name}."},
        {"role": "user", "content": email_text}
    ])


# =========================
# 🌍 TRANSLATE EMAIL
# =========================
def translate_email(email_text, language):
    return get_ai_response([
        {"role": "system", "content": f"Translate into {language}."},
        {"role": "user", "content": email_text}
    ])