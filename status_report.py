import sys
from datetime import date

from sheets import read_rows, TAB_NEW_LEADS, TAB_INITIAL_SENT, TAB_NEEDS_FOLLOWUP, TAB_NO_REPLY
from organize_sheets import days_since

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

    undrafted = [r for r in new_leads if r.get("status", "").strip() != "drafted"]
    drafted_not_sent = [
        r for r in new_leads
        if r.get("status", "").strip() == "drafted"
        and r.get("sent", "").strip() == ""
    ]
    aging_soon = [
        r for r in initial_sent
        if days_since(r.get("sent", "")) is not None
        and days_since(r.get("sent", "")) >= 4
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
    if needs_followup:
        print(f"  Total in tab         : {len(needs_followup)}   <- run: python send_emails.py --followup")
    else:
        print(f"  Total in tab         : 0")

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
    if needs_followup:
        actions.append(f"  [ ] python send_emails.py --followup   — send follow-ups to {len(needs_followup)} lead(s)")

    if actions:
        for line in actions:
            print(line)
    else:
        print("  All clear — nothing pending. Import new leads or check back later.")

    print(SEP)


if __name__ == "__main__":
    main()
