from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def send_alert_email(subject: str, body: str) -> bool:
    enabled = os.getenv("EMAIL_ENABLED", "true").lower() == "true"
    if not enabled:
        print("[email] EMAIL_ENABLED=false. Simulacao:")
        print(subject)
        print(body)
        return False

    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    email_to = os.getenv("ALERT_EMAIL_TO")
    email_from = os.getenv("ALERT_EMAIL_FROM", user or "")

    missing = [
        name
        for name, value in {
            "SMTP_HOST": host,
            "SMTP_USER": user,
            "SMTP_PASSWORD": password,
            "ALERT_EMAIL_TO": email_to,
            "ALERT_EMAIL_FROM": email_from,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Variaveis SMTP ausentes: {', '.join(missing)}")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = email_from
    message["To"] = email_to
    message.set_content(body)

    with smtplib.SMTP(host, port, timeout=20) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(message)

    return True
