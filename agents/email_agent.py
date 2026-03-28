from agents.intent_agent import detect_intent
from agents.task_agent import extract_task
from agents.reply_agent import generate_reply


def process_email_pipeline(email_text):

    # Step 1: detect intent
    intent = detect_intent(email_text)

    # Step 2: extract task
    task = extract_task(email_text)

    # Step 3: generate reply
    reply = generate_reply(email_text, intent)

    return {
        "intent": intent,
        "task": task,
        "reply": reply
    }