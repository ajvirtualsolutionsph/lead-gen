import subprocess
import sys
import time

from organize_sheets import days_since
from sheets import (
    TAB_INITIAL_SENT, TAB_NEEDS_FOLLOWUP,
    read_rows, move_rows_between_tabs, _get_spreadsheet,
)

OLD_NO_REPLY_TAB = "No Reply/Declined"
NEW_NO_REPLY_TAB = "Ready for Call"

STEP_PAUSE = 10  # seconds between steps to avoid 429 quota errors


def main():
    # Step 1: Move 3+ day Initial Email Sent leads → Needs Follow Up
    print("--- Step 1: Moving 3-day-old leads to Needs Follow Up ---")
    initial_rows = read_rows(TAB_INITIAL_SENT)
    to_followup = [
        r for r in initial_rows
        if r.get("sent") not in ("", "SKIPPED_NO_EMAIL")
        and r.get("followup", "").strip()
        and not r.get("followup_sent", "").strip()
        and isinstance(days_since(r.get("sent", "")), int)
        and days_since(r["sent"]) >= 3
    ]
    if to_followup:
        move_rows_between_tabs(to_followup, TAB_INITIAL_SENT, TAB_NEEDS_FOLLOWUP)
        print(f"  Moved {len(to_followup)} lead(s) to Needs Follow Up")
        for r in to_followup:
            print(f"    - {r.get('business_name', '?')} ({days_since(r.get('sent',''))}d old)")
    else:
        print("  No leads aged 3+ days in Initial Email Sent")
    print(f"  Waiting {STEP_PAUSE}s...")
    time.sleep(STEP_PAUSE)

    # Step 2: Send follow-up emails to newly eligible leads
    print("\n--- Step 2: Sending follow-up emails ---")
    subprocess.run([sys.executable, "send_emails.py", "--followup", "--yes"])
    print(f"  Waiting {STEP_PAUSE}s for quota to clear...")
    time.sleep(STEP_PAUSE)

    # Step 3: Move ALL remaining Needs Follow Up → No Reply/Declined
    print("\n--- Step 3: Moving all Needs Follow Up → No Reply/Declined ---")
    followup_rows = read_rows(TAB_NEEDS_FOLLOWUP)
    if followup_rows:
        move_rows_between_tabs(followup_rows, TAB_NEEDS_FOLLOWUP, OLD_NO_REPLY_TAB)
        print(f"  Moved {len(followup_rows)} lead(s) to {OLD_NO_REPLY_TAB}")
    else:
        print("  Needs Follow Up is already empty")
    print(f"  Waiting {STEP_PAUSE}s...")
    time.sleep(STEP_PAUSE)

    # Step 4: Rename "No Reply/Declined" → "Ready for Call"
    print(f"\n--- Step 4: Renaming tab '{OLD_NO_REPLY_TAB}' → '{NEW_NO_REPLY_TAB}' ---")
    spreadsheet = _get_spreadsheet()
    ws = spreadsheet.worksheet(OLD_NO_REPLY_TAB)
    ws.update_title(NEW_NO_REPLY_TAB)
    print(f"  Tab renamed successfully")

    print("\n[DONE] Session override complete.")
    print("  Run: python status_report.py  — to verify final state")


if __name__ == "__main__":
    main()
