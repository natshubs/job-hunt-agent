import csv
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


PROJECT_DIR = Path("/Users/natashaanand/job-hunt-agent")
INPUT_FILE = PROJECT_DIR / "inputs" / "linkedin_saved_job_urls.txt"
OUTPUT_DIR = PROJECT_DIR / "outputs"

COLUMNS = [
    "Job Title",
    "Company Name",
    "Job URL",
    "Location",
    "Remote / Hybrid / In-person",
    "Salary",
    "Source",
    "Date Found",
    "Description",
    "Key Requirements",
    "Hiring Manager / Recruiter",
    "Hiring Contact URL",
    "Scrape Status",
    "Scrape Error",
]


def detect_source(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if "linkedin.com" in domain:
        return "LinkedIn"
    if "indeed.com" in domain:
        return "Indeed"
    if "greenhouse.io" in domain or "greenhouse" in domain:
        return "Greenhouse"
    if "lever.co" in domain:
        return "Lever"
    if "workdayjobs.com" in domain or "myworkdayjobs.com" in domain:
        return "Workday"
    if "wellfound.com" in domain:
        return "Wellfound"
    if "builtin.com" in domain:
        return "Built In"
    return "Company Website"


def infer_work_setting(text: str) -> str:
    text_lower = text.lower()
    if "field-based" in text_lower or "field based" in text_lower:
        return "Field-based"
    if "hybrid" in text_lower:
        return "Hybrid"
    if "remote" in text_lower:
        return "Remote"
    if "in-person" in text_lower or "onsite" in text_lower or "on-site" in text_lower:
        return "In-person"
    return "Unclear"


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_json_ld(soup: BeautifulSoup):
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                for item in data:
                    if item.get("@type") == "JobPosting":
                        return item
            elif data.get("@type") == "JobPosting":
                return data
        except Exception:
            continue
    return None


def scrape_url(url: str) -> dict:
    source = detect_source(url)
    today = datetime.now().strftime("%Y-%m-%d")

    row = {col: "" for col in COLUMNS}
    row["Job URL"] = url
    row["Source"] = source
    row["Date Found"] = today

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        html = response.text or ""

        if response.status_code >= 400:
            row["Scrape Status"] = "Failed"
            row["Scrape Error"] = f"HTTP {response.status_code}"
            return row

        soup = BeautifulSoup(html, "html.parser")
        page_text = clean_text(soup.get_text(" "))

        if "job no longer available" in page_text.lower() or "no longer accepting applications" in page_text.lower():
            row["Scrape Status"] = "Expired"

        json_ld = extract_json_ld(soup)

        if json_ld:
            row["Job Title"] = clean_text(json_ld.get("title", ""))
            org = json_ld.get("hiringOrganization", {})
            if isinstance(org, dict):
                row["Company Name"] = clean_text(org.get("name", ""))
            loc = json_ld.get("jobLocation", "")
            if isinstance(loc, dict):
                address = loc.get("address", {})
                if isinstance(address, dict):
                    row["Location"] = clean_text(", ".join(
                        x for x in [
                            address.get("addressLocality", ""),
                            address.get("addressRegion", ""),
                            address.get("addressCountry", ""),
                        ] if x
                    ))
            elif isinstance(loc, list) and loc:
                row["Location"] = clean_text(str(loc[0]))
            row["Description"] = clean_text(BeautifulSoup(json_ld.get("description", ""), "html.parser").get_text(" "))
            row["Remote / Hybrid / In-person"] = infer_work_setting(row["Description"] + " " + row["Location"])

            salary = json_ld.get("baseSalary", "")
            row["Salary"] = clean_text(str(salary)) if salary else ""

        if not row["Job Title"]:
            title = soup.find("title")
            title_text = clean_text(title.get_text()) if title else ""

            # LinkedIn page titles often look like:
            # "Company hiring Job Title in Location | LinkedIn"
            m = re.match(r"(.+?) hiring (.+?) in (.+?) [|] LinkedIn", title_text)
            if m:
                row["Company Name"] = clean_text(m.group(1))
                row["Job Title"] = clean_text(m.group(2))
                row["Location"] = clean_text(m.group(3))
            else:
                row["Job Title"] = title_text

        if not row["Description"]:
            row["Description"] = page_text[:5000]

        if not row["Remote / Hybrid / In-person"]:
            row["Remote / Hybrid / In-person"] = infer_work_setting(page_text)

        if not row["Scrape Status"]:
            if row["Job Title"] or row["Description"]:
                row["Scrape Status"] = "Success" if row["Job Title"] and row["Description"] else "Partial"
            else:
                row["Scrape Status"] = "Failed"
                row["Scrape Error"] = "No usable job details extracted"

        return row

    except Exception as e:
        row["Scrape Status"] = "Failed"
        row["Scrape Error"] = str(e)
        return row


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    raw_urls = [line.strip() for line in INPUT_FILE.read_text().splitlines() if line.strip()]
    unique_urls = list(dict.fromkeys(raw_urls))
    duplicate_count = len(raw_urls) - len(unique_urls)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_file = OUTPUT_DIR / f"linkedin_saved_jobs_scraped_{timestamp}.csv"

    rows = [scrape_url(url) for url in unique_urls]

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    success = sum(1 for r in rows if r["Scrape Status"] == "Success")
    partial = sum(1 for r in rows if r["Scrape Status"] == "Partial")
    failed = sum(1 for r in rows if r["Scrape Status"] == "Failed")
    expired = sum(1 for r in rows if r["Scrape Status"] == "Expired")

    print(f"URLs found: {len(raw_urls)}")
    print(f"Duplicate URLs removed: {duplicate_count}")
    print(f"Successfully scraped: {success}")
    print(f"Partially scraped: {partial}")
    print(f"Failed: {failed}")
    print(f"Expired: {expired}")
    print(f"Output CSV path: {output_file}")


if __name__ == "__main__":
    main()
