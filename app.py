from flask import Flask, request, jsonify, Response
import os

from services.gmail_service import send_email
from agents.assistant_agent import (
    generate_ai_email,
    improve_email,
    personalize_email,
    chat_with_ai
)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return "🚀 AI Email Agent Live"


# =========================
# ✉️ AI EMAIL GENERATION (FIXED)
# =========================
@app.route("/ai/generate", methods=["POST"])
def generate_email():
    data = request.json

    prompt = data.get("prompt")
    tone = data.get("tone", "professional")
    length = data.get("length", "medium")
    language = data.get("language", "English")
    user_id = data.get("user_id", "default")

    if not prompt:
        return {"error": "Prompt required"}, 400

    email = generate_ai_email(prompt, tone, length, language, user_id)

    # 🔥 IMPORTANT FIX → RETURN CLEAN TEXT
    return Response(email, mimetype="text/plain")


# =========================
# 🤖 AI CHATBOT
# =========================
@app.route("/ai/chat", methods=["POST"])
def ai_chat():
    data = request.json
    message = data.get("message")

    if not message:
        return {"error": "Message required"}, 400

    reply = chat_with_ai(message)
    return {"reply": reply}


# =========================
# ✨ IMPROVE EMAIL
# =========================
@app.route("/ai/improve", methods=["POST"])
def improve():
    data = request.json
    email_text = data.get("email")

    if not email_text:
        return {"error": "Email text required"}, 400

    improved = improve_email(email_text)
    return {"improved_email": improved}


# =========================
# 👤 PERSONALIZE EMAIL
# =========================
@app.route("/ai/personalize", methods=["POST"])
def personalize():
    data = request.json
    email_text = data.get("email")
    name = data.get("name")

    if not email_text or not name:
        return {"error": "Email and name required"}, 400

    result = personalize_email(email_text, name)
    return {"personalized_email": result}


# =========================
# 📧 SEND EMAIL (WITH ATTACHMENT)
# =========================
@app.route("/send-email", methods=["POST"])
def send_single_email():
    to = request.form.get("to") or request.values.get("to")
    subject = request.form.get("subject") or request.values.get("subject")
    body = request.form.get("body") or request.values.get("body")

    if not to:
        return {"error": "Recipient email required"}, 400

    if not subject:
        subject = "No Subject"

    if not body:
        body = "Hello from AI agent"

    attachment_file = request.files.get("attachment")
    attachment_path = None

    if attachment_file:
        filename = attachment_file.filename.replace(" ", "_")
        attachment_path = os.path.join(UPLOAD_FOLDER, filename)
        attachment_file.save(attachment_path)

    result = send_email(to, subject, body, attachment_path)

    return jsonify({
        "message": "Email sent successfully",
        "result": str(result)
    })


# =========================
# 🚀 SERVER START
# =========================
if __name__ == "__main__":
    print("🚀 Server starting on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)