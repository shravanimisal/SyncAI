from google import genai
from config import GEMINI_API_KEY

from agent_system.tools import intent_tool, task_tool, rag_tool, reply_tool

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def run_agent(email_text):

    try:
        # Step-by-step execution (modern approach)
        intent = intent_tool.run(email_text)
        task = task_tool.run(email_text)
        context = rag_tool.run(email_text)
        reply = reply_tool.run(email_text)

        return {
            "intent": intent,
            "task": task,
            "context": context,
            "reply": reply
        }

    except Exception as e:
        return {"error": str(e)}