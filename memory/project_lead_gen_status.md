# Lead Gen Project — Session Status

## Pipeline State
Git repo active and pushed to GitHub. Pipeline tabs and lead data are in Google Sheets — run organize + status scripts to get current counts. 21 leads in Initial Email Sent as of last session.

## Last Actions Taken (2026-05-07)
- Changed git commit message format from "Session N:" to date-based `YYYY-MM-DD:` prefix
- Updated CLAUDE.md 123 workflow step 3 to enforce the new date format

## Next Priorities
1. Add new leads to Google Sheet, then type "draft email" → "send initial email"
2. Around May 11–12, type "send follow up" for the 21 leads in Initial Email Sent
3. Run `python organize_sheets.py` then `python status_report.py` at start of next session

## Notes
- Secrets never committed: .env, gmail_credentials.json, gmail_token.json
- 123 is the end-of-session save trigger — updates CLAUDE.md, this file, commits, and pushes
- Commit messages now use format: `YYYY-MM-DD: description`
