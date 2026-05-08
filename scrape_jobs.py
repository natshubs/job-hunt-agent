from jobspy import scrape_jobs
from datetime import datetime
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

SEARCHES = [
    {
        "label": "medical_affairs_strategy_comms",
        "search_term": (
            '"medical affairs" OR "medical strategy" OR "scientific strategy" '
            'OR "medical communications" OR "scientific communications" '
            'OR "medical information" OR "medical excellence" '
            'OR "medical capabilities" OR "medical affairs operations"'
        ),
        "location": "California",
        "site_name": ["linkedin", "indeed", "google"],
        "results_wanted": 75,
    },
    {
        "label": "msl_field_medical",
        "search_term": (
            '"medical science liaison" OR MSL OR "senior medical science liaison" '
            'OR "field medical scientist" OR "medical outcomes liaison" '
            'OR "field medical lead" OR "regional medical science liaison"'
        ),
        "location": "California",
        "site_name": ["linkedin", "indeed", "google"],
        "results_wanted": 75,
    },
    {
        "label": "clinical_development_science",
        "search_term": (
            '"clinical scientist" OR "senior clinical scientist" '
            'OR "clinical development" OR "clinical science" '
            'OR "clinical strategy" OR "clinical program lead" '
            'OR "medical monitor"'
        ),
        "location": "United States",
        "site_name": ["linkedin", "indeed", "google"],
        "results_wanted": 75,
    },
    {
        "label": "healthcare_ai_digital_health",
        "search_term": (
            '"clinical AI" OR "medical AI" OR "healthcare AI" '
            'OR "LLM evaluation" healthcare OR "GenAI evaluation" healthcare '
            'OR "AI clinical evaluator" OR "clinical product manager" '
            'OR "clinical product" healthcare OR "digital health" clinical '
            'OR "healthcare product strategy"'
        ),
        "location": "United States",
        "site_name": ["linkedin", "indeed", "google"],
        "results_wanted": 75,
    },
    {
        "label": "precision_medicine_neuropsych",
        "search_term": (
            '"precision medicine" psychiatry OR "precision medicine" neuroscience '
            'OR "precision medicine" neuropsychiatry OR "precision medicine" CNS '
            'OR "medical affairs" "precision medicine"'
        ),
        "location": "United States",
        "site_name": ["linkedin", "indeed", "google"],
        "results_wanted": 50,
    },
    {
        "label": "life_sciences_consulting",
        "search_term": (
            '"life sciences" consultant OR "life sciences" "senior consultant" '
            'OR "healthcare strategy" consultant OR "medical affairs" consultant '
            'OR "clinical strategy" consultant OR "digital health" consultant '
            'OR "healthcare AI" consultant OR "pharma strategy" consultant'
        ),
        "location": "United States",
        "site_name": ["linkedin", "indeed", "google"],
        "results_wanted": 75,
    },
]

HARD_EXCLUDE_KEYWORDS = [
    # Residency / physician / license-dependent roles
    "resident physician",
    "residency",
    "resident doctor",
    "medical resident",
    "physician",
    "psychiatrist",
    "attending physician",
    "hospitalist",
    "primary care physician",
    "family medicine physician",
    "internal medicine physician",
    "emergency medicine physician",
    "medical doctor",
    "licensed physician",
    "unrestricted medical license",
    "active medical license",
    "state medical license",
    "medical license",
    "board certified",
    "board-certified",
    "board eligible",
    "board-eligible",
    "be/bc",
    "bc/be",
    "dea license",
    "prescribing license",
    "patient panel",
    "outpatient clinic",
    "inpatient psychiatrist",

    # Other licensed clinical roles
    "registered nurse",
    "nurse practitioner",
    "physician assistant",
    "pa-c",
    "pharmacist",
    "physical therapist",
    "occupational therapist",
    "speech therapist",
    "chiropractor",
    "dentist",
    "veterinarian",

    # Too junior / admin / random
    "medical assistant",
    "clinical assistant",
    "research assistant",
    "scheduler",
    "receptionist",
    "technician",
    "aide",
    "server",
    "waiter",
    "waitress",
    "teacher",
    "coach",
    "operator",
    "office assistant",
    "referral coordinator",
    "administrator",
    "administrative",
    "fitness center",
    "support services",

    # Too senior
    "vice president",
    "vp,",
    "vp ",
    "executive director",
    "chief medical officer",
    "chief scientific officer",
    "senior director",

    # Specific bad fits
    "principal clinical scientist",
    "principal scientist",
    "omnichannel",
    "strategic excellence",
    "automation engineering",
    "director, automation",
    "automation engineer",
    "medical writer",
    "health informatics",
    "wire operator",

    # Functions you do not want
    "regulatory affairs",
    "quality assurance",
    "quality control",
    "clinical research associate",
    "site monitor",
    "clinical trial manager",
    "clinical operations manager",

    # Therapeutic areas you do not want
    "rheumatology",
    "dermatology",
    "ophthalmology",
    "gastroenterology",
    "hepatology",
    "nephrology",
    "urology",
    "infectious disease",
    "vaccines",
    "immunology",

    # Genomics/biomarker-heavy roles
    "biomarker strategy",
    "genomics",
    "genomic medicine",
    "clinical genomics",
    "companion diagnostics",
]

TITLE_INCLUDE_KEYWORDS = [
    # Medical affairs / strategy / communications
    "medical affairs",
    "medical strategy",
    "scientific strategy",
    "medical communications",
    "scientific communications",
    "medical information",
    "medical excellence",
    "medical capabilities",
    "field medical",
    "medical science liaison",
    "msl",

    # Clinical development / science
    "clinical scientist",
    "clinical development",
    "clinical science",
    "clinical strategy",
    "clinical program",
    "medical monitor",

    # AI / digital health / product
    "clinical ai",
    "medical ai",
    "healthcare ai",
    "ai clinical",
    "llm",
    "genai",
    "clinical evaluator",
    "clinical evaluation",
    "clinical quality",
    "clinical safety",
    "clinical content",
    "clinical product",
    "digital health",
    "digital medicine",
    "healthcare product",
    "product strategy",

    # Precision medicine
    "precision medicine",

    # Consulting / strategy
    "life sciences consultant",
    "senior consultant",
    "healthcare strategy",
    "medical affairs consultant",
    "clinical strategy consultant",
    "digital health consultant",
    "healthcare ai consultant",
    "pharma strategy",
    "strategy consultant",
]

PREFERRED_CONTEXT_KEYWORDS = [
    "psychiatry",
    "neuropsychiatry",
    "neuroscience",
    "cns",
    "behavioral health",
    "mental health",
    "ai",
    "llm",
    "genai",
    "digital health",
    "precision medicine",
    "medical affairs",
    "clinical development",
]


def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).lower()


def has_any_keyword(text, keywords):
    return any(keyword in text for keyword in keywords)


def combined_job_text(row):
    fields = ["title", "company", "location", "description", "job_type", "search_bucket"]
    return " ".join(normalize_text(row.get(field, "")) for field in fields)


def classify_job(row):
    title = normalize_text(row.get("title", ""))
    text = combined_job_text(row)

    if has_any_keyword(text, HARD_EXCLUDE_KEYWORDS):
        return "exclude"

    # Keep Associate Director, but exclude standalone Director roles.
    if title.startswith("director") and not title.startswith("associate director"):
        return "exclude"

    # Main rule: title must look relevant.
    if has_any_keyword(title, TITLE_INCLUDE_KEYWORDS):
        if has_any_keyword(text, PREFERRED_CONTEXT_KEYWORDS):
            return "strong_review"
        return "review"

    return "exclude"


all_jobs = []

for search in SEARCHES:
    print(f"Running search: {search['label']}")
    try:
        jobs = scrape_jobs(
            site_name=search["site_name"],
            search_term=search["search_term"],
            location=search["location"],
            results_wanted=search["results_wanted"],
            hours_old=720,
            country_indeed="USA",
            linkedin_fetch_description=True,
        )

        if jobs is None or jobs.empty:
            print(f"No jobs found for {search['label']}")
            continue

        jobs["search_bucket"] = search["label"]
        jobs["date_found"] = datetime.today().strftime("%Y-%m-%d")
        all_jobs.append(jobs)

    except Exception as e:
        print(f"Error running {search['label']}: {e}")

if not all_jobs:
    print("No jobs found from any search.")
    raise SystemExit

combined = pd.concat(all_jobs, ignore_index=True)

if "job_url" in combined.columns:
    combined = combined.drop_duplicates(subset=["job_url"], keep="first")
else:
    dedupe_cols = [col for col in ["title", "company", "location"] if col in combined.columns]
    combined = combined.drop_duplicates(subset=dedupe_cols, keep="first")

combined["fit_category"] = combined.apply(classify_job, axis=1)

review_jobs = combined[combined["fit_category"].isin(["strong_review", "review"])].copy()
excluded_jobs = combined[combined["fit_category"] == "exclude"].copy()

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

review_output_path = OUTPUT_DIR / f"jobspy_REVIEW_jobs_{timestamp}.csv"
excluded_output_path = OUTPUT_DIR / f"jobspy_EXCLUDED_jobs_{timestamp}.csv"
all_output_path = OUTPUT_DIR / f"jobspy_ALL_jobs_{timestamp}.csv"

review_jobs.to_csv(review_output_path, index=False)
excluded_jobs.to_csv(excluded_output_path, index=False)
combined.to_csv(all_output_path, index=False)

print(f"Saved {len(review_jobs)} review jobs to {review_output_path}")
print(f"Saved {len(excluded_jobs)} excluded jobs to {excluded_output_path}")
print(f"Saved {len(combined)} total jobs to {all_output_path}")

if not review_jobs.empty:
    preview_cols = [
        col for col in ["fit_category", "title", "company", "location", "job_url"]
        if col in review_jobs.columns
    ]
    print(review_jobs[preview_cols].head(40).to_string(index=False))
else:
    print("No review jobs passed the filters.")