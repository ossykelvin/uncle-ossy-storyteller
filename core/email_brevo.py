"""Brevo transactional email (best-effort).

Used for app-side signup emails: a welcome to the new user and an alert to the
admin. These never raise into the auth flow — a mail failure must not block a
signup. (Supabase's own confirmation email is separate and configured via SMTP
in the Supabase dashboard.)
"""
import requests
from core.config import (
    APP_NAME, BREVO_API_KEY, BREVO_SENDER_EMAIL, BREVO_SENDER_NAME,
    SIGNUP_ALERT_EMAIL, brevo_enabled,
)

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def send_email(to_email: str, subject: str, html: str, to_name: str = "") -> tuple[bool, str]:
    if not brevo_enabled():
        return False, "Brevo not configured (BREVO_API_KEY / BREVO_SENDER_EMAIL)."
    recipient = {"email": to_email}
    if to_name:
        recipient["name"] = to_name
    payload = {
        "sender": {"email": BREVO_SENDER_EMAIL, "name": BREVO_SENDER_NAME},
        "to": [recipient],
        "subject": subject,
        "htmlContent": html,
    }
    headers = {"api-key": BREVO_API_KEY, "accept": "application/json", "content-type": "application/json"}
    try:
        r = requests.post(BREVO_URL, json=payload, headers=headers, timeout=15)
    except requests.RequestException as exc:
        return False, f"Brevo request failed: {exc}"
    if r.status_code >= 300:
        return False, f"Brevo error {r.status_code}: {(r.text or '').strip()[:300]}"
    try:
        return True, r.json().get("messageId", "sent")
    except Exception:
        return True, "sent"


def _wrap(title: str, body_html: str) -> str:
    return f"""<div style="font-family:Georgia,serif;max-width:560px;margin:0 auto;color:#111827">
  <div style="background:#0D1B3D;color:#fff;padding:20px 24px;border-radius:12px 12px 0 0">
    <h1 style="margin:0;font-size:20px">📚 {APP_NAME}</h1>
  </div>
  <div style="border:1px solid #e5e7eb;border-top:none;padding:24px;border-radius:0 0 12px 12px;line-height:1.6">
    <h2 style="margin-top:0;color:#0D1B3D">{title}</h2>
    {body_html}
  </div>
</div>"""


def send_welcome(email: str) -> tuple[bool, str]:
    html = _wrap(
        "Welcome aboard!",
        f"<p>Thanks for creating an account on {APP_NAME}.</p>"
        "<p>To finish setting up, please click the confirmation link in the verification "
        "email we just sent — then log in and start your first project.</p>"
        "<p>Happy writing,<br>The Ossy Story Teller team</p>",
    )
    return send_email(email, f"Welcome to {APP_NAME}", html)


def send_admin_signup_alert(new_user_email: str) -> tuple[bool, str]:
    if not SIGNUP_ALERT_EMAIL:
        return False, "No admin alert address configured."
    html = _wrap(
        "New signup",
        f"<p>A new user just signed up:</p><p><strong>{new_user_email}</strong></p>",
    )
    return send_email(SIGNUP_ALERT_EMAIL, f"New signup on {APP_NAME}", html)


def notify_signup(email: str) -> dict:
    """Fire welcome + admin alert. Best-effort; never raises."""
    results = {}
    for name, fn, arg in [("welcome", send_welcome, email), ("admin", send_admin_signup_alert, email)]:
        try:
            results[name] = fn(arg)
        except Exception as exc:
            results[name] = (False, str(exc))
    return results
