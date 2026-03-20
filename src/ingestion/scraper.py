import requests
import hashlib
from bs4 import BeautifulSoup
from src.ingestion.database import Session, Document
from dotenv import load_dotenv

load_dotenv()


def scrape_url(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (Chrome/120.0.0.0 Safari/537.36)"
        }
        resp = requests.get(url, timeout=10, headers=headers)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ✗ Failed: {url} — {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["nav", "footer", "script",
                     "style", "header", "aside"]):
        tag.decompose()

    raw_text     = soup.get_text(separator="\n", strip=True)
    title        = soup.title.string if soup.title else url
    content_hash = hashlib.md5(raw_text.encode()).hexdigest()

    return {
        "url":      url,
        "title":    title.strip(),
        "raw_text": raw_text[:50_000],
        "hash":     content_hash
    }


def scrape_all(urls, department):
    session    = Session()
    new_count  = 0
    skipped    = 0

    for url in urls:
        print(f"Scraping: {url}")
        data = scrape_url(url)
        if not data:
            continue

        existing = session.query(Document)\
                          .filter_by(url=url).first()

        if existing and existing.hash == data["hash"]:
            print(f"  → unchanged, skipping")
            skipped += 1
            continue

        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            existing.department = department
        else:
            doc = Document(**data, department=department)
            session.add(doc)

        new_count += 1
        print(f"  ✓ saved")

    session.commit()
    session.close()
    print(f"\n✓ Done: {new_count} new/updated, {skipped} unchanged")


if __name__ == "__main__":
    test_urls = [
        "https://en.wikipedia.org/wiki/Leave_of_absence",
        "https://en.wikipedia.org/wiki/Incident_management",
        "https://en.wikipedia.org/wiki/Knowledge_base",
    ]
    scrape_all(test_urls, department="general")