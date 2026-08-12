import email.utils as email_utils
import os
import smtplib
from email.mime.text import MIMEText

from flask import Flask, jsonify, request

app = Flask(__name__)

GMAIL_USER = os.environ.get("GMAIL_USER", "peacedamola534@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

REQUIRED = ("name", "email", "message")


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.form or request.get_json(silent=True) or {}

    honeypot = str(data.get("_hp", "")).strip()
    if honeypot:
        return jsonify({"ok": True})

    missing = [k for k in REQUIRED if not str(data.get(k, "")).strip()]
    if missing:
        return jsonify({"ok": False, "error": "Missing fields: " + ", ".join(missing)}), 400

    name = str(data["name"]).strip()
    visitor_email = str(data["email"]).strip()
    project_type = str(data.get("project_type", "")).strip()
    budget = str(data.get("budget", "")).strip()
    message = str(data["message"]).strip()

    subject = f"New project inquiry from {name} — Olukoya Martins portfolio"
    body = (
        f"Name: {name}\n"
        f"Email: {visitor_email}\n"
        f"Project type: {project_type or 'Not specified'}\n"
        f"Budget: {budget or 'Not specified'}\n\n"
        f"Message:\n{message}\n"
    )

    if not GMAIL_APP_PASSWORD:
        return (
            jsonify({"ok": False, "error": "Email delivery is not configured yet."}),
            500,
        )

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = f"Portfolio Contact <{GMAIL_USER}>"
    msg["To"] = GMAIL_USER
    msg["Reply-To"] = visitor_email
    msg["Date"] = email_utils.formatdate(localtime=True)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, [GMAIL_USER], msg.as_string())
    except Exception:
        return (
            jsonify({"ok": False, "error": "Could not send. Please email directly."}),
            500,
        )

    return jsonify({"ok": True})


@app.route("/api/contact", methods=["GET", "OPTIONS"])
def contact_info():
    return jsonify({"ok": True, "message": "POST your contact form here."})
