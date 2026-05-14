---
name: project-lead-gen-status
description: Current pipeline state, last actions, and next priorities for the Lead Gen project
metadata:
  type: project
---

## Pipeline State (2026-05-14)

| Tab | Count |
|---|---|
| New Leads | 0 — empty, needs new imports |
| Initial Email Sent | 30 |
| Needs Follow Up | 5 (follow-up already sent, aging out ~May 16) |
| No Reply/Declined | 75 |
| **Total** | **110** |

## Last Actions Taken (2026-05-14)

- Ran full project audit — pipeline state, code quality, security
- Fixed `gspread.authorize()` → `gspread.Client(auth=creds)` in `sheets.py`
- Added `time.sleep(1)` between API phases in `organize_sheets.py` to prevent 429 quota errors
- Wired `email_finder.py` into `draft_agent.py`: auto-crawls website for missing email before drafting

## Next Priorities

1. Import new leads into New Leads tab, then type `draft email`
2. Around May 16, run `python organize_sheets.py` to archive the 5 follow-ups to No Reply
3. After archiving, pipeline needs a fresh batch to stay active

## Notes

- Secrets never committed: `.env`, `gmail_credentials.json`, `gmail_token.json`
- `123` is the end-of-session save trigger
- Commit messages use format: `YYYY-MM-DD: description`
- `email_finder.py` now runs automatically in `draft_agent.py` for leads with a website but no email
