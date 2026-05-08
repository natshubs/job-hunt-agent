import argparse
import re
from pathlib import Path

import pandas as pd


TITLE_CORE_MATCHES = [
    "medical affairs",
    "medical director",
    "associate medical director",
    "clinical development",
    "clinical scientist",
    "clinical science",
    "clinical strategy",
    "medical science liaison",
    "field medical",
    "scientific director",
    "medical communications",
    "medical information",
    "clinical product",
    "clinical product manager",
    "healthcare product",
    "digital health",
    "healthcare ai",
    "health ai",
    "clinical ai",
    "precision medicine",
    "genomics",
]

TITLE_THERAPEUTIC_MATCHES = [
    "psychiatry",
    "psychiatric",
    "neuropsychiatry",
    "neuroscience",
    "neurology",
    "mental health",
    "behavioral health",
    "schizophrenia",
    "depression",
    "bipolar",
    "ocd",
    "adhd",
    "substance use",
]

SUPPORTING_CONTENT_MATCHES = [
    "medical affairs",
    "clinical development",
    "clinical strategy",
    "clinical scientist",
    "clinical science",
    "field medical",
    "medical science liaison",
    "msl",
    "medical communications",
    "scientific communications",
    "medical information",
    "evidence generation",
    "real-world evidence",
    "rwe",
    "digital health",
    "machine learning",
    "large language model",
    "llm",
    "generative ai",
    "clinical ai",
    "healthcare ai",
    "precision medicine",
    "genomics",
    "genetic",
    "biomarker",
    "psychiatry",
    "psychiatric",
    "neuropsychiatry",
    "neuroscience",
    "mental health",
    "behavioral health",
    "schizophrenia",
    "depression",
    "bipolar",
]

GOOD_SEARCH_BUCKETS = [
    "medical_affairs_strategy_comms",
    "msl_field_medical",
    "clinical_development_science",
    "healthcare_ai_digital_health",
    "precision_medicine_genomics",
    "precision_medicine_neuropsych",
    "life_sciences_consulting",
]

EXCLUDE_TITLE_KEYWORDS = [
    "chiropractor",
    "physical therapist",
    "occupational therapist",
    "speech therapist",
    "respiratory therapist",
    "technologist",
    "technician",
    "sonographer",
    "nurse",
    "registered nurse",
    " rn ",
    "lpn",
    "lvn",
    "cna",
    "medical assistant",
    "dentist",
    "dental",
    "pharmacist",
    "pharmacy",
    "veterinarian",
    "veterinary",
    "social worker",
    "licensed therapist",
    "case manager",
    "regulatory affairs",
    "medical writer",
    "health informatics",
    "account executive",
    "sales representative",
    "territory sales",
    "sales manager",
    "chief medical officer",
    "chief scientific officer",
    "chief clinical officer",
    "vice president",
    " vp ",
    "svp",
]

WRONG_MSL_AREAS = [
    "rheumatology",
    "dermatology",
    "gastroenterology",
    "ophthalmology",
    "immunology",
    "nephrology",
    "urology",
    "endocrinology",
    "metabolic",
    "diabetes",
    "skeletal",
    "cardiorenal",
    "pah",
    "pulmonary arterial hypertension",
]

TOO_SENIOR_TERMS = [
    "executive director",
    "senior director",
    "sr. director",
    "vice president",
    "vp",
    "chief",
]

TOO_JUNIOR_TERMS = [
    "coordinator",
    "assistant",
    "intern",
    "entry level",
]


def normalize_text(value):
    if pd.isna(value):
        return ""
    return f" {str(value).lower().strip()} "


def compact_text(value):
    if pd.isna(value):
        return ""
    return str(value).lower().strip()


def get_field(row, *names):
    for name in names:
        if name in row:
            return row.get(name, "")
    return ""


def has_phrase(text, phrase):
    phrase = phrase.lower().strip()
    return re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text) is not None


def has_any(text, phrases):
    return any(has_phrase(text, phrase) for phrase in phrases)


def score_job(row):
    title = normalize_text(get_field(row, "Job Title", "title"))
    title_raw = compact_text(get_field(row, "Job Title", "title"))
    company = normalize_text(get_field(row, "Company Name", "company"))
    description = normalize_text(get_field(row, "Description", "description"))
    location = normalize_text(get_field(row, "Location", "location"))
    remote_field = normalize_text(get_field(row, "Remote / Hybrid / In-person", "is_remote", "work_from_home_type"))
    job_level = normalize_text(get_field(row, "job_level", "Job Level"))
    job_function = normalize_text(get_field(row, "job_function", "Job Function"))
    search_bucket = compact_text(get_field(row, "search_bucket", "Search Bucket"))
    skills = normalize_text(get_field(row, "skills", "Skills"))
    company_industry = normalize_text(get_field(row, "company_industry", "Company Industry"))

    combined = " ".join(
        [
            title,
            company,
            description,
            location,
            remote_field,
            job_level,
            job_function,
            f" {search_bucket} ",
            skills,
            company_industry,
        ]
    )

    score = 0
    reasons = []

    # Hard title exclusions
    for keyword in EXCLUDE_TITLE_KEYWORDS:
        if has_phrase(title, keyword):
            score -= 30
            reasons.append(f"exclude title: {keyword}")

    # Core title relevance
    for keyword in TITLE_CORE_MATCHES:
        if has_phrase(title, keyword):
            score += 8
            reasons.append(f"title core: {keyword}")

    # Therapeutic title relevance
    for keyword in TITLE_THERAPEUTIC_MATCHES:
        if has_phrase(title, keyword):
            score += 6
            reasons.append(f"title therapeutic: {keyword}")

    # Supporting content relevance, capped to avoid over-scoring long descriptions
    supporting_hits = []
    for keyword in SUPPORTING_CONTENT_MATCHES:
        if has_phrase(combined, keyword) and not has_phrase(title, keyword):
            supporting_hits.append(keyword)

    if supporting_hits:
        content_points = min(len(supporting_hits) * 1.5, 9)
        score += content_points
        reasons.append("supporting content: " + ", ".join(supporting_hits[:8]))

    # Search bucket is useful but should not rescue a bad title alone
    if search_bucket in GOOD_SEARCH_BUCKETS:
        score += 2
        reasons.append(f"search bucket: {search_bucket}")

    # Location / remote fit
    if "true" in remote_field or has_phrase(remote_field, "remote") or has_phrase(combined, "remote"):
        score += 2
        reasons.append("remote")

    if any(
        place in combined
        for place in [
            " california ",
            " los angeles ",
            " san diego ",
            " orange county ",
            " irvine ",
            " santa monica ",
            " pasadena ",
            " carlsbad ",
            " san francisco ",
            " redwood city ",
            " south san francisco ",
        ]
    ):
        score += 2
        reasons.append("california/socal")

    # Seniority modifiers
    if has_phrase(title, "associate director"):
        score += 4
        reasons.append("associate director level")

    elif has_phrase(title, "director"):
        score += 2
        reasons.append("director level")

    if has_any(title, ["manager", "lead", "consultant"]):
        score += 2
        reasons.append("reasonable seniority")

    if has_any(title, TOO_SENIOR_TERMS):
        score -= 8
        reasons.append("possibly too senior")

    if has_any(title, TOO_JUNIOR_TERMS):
        score -= 10
        reasons.append("too junior")

    # MSL therapeutic mismatch penalty
    is_msl = has_phrase(title, "medical science liaison") or has_phrase(title, "msl")
    if is_msl and has_any(combined, WRONG_MSL_AREAS):
        score -= 18
        reasons.append("MSL therapeutic area mismatch")

    # Oncology MSLs are possible but lower priority unless genomics/precision medicine is present
    if is_msl and has_phrase(combined, "oncology") and not has_any(combined, ["genomics", "precision medicine", "biomarker"]):
        score -= 8
        reasons.append("lower-priority oncology MSL")

    # Prevent broad descriptions from rescuing titles with no relevant title signal
    has_relevant_title_signal = has_any(title, TITLE_CORE_MATCHES) or has_any(title, TITLE_THERAPEUTIC_MATCHES)
    if not has_relevant_title_signal and score < 14:
        score -= 6
        reasons.append("weak title signal")

    return score, "; ".join(reasons)


def classify(score):
    if score >= 24:
        return "HIGH_PRIORITY"
    if score >= 12:
        return "REVIEW"
    return "EXCLUDED"


def main():
    parser = argparse.ArgumentParser(description="Pre-filter scraped job CSVs before Claude review.")
    parser.add_argument("input_csv", help="Path to scraped jobs CSV")
    args = parser.parse_args()

    input_path = Path(args.input_csv)

    if not input_path.exists():
        raise FileNotFoundError(f"Could not find input file: {input_path}")

    df = pd.read_csv(input_path)
    original_count = len(df)

    if "job_url" in df.columns:
        df = df.drop_duplicates(subset=["job_url"], keep="first")
    elif "Job URL" in df.columns:
        df = df.drop_duplicates(subset=["Job URL"], keep="first")
    else:
        possible_cols = [
            col
            for col in ["Job Title", "title", "Company Name", "company", "Location", "location"]
            if col in df.columns
        ]
        if possible_cols:
            df = df.drop_duplicates(subset=possible_cols, keep="first")
        else:
            df = df.drop_duplicates(keep="first")

    scores = df.apply(score_job, axis=1)
    df["Prefilter Score"] = [item[0] for item in scores]
    df["Prefilter Reasons"] = [item[1] for item in scores]
    df["Prefilter Category"] = df["Prefilter Score"].apply(classify)

    high_priority_df = df[df["Prefilter Category"] == "HIGH_PRIORITY"].sort_values(
        "Prefilter Score", ascending=False
    )

    review_df = df[df["Prefilter Category"].isin(["HIGH_PRIORITY", "REVIEW"])].sort_values(
        "Prefilter Score", ascending=False
    )

    excluded_df = df[df["Prefilter Category"] == "EXCLUDED"].sort_values(
        "Prefilter Score", ascending=True
    )

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    stem = input_path.stem
    high_priority_path = output_dir / f"{stem}_PREFILTER_HIGH_PRIORITY.csv"
    review_path = output_dir / f"{stem}_PREFILTER_REVIEW.csv"
    excluded_path = output_dir / f"{stem}_PREFILTER_EXCLUDED.csv"

    high_priority_df.to_csv(high_priority_path, index=False)
    review_df.to_csv(review_path, index=False)
    excluded_df.to_csv(excluded_path, index=False)

    print(f"Input jobs: {original_count}")
    print(f"After dedupe: {len(df)}")
    print(f"High priority jobs: {len(high_priority_df)}")
    print(f"Review jobs including high priority: {len(review_df)}")
    print(f"Excluded jobs: {len(excluded_df)}")
    print(f"Saved high priority file: {high_priority_path}")
    print(f"Saved review file: {review_path}")
    print(f"Saved excluded file: {excluded_path}")


if __name__ == "__main__":
    main()