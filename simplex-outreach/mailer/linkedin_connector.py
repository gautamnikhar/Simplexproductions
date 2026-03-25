import time
import re
from requests.cookies import RequestsCookieJar
from linkedin_api import Linkedin


def create_client_with_cookies(li_at: str, jsessionid: str) -> dict:
    """
    Authenticate with LinkedIn using browser cookies (bypasses CAPTCHA).
    li_at: the 'li_at' cookie value from your browser
    jsessionid: the 'JSESSIONID' cookie value from your browser
    Returns dict with 'success', 'client', 'error' keys.
    """
    result = {"success": False, "client": None, "error": ""}

    # Clean up cookie values (remove surrounding quotes if present)
    li_at = li_at.strip().strip('"')
    jsessionid = jsessionid.strip().strip('"')

    if not li_at or not jsessionid:
        result["error"] = "Both li_at and JSESSIONID cookies are required."
        return result

    try:
        # Build a proper RequestsCookieJar (linkedin-api expects this, not a plain dict)
        cookie_jar = RequestsCookieJar()
        cookie_jar.set("li_at", li_at, domain=".linkedin.com", path="/")
        cookie_jar.set("JSESSIONID", f'"{jsessionid}"', domain=".linkedin.com", path="/")

        api = Linkedin("", "", cookies=cookie_jar)

        # Verify the session works by fetching own profile
        me = api.get_user_profile()
        if not me:
            result["error"] = "Cookies are expired or invalid. Please grab fresh cookies from your browser."
            return result

        result["success"] = True
        result["client"] = api

    except Exception as e:
        error_str = str(e)
        if "401" in error_str or "unauthorized" in error_str.lower():
            result["error"] = "Cookies are expired or invalid. Please grab fresh cookies from your browser."
        else:
            result["error"] = f"Login failed: {error_str}"

    return result


def get_profile_id_from_url(linkedin_url: str) -> str:
    """Extract the public profile ID from a LinkedIn URL."""
    match = re.search(r'linkedin\.com/in/([^/?]+)', linkedin_url)
    return match.group(1) if match else ""


def send_connection_request(client: Linkedin, linkedin_url: str, note: str = "") -> dict:
    """
    Send a connection request to a LinkedIn profile.
    note: max 300 characters.
    Returns dict with 'success', 'error' keys.
    """
    result = {"success": False, "error": ""}

    profile_id = get_profile_id_from_url(linkedin_url)
    if not profile_id:
        result["error"] = f"Could not extract profile ID from URL: {linkedin_url}"
        return result

    # Enforce 300 char limit
    if note and len(note) > 300:
        note = note[:297] + "..."

    try:
        # Send the connection request
        if note:
            client.add_connection(profile_public_id=profile_id, message=note)
        else:
            client.add_connection(profile_public_id=profile_id)

        result["success"] = True

    except Exception as e:
        error_str = str(e)
        if "already" in error_str.lower():
            result["error"] = "Already connected or pending request."
        elif "limit" in error_str.lower() or "restrict" in error_str.lower():
            result["error"] = "Weekly connection limit reached. Stop and wait."
        else:
            result["error"] = f"Error: {error_str}"

    return result


def render_note(template: str, lead: dict) -> str:
    """Replace placeholders in note template. Enforces 300 char limit."""
    result = template
    for key, value in lead.items():
        result = result.replace("{" + key + "}", str(value or ""))
    # Clean up unreplaced placeholders
    result = re.sub(r"\{[a-z_]+\}", "", result)
    result = result.strip()
    if len(result) > 300:
        result = result[:297] + "..."
    return result


def test_linkedin_cookies(li_at: str, jsessionid: str) -> dict:
    """Test LinkedIn cookie auth without performing any actions."""
    return create_client_with_cookies(li_at, jsessionid)
