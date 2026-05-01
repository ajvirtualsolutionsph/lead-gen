import re
import time
import random
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

CONTACT_PATHS = ["/contact", "/contact-us", "/about", "/about-us"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

EXCLUDE_DOMAINS = {"sentry.io", "example.com", "wixpress.com", "squarespace.com"}

_PREFERRED_PREFIXES = ("contact", "info", "hello", "hi", "enquiries", "enquiry", "support", "sales")


def _pick_best_email(emails):
    for prefix in _PREFERRED_PREFIXES:
        for e in sorted(emails):
            if e.lower().startswith(prefix + "@"):
                return e
    return sorted(emails)[0]


def extract_emails_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    emails = set()

    # mailto links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("mailto:"):
            email = href[7:].split("?")[0].strip()
            if EMAIL_REGEX.match(email):
                emails.add(email)

    # plain text scan
    text = soup.get_text()
    for match in EMAIL_REGEX.findall(text):
        emails.add(match)

    # Filter out common false positives
    filtered = set()
    for e in emails:
        domain = e.split("@")[-1].lower()
        if domain not in EXCLUDE_DOMAINS and not domain.endswith(".png") and not domain.endswith(".jpg"):
            filtered.add(e)

    return filtered


def find_email_for_site(website):
    """Crawl a website and its contact pages to find a contact email. Returns email string or None."""
    base = website.rstrip("/")
    parsed = urlparse(base)
    if not parsed.scheme:
        base = "https://" + base

    urls_to_try = [base] + [base + path for path in CONTACT_PATHS]

    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
            if resp.status_code != 200:
                continue
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                continue
            emails = extract_emails_from_html(resp.text)
            if emails:
                return _pick_best_email(emails)
        except Exception:
            continue

    return None


