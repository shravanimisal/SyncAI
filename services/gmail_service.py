import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_gmail_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build('gmail', 'v1', credentials=creds)


# ✅ FINAL FIXED EMAIL FUNCTION
def send_email(to, subject, body, attachment_path=None):
    try:
        service = get_gmail_service()

        # 🔥 Create multipart message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        # ✅ ADD BODY FIRST (IMPORTANT)
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)

        # ✅ ADD ATTACHMENT
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(attachment_path)}"'
            )

            message.attach(part)

        # 🔥 Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # 🔥 Send
        service.users().messages().send(
            userId="me",
            body={'raw': raw_message}
        ).execute()

        return "✅ Sent"

    except Exception as e:
        return f"❌ Error: {str(e)}"