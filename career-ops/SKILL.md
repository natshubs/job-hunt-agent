# Career-Ops Skill

This Skill helps Natasha Anand manage her job-search pipeline.

## Purpose

Use this Skill to:

- Review scraped job CSVs.
- Filter jobs for relevance.
- Score jobs based on Natasha’s fit.
- Update Airtable.
- Identify jobs worth applying to.
- Identify jobs that should be excluded.
- Preserve gray-area jobs for human review.
- Learn from Natasha’s feedback and update future filtering behavior.

## Required Context Files

Before reviewing jobs, read:

1. profile.md
2. filtering_rules.md
3. airtable_schema.md
4. feedback_log.md

## Operating Principles

Do not make the job search overly narrow.

The scraper may collect broad results. Claude’s role is to sort, score, and prioritize them.

When uncertain, use “Needs Human Review” rather than excluding.

Do not exclude jobs simply because the title is unfamiliar. Exclude only when the job is clearly misaligned.

Do not apply to jobs automatically unless Natasha explicitly asks.

Do not delete Airtable records unless Natasha explicitly asks.

Do not fabricate job details. If a job description is missing, use the available title, company, location, and URL, and mark confidence accordingly.

## Job Review Workflow

When Natasha asks to review a scraped job file:

1. Open the most recent CSV in the outputs folder, unless she provides a specific file path.
2. Read the available fields.
3. Deduplicate by Job Title + Company + Location + URL.
4. Classify each job as:
   - Strong Match
   - Review
   - Needs Human Review
   - Excluded
5. Assign a Fit Score from 1–5.
6. Assign Priority:
   - High
   - Medium
   - Low
   - Exclude
7. Add a short reason for inclusion or exclusion.
8. Prepare Airtable-ready rows.
9. Update Airtable if Airtable access is available.
10. If Airtable access is not available, generate a clean CSV for Airtable import.

## Scoring Rules

5:
Excellent fit. Strong alignment with Natasha’s profile. Prioritize.

4:
Good fit. Worth applying or reviewing closely.

3:
Possible fit. Save for human review.

2:
Weak fit. Usually exclude unless there is a special reason.

1:
Clearly irrelevant. Exclude.

## Strong Match Criteria

Mark as Strong Match if the job aligns with several of these:

- Medical affairs
- Medical strategy
- Clinical development
- Clinical science
- Psychiatry / CNS / neuroscience
- Healthcare AI / digital health
- Genomics / precision medicine
- KOL engagement
- Evidence generation
- Scientific communications
- Medical education
- Clinical product strategy
- Cross-functional leadership
- MD preferred or accepted
- Remote or California-based

## Exclusion Criteria

Exclude if clearly:

- Chiropractor
- Physical therapy
- Nurse-only
- Pharmacist retail
- Dental
- Veterinary
- Pure health informatics
- Pure medical writing
- Pure regulatory affairs
- Pure sales
- Entry-level coordinator
- Clinical research assistant
- Lab technician
- VP / CMO / Head-level role that is clearly too senior
- Requires completed residency, board certification, or active attending status that Natasha does not have

## Feedback Learning

When Natasha gives feedback such as:

- “This is too senior.”
- “This therapeutic area is okay.”
- “Don’t include this type of job.”
- “This should have been a strong match.”
- “This is too narrow.”
- “This is irrelevant.”

Then:

1. Update feedback_log.md.
2. Convert the feedback into a reusable rule.
3. Apply that rule to future job reviews.
4. Mention the rule briefly when relevant.

## Output Format

When summarizing reviewed jobs, provide:

- Total jobs reviewed
- Number of Strong Matches
- Number for Review
- Number needing Human Review
- Number Excluded
- Top 10 jobs worth looking at
- Any patterns noticed
- Any recommended changes to scraper search terms

## Airtable Update Behavior

When updating Airtable:

- Do not create duplicates.
- Preserve existing statuses like Applied, Follow Up, Interview, Rejected, or Apply.
- Do not overwrite human notes unless asked.
- Add new notes below existing notes if needed.
- Use concise reason fields.
- Make excluded jobs searchable but low priority.
- Keep a clean record of why something was excluded.

## Search Term Adjustment Logic

Only suggest changes to scraper search terms if the scrape quality is poor.

Do not overcorrect based on one bad scrape.

If too many irrelevant jobs appear, suggest excluding terms rather than narrowing the main search too much.

Examples of useful exclusion terms:

- chiropractor
- physical therapist
- RN
- nurse
- pharmacist
- dentist
- veterinary
- billing
- coding
- medical assistant
- laboratory technician
- sales representative
- territory manager

Examples of useful inclusion terms:

- medical affairs
- medical strategy
- clinical development
- clinical scientist
- medical science liaison
- MSL
- neuroscience
- psychiatry
- CNS
- neuropsychiatry
- healthcare AI
- digital health
- clinical product
- precision medicine
- genomics
- evidence generation