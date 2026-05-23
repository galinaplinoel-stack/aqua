"""Email tools - SMTP and IMAP."""

import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from rich.console import Console

console = Console()


def send_email(
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    to: str,
    subject: str,
    body: str,
    html: bool = False,
    cc: Optional[str] = None,
) -> str:
    """Send an email via SMTP."""
    try:
        msg = MIMEMultipart()
        msg["From"] = username
        msg["To"] = to
        msg["Subject"] = subject
        if cc:
            msg["Cc"] = cc

        content_type = "html" if html else "plain"
        msg.attach(MIMEText(body, content_type))

        recipients = [to]
        if cc:
            recipients.extend(cc.split(","))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, recipients, msg.as_string())

        return f"Email sent to {to}"

    except Exception as e:
        return f"Email error: {e}"


def read_emails(
    imap_host: str,
    username: str,
    password: str,
    folder: str = "INBOX",
    limit: int = 10,
    unread_only: bool = False,
) -> str:
    """Read emails from IMAP server."""
    try:
        import imaplib
        from email import message_from_bytes
        from email.header import decode_header

        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(username, password)
        mail.select(folder)

        if unread_only:
            status, messages = mail.search(None, "UNSEEN")
        else:
            status, messages = mail.search(None, "ALL")

        if status != "OK":
            return "No messages found"

        email_ids = messages[0].split()
        email_ids = email_ids[-limit:]  # Get latest

        results = []
        for eid in reversed(email_ids):
            status, msg_data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            msg = message_from_bytes(msg_data[0][1])

            # Decode subject
            subject = msg["Subject"]
            if subject:
                decoded = decode_header(subject)
                subject = decoded[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()

            # Get body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            results.append({
                "id": eid.decode(),
                "from": msg["From"],
                "to": msg["To"],
                "subject": subject,
                "date": msg["Date"],
                "body": body[:1000],
            })

        mail.logout()
        return json.dumps(results, indent=2)

    except ImportError:
        return "Error: imaplib not available"
    except Exception as e:
        return f"IMAP error: {e}"


EMAIL_TOOLS = {
    "send_email": {
        "func": send_email,
        "schema": {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": "Send an email via SMTP.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "smtp_host": {"type": "string", "description": "SMTP server host"},
                        "smtp_port": {"type": "integer", "description": "SMTP server port"},
                        "username": {"type": "string", "description": "Email username/address"},
                        "password": {"type": "string", "description": "Email password"},
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"},
                        "html": {"type": "boolean", "description": "Whether body is HTML (default: false)"},
                        "cc": {"type": "string", "description": "CC recipients (comma-separated)"},
                    },
                    "required": ["smtp_host", "smtp_port", "username", "password", "to", "subject", "body"],
                },
            },
        },
    },
    "read_emails": {
        "func": read_emails,
        "schema": {
            "type": "function",
            "function": {
                "name": "read_emails",
                "description": "Read emails from IMAP server.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "imap_host": {"type": "string", "description": "IMAP server host"},
                        "username": {"type": "string", "description": "Email username/address"},
                        "password": {"type": "string", "description": "Email password"},
                        "folder": {"type": "string", "description": "Mail folder (default: INBOX)"},
                        "limit": {"type": "integer", "description": "Max emails to read (default: 10)"},
                        "unread_only": {"type": "boolean", "description": "Only unread emails (default: false)"},
                    },
                    "required": ["imap_host", "username", "password"],
                },
            },
        },
    },
}
