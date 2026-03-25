import re
import time
from ddgs import DDGS


def _clean_text(text: str) -> str:
    """Remove special unicode characters."""
    return re.sub(r'[\u200e\u200f\u200b\u200c\u200d\u202a-\u202e]', '', text).strip()


def _parse_result(title: str, body: str, href: str):
    """Parse a DuckDuckGo search result into structured lead data."""
    lead = {
        "full_name": "",
        "first_name": "",
        "last_name": "",
        "title": "",
        "company": "",
        "linkedin_url": href.split('?')[0].rstrip('/'),
        "location": "",
    }

    title = _clean_text(title)
    body = _clean_text(body)

    # DuckDuckGo sometimes concatenates multiple results in the title
    # e.g. "Ahmad Malik - Fintech Founder - Chief Risk Officer ... Nameer Khan - M"
    # Cut at "..." if present to get just the first person
    if "..." in title:
        title = title[:title.index("...")].strip()

    # Remove LinkedIn suffix
    title = title.replace(" | LinkedIn", "").replace(" - LinkedIn", "")

    # Split by " - " or " – "
    parts = [p.strip() for p in re.split(r'\s*[-–]\s*', title)]

    if parts:
        lead["full_name"] = parts[0]
        name_parts = parts[0].split()
        if len(name_parts) >= 2:
            lead["first_name"] = name_parts[0]
            lead["last_name"] = " ".join(name_parts[1:])
        elif len(name_parts) == 1:
            lead["first_name"] = name_parts[0]

    if len(parts) >= 2:
        lead["title"] = parts[1]
    if len(parts) >= 3:
        lead["company"] = parts[2]

    # Extract info from body/snippet
    if body:
        loc_match = re.search(r"([A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z\s]+)?)\s*[·]", body)
        if loc_match:
            lead["location"] = loc_match.group(1).strip()

        if not lead["company"]:
            at_match = re.search(r"(?:at|@)\s+([A-Za-z0-9\s&.]+)", body)
            if at_match:
                lead["company"] = at_match.group(1).strip()

        # If title is still empty, try to get it from body
        if not lead["title"] and body:
            # Body often starts with the title: "Founder | Fintech | ..." or "CEO at Company"
            title_match = re.match(r"^([^·\n]{5,60}?)(?:\s*·|\s*-\s)", body)
            if title_match:
                lead["title"] = title_match.group(1).strip()

    return lead


def _extract_domain_from_company(company_name: str) -> str:
    """Guess company domain from company name."""
    if not company_name:
        return ""
    name = company_name.lower().strip()
    for suffix in [" inc", " inc.", " ltd", " ltd.", " llc", " co.", " corp",
                   " corporation", " pvt", " pvt.", " private limited", " limited"]:
        name = name.replace(suffix, "")
    name = re.sub(r"[^a-z0-9]", "", name)
    return f"{name}.com" if name else ""


def search_linkedin_founders(query: str, num_results: int = 20, progress_callback=None):
    """
    Search DuckDuckGo for LinkedIn profiles matching the query.
    query: e.g. 'founder fintech Dubai'
    Returns list of parsed lead dicts.
    """
    leads = []
    seen_urls = set()
    search_query = f'site:linkedin.com/in {query}'

    if progress_callback:
        progress_callback("Searching DuckDuckGo for LinkedIn profiles...")

    try:
        results = DDGS().text(search_query, max_results=min(num_results + 10, 100))

        for r in results:
            href = r.get('href', '')
            if 'linkedin.com/in/' not in href:
                continue

            clean_url = href.split('?')[0].rstrip('/')
            if clean_url in seen_urls:
                continue
            seen_urls.add(clean_url)

            lead = _parse_result(r.get('title', ''), r.get('body', ''), href)
            lead["company_domain"] = _extract_domain_from_company(lead["company"])
            lead["search_query"] = query
            leads.append(lead)

            if progress_callback and len(leads) % 5 == 0:
                progress_callback(f"Found {len(leads)} leads so far...")

            if len(leads) >= num_results:
                break

    except Exception as e:
        if progress_callback:
            progress_callback(f"Search error: {e}")

    if progress_callback:
        progress_callback(f"Done! Found {len(leads)} leads.")

    return leads[:num_results]


if __name__ == "__main__":
    results = search_linkedin_founders("founder fintech Dubai", num_results=10,
                                        progress_callback=print)
    for r in results:
        print(f"{r['full_name']} | {r['title']} | {r['company']} | {r['linkedin_url']}")
