"""Optional email delivery of the rendered digest, over SMTP.

All settings come from environment variables (loaded from .env by the cron
wrapper), so no credentials ever live in code or git:

    SMTP_HOST   default smtp.gmail.com
    SMTP_PORT   default 587 (STARTTLS)
    SMTP_USER   the sending account, e.g. you@gmail.com
    SMTP_PASS   an app password (NOT your normal login password)
    DIGEST_TO   recipient address
    DIGEST_FROM optional; defaults to SMTP_USER

If SMTP_USER / SMTP_PASS / DIGEST_TO aren't all set, email is simply skipped.
"""

import os
import smtplib
import ssl
from email.message import EmailMessage


def email_config():
    """Return an SMTP config dict, or None if email isn't fully configured."""
    to = os.environ.get("DIGEST_TO")
    user = os.environ.get("SMTP_USER")
    # Gmail displays app passwords in 4 groups with spaces; the real value is
    # the 16 characters with no spaces. Normalize so a pasted-with-spaces
    # password works either way.
    password = (os.environ.get("SMTP_PASS") or "").replace(" ", "").strip()
    if not (to and user and password):
        return None
    return {
        "host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": user,
        "password": password,
        "to": to,
        "from": os.environ.get("DIGEST_FROM", user),
    }


def send_digest(subject, html_body, cfg):
    """Send `html_body` as an HTML email using the given SMTP config.

    Raises on failure so the caller can log it; the digest file has already
    been written by this point either way.
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg["from"]
    msg["To"] = cfg["to"]
    msg.set_content(
        "Your morning digest is in this message as HTML. "
        "View it in an HTML-capable email client."
    )
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP(cfg["host"], cfg["port"], timeout=30) as server:
        server.starttls(context=context)
        server.login(cfg["user"], cfg["password"])
        server.send_message(msg)
