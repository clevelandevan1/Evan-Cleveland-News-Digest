"""Interactive helper to put your secrets into .env correctly.

Run it from your own terminal:

    cd ~/news-digest && ./.venv/bin/python setup_secrets.py

It prompts for your Claude API key and your Gmail app password using hidden
input (nothing is displayed as you type or paste), cleans up stray spaces or
quotes, writes them into the .env next to this script, and then tests the
Gmail login. Your secrets are never printed and never leave this machine.
"""

import getpass
import re
import ssl
import smtplib
from pathlib import Path

ENV = Path(__file__).resolve().parent / ".env"


def set_key(text, key, value):
    """Replace `key=...` line in text, or append it if missing."""
    pattern = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
    line = f"{key}={value}"
    if pattern.search(text):
        return pattern.sub(line, text)
    return text.rstrip("\n") + "\n" + line + "\n"


def main():
    if not ENV.exists():
        print(f"No .env found at {ENV}. Run: cp .env.example .env")
        return
    text = ENV.read_text(encoding="utf-8")

    print(f"Updating {ENV}\n(press Enter to leave a value unchanged)\n")

    api = getpass.getpass("Paste your Claude API key (sk-ant-...): ").strip().strip('"').strip("'")
    if api:
        text = set_key(text, "ANTHROPIC_API_KEY", api)

    pw = getpass.getpass("Paste your Gmail 16-char app password: ")
    pw = pw.strip().strip('"').strip("'").replace(" ", "")  # Gmail shows it with spaces
    if pw:
        text = set_key(text, "SMTP_PASS", pw)

    ENV.write_text(text, encoding="utf-8")
    print("\n.env updated.")
    print(f"  ANTHROPIC_API_KEY : {'set (' + str(len(api)) + ' chars)' if api else 'unchanged'}")
    print(f"  SMTP_PASS         : {'set (' + str(len(pw)) + ' chars)' if pw else 'unchanged'}")

    if pw:
        # Re-read the file so we test exactly what was written.
        env = {}
        for ln in ENV.read_text(encoding="utf-8").splitlines():
            if "=" in ln and not ln.lstrip().startswith("#"):
                k, v = ln.split("=", 1)
                env[k.strip()] = v.strip()
        print("\nTesting Gmail login (no email is sent)...")
        try:
            ctx = ssl.create_default_context()
            with smtplib.SMTP(env.get("SMTP_HOST", "smtp.gmail.com"),
                              int(env.get("SMTP_PORT", "587")), timeout=30) as s:
                s.starttls(context=ctx)
                s.login(env["SMTP_USER"], env["SMTP_PASS"])
            print("SUCCESS: Gmail accepted the login. Email delivery is ready.")
        except Exception as e:  # noqa: BLE001
            print(f"FAILED: {type(e).__name__}: {e}")
            print("If it says BadCredentials: the app password is wrong or "
                  "2-Step Verification isn't enabled on the account.")


if __name__ == "__main__":
    main()
