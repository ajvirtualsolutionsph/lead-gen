import sys
from datetime import date

from sheets import read_rows, TAB_NEW_LEADS, TAB_INITIAL_SENT, TAB_NEEDS_FOLLOWUP, TAB_NO_REPLY
from organize_sheets import days_since, NOREPLY_AGE_DAYS

SEP = "=" * 60


def main():
    try:
        new_leads = read_rows(TAB_NEW_LEADS)
        initial_sent = read_rows(TAB_INITIAL_SENT)
        needs_followup = read_rows(TAB_NEEDS_FOLLOWUP)
        no_reply = read_rows(TAB_NO_REPLY)
    except Exception as e:
        print(f"Error reading pipeline data: {e}")
        sys.exit(1)

    undrafted = [r for r in new_leads if r.get("status", "").strip() != "Drafted"]
    drafted_not_sent = [
        r for r in new_leads
        if r.get("status", "").strip() == "Drafted"
        and r.get("sent", "").strip() == ""
    ]
    aging_soon = [
        r for r in initial_sent
        if days_since(r.get("sent", "")) is not None
        and days_since(r.get("sent", "")) >= 4
    ]

    # Needs Follow Up: split by whether follow-up has been sent already
    followup_pending = [
        r for r in needs_followup
        if r.get("followup_sent", "").strip() in ("", "SKIPPED_NO_EMAIL")
        and r.get("sent", "").strip() not in ("", )
    ]
    followup_aging = [
        r for r in needs_followup
        if r.get("followup_sent", "").strip() not in ("", "SKIPPED_NO_EMAIL")
    ]

    today = date.today().strftime("%B %d, %Y")

    print(SEP)
    print(f"  LEAD GEN PIPELINE — STATUS REPORT")
    print(f"  {today}")
    print(SEP)

    print()
    print("[NEW LEADS]")
    print(f"  Total in tab         : {len(new_leads)}")
    if undrafted:
        print(f"  Undrafted            : {len(undrafted)}   <- run: python draft_agent.py")
    if drafted_not_sent:
        print(f"  Drafted, not sent    : {len(drafted_not_sent)}   <- run: python send_emails.py --initial")

    print()
    print("[INITIAL EMAIL SENT]")
    print(f"  Total in tab         : {len(initial_sent)}")
    if aging_soon:
        print(f"  Aging toward follow-up (4+ days old): {len(aging_soon)}")

    print()
    print("[NEEDS FOLLOW-UP]")
    print(f"  Total in tab         : {len(needs_followup)}")
    if followup_pending:
        print(f"  Follow-up not sent   : {len(followup_pending)}   <- run: python send_emails.py --followup")
    if followup_aging:
        days_info = []
        for r in followup_aging:
            age = days_since(r.get("followup_sent", ""))
            days_left = max(0, NOREPLY_AGE_DAYS - age) if age is not None else "?"
            days_info.append(days_left)
        moving_soon = sum(1 for d in days_info if d == 0)
        still_aging = len(days_info) - moving_soon
        if still_aging:
            print(f"  Aging (follow-up sent, waiting {NOREPLY_AGE_DAYS}d): {still_aging}   <- no action needed")
        if moving_soon:
            print(f"  Ready to archive     : {moving_soon}   <- run: python organize_sheets.py")

    print()
    print("[NO REPLY / DECLINED]")
    print(f"  Total in tab         : {len(no_reply)}")

    print()
    print(SEP)
    print("  NEXT ACTIONS")
    print(SEP)

    actions = []
    if undrafted:
        actions.append(f"  [ ] python draft_agent.py              — draft emails for {len(undrafted)} lead(s)")
    if drafted_not_sent:
        actions.append(f"  [ ] python send_emails.py --initial    — send to {len(drafted_not_sent)} drafted lead(s)")
    if followup_pending:
        actions.append(f"  [ ] python send_emails.py --followup   — send follow-ups to {len(followup_pending)} lead(s)")
    if any(d == 0 for d in [max(0, NOREPLY_AGE_DAYS - (days_since(r.get("followup_sent", "")) or 0)) for r in followup_aging]):
        actions.append(f"  [ ] python organize_sheets.py          — archive {sum(1 for r in followup_aging if (days_since(r.get('followup_sent','')) or 0) >= NOREPLY_AGE_DAYS)} lead(s) to No Reply/Declined")

    if actions:
        for line in actions:
            print(line)
    else:
        print("  All clear — nothing pending. Import new leads or check back later.")

    print(SEP)


if __name__ == "__main__":
    main()
