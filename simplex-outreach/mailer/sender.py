import smtplib
import time
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def render_template(template: str, lead: dict) -> str:
    """Replace placeholders like {first_name}, {company} with lead data."""
    result = template
    for key, value in lead.items():
        result = result.replace("{" + key + "}", str(value or ""))
    # Clean up any unreplaced placeholders
    result = re.sub(r"\{[a-z_]+\}", "", result)
    return result.strip()


def send_email(smtp_config: dict, to_email: str, subject: str, body: str) -> dict:
    """
    Send a single email via SMTP.

    smtp_config keys: host, port, username, password, from_name, from_email
    Returns dict with 'success', 'error' keys.
    """
    result = {"success": False, "error": ""}

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        # Add unsubscribe header (CAN-SPAM compliance)
        msg["List-Unsubscribe"] = f"<mailto:{smtp_config['from_email']}?subject=unsubscribe>"

        # Plain text version
        msg.attach(MIMEText(body, "plain"))

        # HTML version (simple conversion: newlines to <br>)
        html_body = body.replace("\n", "<br>")
        html = f"""<html><body style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
        {html_body}
        <br><br>
        <p style="font-size: 11px; color: #999;">
        If you'd like to stop receiving these emails, simply reply with "unsubscribe".
        </p>
        </body></html>"""
        msg.attach(MIMEText(html, "html"))

        # Connect and send
        port = int(smtp_config["port"])
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_config["host"], port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_config["host"], port, timeout=30)
            server.starttls()

        server.login(smtp_config["username"], smtp_config["password"])
        server.sendmail(smtp_config["from_email"], to_email, msg.as_string())
        server.quit()

        result["success"] = True

    except smtplib.SMTPAuthenticationError:
        result["error"] = "Authentication failed. Check your username/password."
    except smtplib.SMTPRecipientsRefused:
        result["error"] = f"Recipient refused: {to_email}"
    except smtplib.SMTPException as e:
        result["error"] = f"SMTP error: {str(e)}"
    except Exception as e:
        result["error"] = f"Error: {str(e)}"

    return result


def send_bulk_emails(smtp_config: dict, leads: list, template_subject: str, template_body: str,
                     delay_seconds: int = 10, daily_limit: int = 200,
                     sent_today: int = 0, progress_callback=None):
    """
    Send emails to a list of leads with rate limiting.

    leads: list of dicts with at least 'email', 'first_name', 'last_name', etc.
    Returns list of result dicts.
    """
    results = []
    count = 0

    for lead in leads:
        if not lead.get("email"):
            results.append({"lead": lead, "success": False, "error": "No email", "skipped": True})
            continue

        if sent_today + count >= daily_limit:
            if progress_callback:
                progress_callback(f"Daily limit ({daily_limit}) reached. Stopping.")
            break

        subject = render_template(template_subject, lead)
        body = render_template(template_body, lead)

        if progress_callback:
            progress_callback(f"Sending to {lead['email']} ({count + 1}/{len(leads)})...")

        result = send_email(smtp_config, lead["email"], subject, body)
        result["lead"] = lead
        result["subject"] = subject
        result["body"] = body
        result["skipped"] = False
        results.append(result)

        count += 1

        # Rate limiting
        if count < len(leads):
            time.sleep(delay_seconds)

    return results


def test_smtp_connection(smtp_config: dict) -> dict:
    """Test SMTP connection without sending an email."""
    result = {"success": False, "error": ""}
    try:
        port = int(smtp_config["port"])
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_config["host"], port, timeout=15)
        else:
            server = smtplib.SMTP(smtp_config["host"], port, timeout=15)
            server.starttls()

        server.login(smtp_config["username"], smtp_config["password"])
        server.quit()
        result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result
