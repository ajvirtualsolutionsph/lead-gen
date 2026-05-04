# CLAUDE.md

## When the User Types "123" (End-of-Session Save)

Run this sequence in order, without asking:

1. **Update CLAUDE.md** — Rewrite the `### ✅ Done` and `### 🔲 Next Session` sections based on what was accomplished this session.
2. **Update memory file** — Rewrite `memory/project_lead_gen_status.md` with current pipeline state, last actions taken, and next priorities.
3. **Commit + push** — Stage all changed files, commit with a clear message describing what was done, and push to `origin/main`.
4. **Chat report** — Reply with a summary covering: what files were updated, what was committed, and what the next priority is.

This is the end-of-session save trigger. Execute all four steps every time "123" is typed.

### ✅ Done

- Set up 123 end-of-session save workflow in CLAUDE.md
- Initialized git repo, connected to GitHub remote, made initial commit
- Re-authenticated Google OAuth (deleted expired `gmail_token.json`)
- Drafted emails for 3 new leads (Just In Time Plumbing, The Smile Center, Dentistry of Virginia Beach)
- Sent 4 initial emails (Olivia, Just In Time Plumbing, The Smile Center, Dentistry of Virginia Beach)
- Updated `draft_agent.py` system prompt:
  - Pricing corrected to $2,000–$2,500 (was $1,500–$2,000)
  - Added AI Executive Assistant as a named, priority package (Notion + Claude)
  - Primary focus rule: lead with AI Executive Assistant or AI Marketing Agent
  - Updated package routing rules and salary comparison range
  - Updated retainer pricing to match website (30%/25%/20%)
- 12 follow-ups in Needs Follow Up tab still pending (hit Google Sheets rate limit — run manually)

### 🔲 Next Session

- Run `python send_emails.py --followup` to send 12 pending follow-ups (wait 2–3 min after starting terminal before running)
- Run `python organize_sheets.py` + `python status_report.py` to check pipeline state
- Add new leads to Google Sheets then run `python draft_agent.py`

---

## When the User Says "Run the Project"

Always run this sequence first, before responding or asking anything:

1. `python organize_sheets.py`
2. `python status_report.py`
3. Show full output of both scripts
4. Ask: "What would you like to do next?"

The report is only accurate after step 1. Show raw output before commentary.

---

## Commands

```bash
python draft_agent.py          # Draft emails for new leads
python send_emails.py          # Send initial + follow-ups (run from Windows Terminal)
python send_emails.py --initial
python send_emails.py --followup
python organize_sheets.py      # Refresh tabs (run after any send)
python status_report.py        # Show pipeline state
pip install -r requirements.txt
```

---

## Pipeline

Full lifecycle: **add leads → draft → send initial → 5 days → follow-up → 2 days → no reply**

| Tab | Rule |
|---|---|
| **New Leads** | `sent` is empty |
| **Initial Email Sent** | `sent` filled, no other tab applies |
| **Needs Follow Up** | `sent` filled, 5+ days old, follow-up drafted, `followup_sent` empty |
| **No Reply/Declined** | `followup_sent` filled, 2+ days passed |

Priority order: No Reply/Declined → Needs Follow Up → Initial Email Sent → New Leads.

Sheet: https://docs.google.com/spreadsheets/d/1Zq7muXisE8QywVGXtRE6OqyDRl84UKWy37HoorjxO3s

Fill in: `name`, `business_name`, `category`, `address`, `phone`, `website`, `email`, `rating`, `review_count`, `notes`, `details` — leave all other columns blank.

---

## Architecture

**`draft_agent.py`** — reads rows where `status != "drafted"`, calls Claude (`claude-sonnet-4-6`), parses `SUBJECT:` / `EMAIL:` / `FOLLOWUP:` from response, writes back with `status = "drafted"`.

**`send_emails.py`** — sends initial emails (`sent` empty) and follow-ups (`sent` filled, `followup_sent` empty). Saves `thread_id` + `message_id` for Gmail threading. No email → sets `sent`/`followup_sent` to `SKIPPED_NO_EMAIL`.

**`sheets.py`** — central read/write module. Sheet ID in `.env` as `GOOGLE_SHEET_ID`.

**Threading** — follow-ups sent as Gmail thread replies via `threadId` + `In-Reply-To`/`References` headers. Leads without `thread_id` send as new threads.

**Email rendering** — plain text → HTML, URLs auto-linkified, Gmail signature appended, subject title-cased.

### Gmail OAuth
- `gmail_credentials.json` — from Google Cloud Console
- `gmail_token.json` — auto-generated; delete to force re-auth
- Scopes: `gmail.send`, `gmail.readonly`, `gmail.settings.basic`, `spreadsheets`, `drive.file`

### `.env` keys
- `ANTHROPIC_API_KEY`, `GMAIL_ADDRESS`, `GOOGLE_SHEET_ID`

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Gmail auth popup doesn't appear | Delete `gmail_token.json`, re-run |
| "Scopes have changed" error | Delete `gmail_token.json`, re-run |
| Module not found | `pip install -r requirements.txt` |
| Draft agent fails | Check `ANTHROPIC_API_KEY` in `.env` |
| Sheet not found | Check `GOOGLE_SHEET_ID` in `.env` |

---

## File Reference

| File | Purpose |
|---|---|
| `draft_agent.py` | Draft emails via Claude AI |
| `send_emails.py` | Send emails and follow-ups via Gmail |
| `organize_sheets.py` | Move leads between tabs |
| `status_report.py` | Pipeline counts and next actions |
| `sheets.py` | Google Sheets read/write (don't edit) |
| `format_sheets.py` | Visual tab formatting (don't edit) |
| `email_finder.py` | Email crawler (don't edit) |
| `.env` | API keys — never share |
| `gmail_credentials.json` | OAuth credentials — never share |
| `gmail_token.json` | Auth token — safe to delete |
| `signature.html` | Gmail signature appended to all emails |
