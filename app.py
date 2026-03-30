from flask import Flask, request, jsonify
import os

from services.gmail_service import send_bulk_emails
from agents.assistant_agent import generate_ai_email
from utils.file_handler import extract_emails_from_file

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return "🚀 AI Email Agent Live"


# 🤖 AI EMAIL GENERATOR
@app.route("/generate-email", methods=["POST"])
def generate_email():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return {"error": "Prompt required"}, 400

    email = generate_ai_email(prompt)
    return {"generated_email": email}


# 📧 BULK EMAIL (MANUAL)
@app.route("/send-bulk", methods=["POST"])
def send_bulk():
    data = request.json

    emails = data.get("emails")
    subject = data.get("subject")
    body = data.get("body")

    if not emails:
        return {"error": "Emails required"}, 400

    results = send_bulk_emails(emails, subject, body)

    return {
        "message": "Bulk email sent",
        "results": results
    }


# 📂 BULK EMAIL VIA FILE
@app.route("/send-bulk-upload", methods=["POST"])
def send_bulk_upload():
    try:
        file = request.files.get("file")
        subject = request.form.get("subject")
        body = request.form.get("body")

        if not file:
            return {"error": "File required"}, 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        emails = extract_emails_from_file(file_path)

        if not emails:
            return {"error": "No emails found in file"}, 400

        results = send_bulk_emails(emails, subject, body)

        return {
            "message": "Emails sent from file",
            "results": results
        }

    except Exception as e:
        return {"error": str(e)}, 500


# 🤖 AI ASSISTANT CHAT
@app.route("/ai-assistant", methods=["POST"])
def ai_assistant():
    data = request.json
    query = data.get("query")

    if not query:
        return {"error": "Query required"}, 400

    response = generate_ai_email(query)
    return {"response": response}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)