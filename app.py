from flask import Flask, jsonify

from agents.intent_agent import detect_intent
from agents.task_agent import extract_task
from agents.reply_agent import generate_reply
from agents.filter_agent import should_reply
from agents.scheduler_agent import suggest_meeting_time

from services.gmail_service import (
    get_latest_email,
    send_email_reply,
    mark_email_processed,
    mark_as_read
)

from utils.memory_manager import add_to_memory, get_context
from utils.analytics_manager import increment, get_analytics

app = Flask(__name__)


# 🔹 Home Route
@app.route("/")
def home():
    return "🚀 AI Email Agent (Final System + Analytics Running)"


# 🔥 AUTO EMAIL SYSTEM
@app.route("/auto-email")
def auto_email():

    email_data = get_latest_email()

    if not email_data:
        return {"message": "No new emails"}

    if "error" in email_data:
        return email_data

    # 📊 Track total emails
    increment("total_emails")

    email_id = email_data["id"]
    email_text = email_data["body"]
    sender = email_data["sender"]

    # 🔍 Smart Filter
    if not should_reply(email_text):
        increment("skipped")
        mark_email_processed(email_id)
        mark_as_read(email_id)

        return {"message": "Skipped (not important)"}

    # 🧠 Memory Context
    context = get_context(sender)

    # 🤖 AI Processing
    intent = detect_intent(email_text)
    task = extract_task(email_text)
    reply = generate_reply(email_text, intent, context)

    # 📅 Scheduler
    meeting = suggest_meeting_time(task)
    if meeting:
        reply += "\n\n" + meeting
        increment("meetings")

    # 📤 Send Email
    status = send_email_reply(sender, "Re: AI Response", reply)

    # 📊 Track reply
    increment("replies_sent")

    # 💾 Save memory
    add_to_memory(sender, email_text, reply)

    # 🔐 Phase 1 controls
    mark_email_processed(email_id)
    mark_as_read(email_id)

    return {
        "email": email_text,
        "reply": reply,
        "status": status
    }


# 📊 Analytics API
@app.route("/analytics")
def analytics():
    return jsonify(get_analytics())


if __name__ == "__main__":
    app.run(debug=True)