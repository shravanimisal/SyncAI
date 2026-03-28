import os
import base64
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# 🔑 AUTH SERVICE
def get_gmail_service():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # ⚠️ LOCAL ONLY (will fix for Render later)
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


# 📌 EMAIL TRACKING
def is_email_processed(email_id):
    if not os.path.exists("processed_emails.txt"):
        return False
    with open("processed_emails.txt", "r") as f:
        return email_id in f.read().splitlines()


def mark_email_processed(email_id):
    with open("processed_emails.txt", "a") as f:
        f.write(email_id + "\n")


def mark_as_read(email_id):
    service = get_gmail_service()
    service.users().messages().modify(
        userId='me',
        id=email_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()


# 📩 HELPER
def extract_sender(headers):
    for header in headers:
        if header['name'] == 'From':
            sender = header['value']
            match = re.search(r'<(.+?)>', sender)
            return match.group(1) if match else sender
    return ""


# 📥 FETCH SINGLE EMAIL (AUTO SYSTEM)
def get_latest_email():
    try:
        service = get_gmail_service()

        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            q="is:unread",
            maxResults=1
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            return None

        email_id = messages[0]['id']

        if is_email_processed(email_id):
            return None

        msg = service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()

        payload = msg.get('payload', {})
        headers = payload.get('headers', [])

        sender = extract_sender(headers)

        parts = payload.get('parts', [])
        data = ""

        if parts:
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data')
                    break
        else:
            data = payload.get('body', {}).get('data')

        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            body = msg.get('snippet', '')

        return {"id": email_id, "body": body, "sender": sender}

    except Exception as e:
        return {"error": str(e)}


# 📥 FETCH MULTIPLE EMAILS (FOR DASHBOARD)
def fetch_emails(max_results=10):
    try:
        service = get_gmail_service()

        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])
        email_list = []

        for msg_data in messages:
            msg = service.users().messages().get(
                userId='me',
                id=msg_data['id'],
                format='metadata',
                metadataHeaders=['Subject', 'From']
            ).execute()

            headers = msg.get('payload', {}).get('headers', [])

            subject = ""
            sender = ""

            for h in headers:
                if h['name'] == 'Subject':
                    subject = h['value']
                if h['name'] == 'From':
                    sender = h['value']

            email_list.append({
                "id": msg_data['id'],
                "sender": sender,
                "subject": subject,
                "snippet": msg.get('snippet', '')
            })

        return email_list

    except Exception as e:
        return [{"error": str(e)}]


# 📤 SEND REPLY
def send_email_reply(to_email, subject, message_text):
    try:
        service = get_gmail_service()

        message = MIMEText(message_text)
        message['to'] = to_email
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        service.users().messages().send(
            userId="me",
            body={'raw': raw}
        ).execute()

        return "✅ Email sent"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# 🚀 SEND EMAIL (WITH ATTACHMENT SUPPORT)
def send_email(to, subject, body, attachment=None):
    try:
        service = get_gmail_service()

        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        # 📎 Attachment
        if attachment and os.path.exists(attachment):
            with open(attachment, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(attachment)}"'
            )
            message.attach(part)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        service.users().messages().send(
            userId="me",
            body={'raw': raw}
        ).execute()

        return "✅ Sent"

    except Exception as e:
        return f"❌ Error: {str(e)}"