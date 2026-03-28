from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def should_reply(email_text):
    prompt = f"""
Decide if this email needs a reply.

Reply ONLY with YES or NO.

Ignore ads, spam, promotions.

Email:
{email_text}
"""
    try:
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return res.text.strip().upper() == "YES"
    except:
        return False