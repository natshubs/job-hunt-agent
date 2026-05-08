# Career Ops Automation Plan

Goal: minimize manual work while limiting Claude token usage.

## Division of labor

Python should handle:
- Deduplication
- Obvious exclusions
- Basic scoring
- CSV cleanup
- Airtable-ready formatting

Claude should handle:
- Nuanced fit review
- Borderline job decisions
- Feedback interpretation
- Updating filtering rules/profile/feedback log
- Final Airtable update recommendations

## Target workflow

1. Scrape broad job results locally.
2. Python creates:
   - ALL jobs
   - EXCLUDED jobs
   - REVIEW jobs
   - HIGH_PRIORITY jobs
3. User gives Claude only REVIEW/HIGH_PRIORITY files.
4. Claude filters using career-ops skill.
5. Claude updates Airtable or produces Airtable-ready rows.
6. User gives feedback.
7. Claude updates feedback_log.md and filtering_rules.md.
