# Job Hunt Agent

This repo supports my career-ops workflow for filtering job search results and updating Airtable.

## Structure

- `scrape_jobs.py` — scrapes broad job search results.
- `scrape_saved_job_links.py` — scrapes saved LinkedIn job links.
- `career-ops/SKILL.md` — instructions for Claude to filter jobs and update Airtable.
- `career-ops/profile.md` — my target role profile and preferences.
- `career-ops/filtering_rules.md` — inclusion/exclusion rules for job filtering.
- `career-ops/airtable_schema.md` — Airtable fields and update expectations.
- `career-ops/feedback_log.md` — user feedback Claude should use to improve future filtering.

## Workflow

1. Scrape jobs locally.
2. Give Claude the newest CSV from `outputs/`.
3. Claude filters jobs using the `career-ops` skill files.
4. Claude updates Airtable.
5. User gives feedback.
6. Claude updates `feedback_log.md`, `filtering_rules.md`, and/or `profile.md`.
