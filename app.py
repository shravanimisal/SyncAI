from flask import Flask, jsonify, request
import os

from agents.intent_agent import detect_intent
from agents.task_agent import extract_task
from agents.reply_agent import generate_reply
from agents.filter_agent import should_reply
from agents.scheduler_agent import suggest_meeting_time

from services.gmail_service import (
    get_latest_email,
    send_email_reply,
    mark_email_processed,
    mark_as_read,
    fetch_emails,
    send_email
)

from utils.memory_manager import add_to_memory, get_context
from utils.analytics_manager import increment, get_analytics

app = Flask(__name__)

# 📁 Upload folder for attachments
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# 🔹 Home Route
@app.route("/")
def home():
    return "🚀 AI Email Agent (Live on Render)"


# 🔥 AUTO EMAIL SYSTEM
@app.route("/auto-email")
def auto_email():

    email_data = get_latest_email()

    if not email_data:
        return {"message": "No new emails"}

    if "error" in email_data:
        return email_data

    increment("total_emails")

    email_id = email_data["id"]
    email_text = email_data["body"]
    sender = email_data["sender"]

    if not should_reply(email_text):
        increment("skipped")
        mark_email_processed(email_id)
        mark_as_read(email_id)
        return {"message": "Skipped (not important)"}

    context = get_context(sender)

    intent = detect_intent(email_text)
    task = extract_task(email_text)
    reply = generate_reply(email_text, intent, context)

    meeting = suggest_meeting_time(task)
    if meeting:
        reply += "\n\n" + meeting
        increment("meetings")

    status = send_email_reply(sender, "Re: AI Response", reply)

    increment("replies_sent")

    add_to_memory(sender, email_text, reply)

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


# 📧 FETCH EMAILS (Dashboard)
@app.route("/emails")
def get_emails():
    try:
        emails = fetch_emails()
        return jsonify(emails)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🤖 GENERATE AI REPLY
@app.route("/generate-reply", methods=["POST"])
def generate_reply_api():
    try:
        data = request.json
        email_text = data.get("email")

        if not email_text:
            return jsonify({"error": "Email content required"}), 400

        intent = detect_intent(email_text)
        reply = generate_reply(email_text, intent, "")

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🚀 BULK EMAIL (JSON VERSION)
@app.route("/send-bulk", methods=["POST"])
def send_bulk():
    try:
        data = request.json

        emails = data.get("emails", [])
        subject = data.get("subject", "")
        body = data.get("body", "")
        attachment = data.get("attachment")  # optional file path

        if not emails:
            return jsonify({"error": "Email list required"}), 400

        results = []

        for email in emails:
            try:
                send_email(email, subject, body, attachment)
                results.append({"email": email, "status": "sent"})
            except Exception as e:
                results.append({"email": email, "status": str(e)})

        return jsonify({
            "message": "Bulk email completed",
            "results": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📎 BULK EMAIL WITH FILE UPLOAD (IMPORTANT 🔥)
@app.route("/send-bulk-upload", methods=["POST"])
def send_bulk_with_upload():
    try:
        emails = request.form.get("emails")
        subject = request.form.get("subject")
        body = request.form.get("body")
        file = request.files.get("file")

        if not emails:
            return jsonify({"error": "Emails required"}), 400

        email_list = [e.strip() for e in emails.split(",")]

        file_path = None
        if file:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)

        results = []

        for email in email_list:
            try:
                send_email(email, subject, body, file_path)
                results.append({"email": email, "status": "sent"})
            except Exception as e:
                results.append({"email": email, "status": str(e)})

        return jsonify({
            "message": "Bulk email with attachment completed",
            "results": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔥 RUN (Render Compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)