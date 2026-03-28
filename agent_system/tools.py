from langchain.tools import tool
from agents.intent_agent import detect_intent
from agents.task_agent import extract_task
from agents.reply_agent import generate_reply
from rag.retriever import retrieve_context


@tool
def intent_tool(email: str):
    """Detect intent of email"""
    return str(detect_intent(email))


@tool
def task_tool(email: str):
    """Extract task details from email"""
    return str(extract_task(email))


@tool
def rag_tool(email: str):
    """Retrieve company knowledge"""
    context = retrieve_context(email)
    return str(context)


@tool
def reply_tool(email: str):
    """Generate professional reply"""
    intent = detect_intent(email)
    return generate_reply(email, intent)