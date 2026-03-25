import re
import dns.resolver
import smtplib
import socket
import time


# Common email patterns for businesses
EMAIL_PATTERNS = [
    "{first}@{domain}",
    "{first}.{last}@{domain}",
    "{first}{last}@{domain}",
    "{f}{last}@{domain}",
    "{first}_{last}@{domain}",
    "{first}.{l}@{domain}",
    "{f}.{last}@{domain}",
    "{last}@{domain}",
]


def generate_email_guesses(first_name: str, last_name: str, domain: str) -> list:
    """Generate possible email addresses based on name and domain."""
    if not first_name or not domain:
        return []

    first = first_name.lower().strip()
    last = last_name.lower().strip() if last_name else ""
    f = first[0] if first else ""
    l = last[0] if last else ""

    guesses = []
    for pattern in EMAIL_PATTERNS:
        try:
            email = pattern.format(first=first, last=last, f=f, l=l, domain=domain)
            # Skip patterns that produce empty segments
            if ".@" in email or "@." in email or ".." in email or not last and "{last}" in pattern:
                continue
            guesses.append(email)
        except (KeyError, IndexError):
            continue

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for g in guesses:
        if g not in seen:
            seen.add(g)
            unique.append(g)
    return unique


def check_mx_record(domain: str) -> bool:
    """Check if a domain has valid MX records (can receive email)."""
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        return len(mx_records) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, Exception):
        return False


def get_mx_host(domain: str) -> str:
    """Get the primary MX host for a domain."""
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        # Sort by priority (lowest = highest priority)
        records = sorted(mx_records, key=lambda r: r.preference)
        return str(records[0].exchange).rstrip(".")
    except Exception:
        return ""


def verify_email_smtp(email: str, timeout: int = 10) -> str:
    """
    Verify email via SMTP RCPT TO check.
    Returns: 'valid', 'invalid', or 'unknown' (catch-all or server refused).

    Note: Many mail servers block this technique or accept all addresses.
    This is a best-effort check.
    """
    domain = email.split("@")[1]
    mx_host = get_mx_host(domain)
    if not mx_host:
        return "unknown"

    try:
        smtp = smtplib.SMTP(timeout=timeout)
        smtp.connect(mx_host, 25)
        smtp.helo("check.example.com")
        smtp.mail("verify@example.com")
        code, _ = smtp.rcpt(email)
        smtp.quit()

        if code == 250:
            return "valid"
        elif code == 550:
            return "invalid"
        else:
            return "unknown"
    except (smtplib.SMTPException, socket.error, OSError):
        return "unknown"


def find_email(first_name: str, last_name: str, domain: str, verify: bool = True) -> dict:
    """
    Find the most likely email for a person at a domain.
    Returns dict with 'email', 'guesses', 'mx_valid', 'verified' status.
    """
    result = {
        "email": "",
        "guesses": [],
        "mx_valid": False,
        "verified": False,
    }

    if not domain:
        return result

    # Step 1: Check if domain has MX records
    result["mx_valid"] = check_mx_record(domain)
    if not result["mx_valid"]:
        return result

    # Step 2: Generate email guesses
    guesses = generate_email_guesses(first_name, last_name, domain)
    result["guesses"] = guesses

    if not guesses:
        return result

    # Step 3: If verify is enabled, try SMTP verification
    if verify:
        for guess in guesses[:3]:  # Only verify top 3 to avoid being blocked
            status = verify_email_smtp(guess)
            if status == "valid":
                result["email"] = guess
                result["verified"] = True
                return result
            time.sleep(1)

    # Fallback: return the most common pattern (first@domain or first.last@domain)
    result["email"] = guesses[0]
    return result


if __name__ == "__main__":
    result = find_email("John", "Doe", "example.com", verify=False)
    print(f"Best guess: {result['email']}")
    print(f"All guesses: {result['guesses']}")
