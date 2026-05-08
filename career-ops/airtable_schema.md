# Airtable Schema for Career-Ops

Claude should update Airtable using the following fields.

## Core Fields

- Job Title
- Company
- Location
- Remote / Hybrid / In-person
- Job URL
- Source
- Date Found
- Date Updated
- Status
- Fit Score
- Priority
- Therapeutic Area
- Function
- Role Level
- Compensation, if available
- Application Deadline, if available
- Notes
- Reason for Inclusion
- Reason for Exclusion
- Resume Version Used
- Cover Letter Needed
- Follow-Up Needed
- Contact / Recruiter
- Hiring Manager
- Feedback

## Status Definitions

New:
A job has been added but not reviewed.

Review:
The job may be relevant and needs review.

Strong Match:
The job is highly aligned and should be prioritized.

Apply:
Natasha should apply.

Applied:
Application has been submitted.

Follow Up:
Application, recruiter message, or hiring contact requires follow-up.

Interview:
Interview or recruiter screen has been scheduled.

Rejected:
The company rejected the application.

Excluded:
The job is not a fit.

Needs Human Review:
Claude is uncertain and Natasha should decide.

## Priority Definitions

High:
Strong match, likely worth applying soon.

Medium:
Reasonable fit, but not urgent.

Low:
Weak or uncertain fit.

Exclude:
Clearly not appropriate.

## Deduplication Rules

Before adding a job, check whether the same company + job title + location + URL already exists.

If a duplicate exists:

- Do not create a new record.
- Update missing fields if needed.
- Add a note if the job appeared again in a new scrape.
- Do not overwrite human-edited statuses such as Applied, Follow Up, Interview, Rejected, or Apply.