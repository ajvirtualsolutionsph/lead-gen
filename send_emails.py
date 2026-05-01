import base64
import html
import os
import re
from datetime import datetime
from email.mime.text import MIMEText

from dotenv import load_dotenv
from googleapiclient.discovery import build

from sheets import read_rows, write_rows, get_creds, TAB_NEW_LEADS, TAB_NEEDS_FOLLOWUP

load_dotenv()

_MINOR = {"a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "by", "in", "of", "up"}


def title_case(s):
    words = s.split()
    return " ".join(
        w.capitalize() if i == 0 or w.lower() not in _MINOR else w.lower()
        for i, w in enumerate(words)
    )


def linkify(text):
    url_pattern = re.compile(r'(https?://[^\s]+|[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)')
    def replace(m):
        url = m.group(0)
        href = url if url.startswith("http") else f"https://{url}"
        return f'<a href="{href}">{url}</a>'
    return url_pattern.sub(replace, text)


def text_to_html(text):
    escaped = html.escape(text)
    linked = linkify(escaped)
    paragraphs = linked.split("\n\n")
    return "".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paragraphs)


def get_gmail_service():
    creds = get_creds()
    if not creds:
        return None
    return build("gmail", "v1", credentials=creds)


SIGNATURE_FILE = "signature.html"


def get_gmail_signature(service, user_email):
    if os.path.exists(SIGNATURE_FILE):
        with open(SIGNATURE_FILE, encoding="utf-8") as f:
            return f.read().strip()
    try:
        result = service.users().settings().sendAs().get(
            userId="me", sendAsEmail=user_email
        ).execute()
        return result.get("signature", "")
    except Exception:
        return ""


def create_message(to, subject, body_html):
    msg = MIMEText(body_html, "html")
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def get_message_id_header(service, msg_id):
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="metadata", metadataHeaders=["Message-ID"]
    ).execute()
    for h in msg["payload"]["headers"]:
        if h["name"] == "Message-ID":
            return h["value"]
    return ""


def send_message(service, message):
    result = service.users().messages().send(userId="me", body=message).execute()
    return result


def create_reply_message(to, subject, body_html, thread_id, in_reply_to):
    msg = MIMEText(body_html, "html")
    msg["to"] = to
    msg["subject"] = "Re: " + subject
    msg["In-Reply-To"] = in_reply_to
    msg["References"] = in_reply_to
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw, "threadId": thread_id}


def send_batch(rows, fieldnames, service, signature_html, subject_col, body_col, sent_col, label):
    pending = [
        r for r in rows
        if r.get("status", "").strip() == "drafted"
        and r.get(subject_col, "").strip()
        and not r.get(sent_col, "").strip()
    ]

    print(f"{len(pending)} {label} email(s) ready to send.\n")

    if not pending:
        return 0

    if sent_col not in fieldnames:
        fieldnames.append(sent_col)
        for row in rows:
            row.setdefault(sent_col, "")

    # Show all drafts first
    for i, row in enumerate(pending, 1):
        name = row.get("name", "").strip()
        business = row.get("business_name", "").strip()
        to_email = row.get("email", "").strip()
        subject = title_case(row.get(subject_col, "").strip())
        body = row.get(body_col, "").strip()

        print(f"  [{i}/{len(pending)}] {name} — {business} <{to_email}>")
        print(f"  Subject: {subject}")
        print(f"  Body:")
        for line in body.split("\n"):
            print(f"    {line}")
        print()

    # Single confirmation for the whole batch
    choice = input(f"  Send all {len(pending)} {label} email(s)? (y = send all / n = cancel): ").strip().lower()
    if choice != "y":
        print(f"  {label.capitalize()} emails cancelled.\n")
        return 0

    # Re-read the sheet to catch any rows already sent (e.g. duplicate run after token expiry)
    if sent_col in ("sent", "followup_sent"):
        from sheets import read_rows as _read_rows, TAB_NEEDS_FOLLOWUP as _TAB_FU, TAB_NEW_LEADS as _TAB_NL
        _tab = _TAB_NL if sent_col == "sent" else _TAB_FU
        fresh = {
            (r.get("business_name", "").lower().strip(), r.get("address", "").lower().strip()):
            r.get(sent_col, "").strip()
            for r in _read_rows(_tab)
        }
        already_sent = []
        safe_pending = []
        for row in pending:
            key = (row.get("business_name", "").lower().strip(), row.get("address", "").lower().strip())
            if fresh.get(key, ""):
                already_sent.append(row.get("business_name", row.get("name", "?")))
            else:
                safe_pending.append(row)
        if already_sent:
            print(f"  [!] Skipping {len(already_sent)} already-sent follow-up(s): {', '.join(already_sent)}")
        pending = safe_pending
        if not pending:
            print("  All follow-ups already sent. Nothing to do.\n")
            return 0

    sent_count = 0
    for row in pending:
        to_email = row.get("email", "").strip()
        subject = title_case(row.get(subject_col, "").strip())
        body = row.get(body_col, "").strip()
        name = row.get("name", "").strip()

        if not to_email:
            print(f"  [!] Skipping {name} — no email address.")
            row[sent_col] = "SKIPPED_NO_EMAIL"
            continue

        html_body = text_to_html(body)
        if signature_html:
            html_body += "<br><br>" + signature_html

        try:
            thread_id = row.get("thread_id", "").strip()
            in_reply_to = row.get("message_id", "").strip()
            if sent_col == "followup_sent" and thread_id:
                msg = create_reply_message(to_email, subject, html_body, thread_id, in_reply_to)
            else:
                msg = create_message(to_email, subject, html_body)
            result = send_message(service, msg)
            row[sent_col] = datetime.now().strftime("%Y-%m-%d %H:%M")
            if sent_col == "sent":
                row["thread_id"] = result.get("threadId", "")
                try:
                    row["message_id"] = get_message_id_header(service, result["id"])
                except Exception as e:
                    print(f"  [!] Sent but failed to fetch Message-ID for {name}: {e}")
                    row["message_id"] = ""
            sent_count += 1
            print(f"  Sent: {name} <{to_email}>")
        except Exception as e:
            print(f"  [!] Failed to send to {to_email}: {e}")

    print()
    return sent_count


def run(mode="both"):
    """
    mode: "initial"  — send initial emails only (reads New Leads tab)
          "followup" — send follow-up emails only (reads Needs Follow Up tab)
          "both"     — send initial first, then prompt for follow-ups
    """
    service = get_gmail_service()
    if not service:
        return

    user_email = os.getenv("GMAIL_ADDRESS", "").strip()
    if not user_email:
        print("[!] Add GMAIL_ADDRESS=your@gmail.com to your .env file to use your Gmail signature.")
    signature_html = get_gmail_signature(service, user_email) if user_email else ""
    if signature_html:
        print(f"[OK] Gmail signature loaded.\n")

    initial_sent = 0
    followup_sent = 0

    if mode in ("initial", "both"):
        rows = read_rows(TAB_NEW_LEADS)
        if not rows:
            print("No leads found in New Leads tab.")
        else:
            fieldnames = list(rows[0].keys())
            for col in ("sent", "followup_sent", "thread_id", "message_id"):
                if col not in fieldnames:
                    fieldnames.append(col)
                    for row in rows:
                        row[col] = ""
            initial_sent = send_batch(
                rows, fieldnames, service, signature_html,
                subject_col="subject", body_col="email_body", sent_col="sent",
                label="initial"
            )
            write_rows(rows, TAB_NEW_LEADS, fieldnames=fieldnames)

    if mode in ("followup", "both"):
        if mode == "both":
            followup_rows = read_rows(TAB_NEEDS_FOLLOWUP)
            if followup_rows:
                print(f"\n{'='*60}")
                print(f"  {len(followup_rows)} follow-up(s) are ready to send.")
                print(f"  These are SEPARATE from the initial emails above.")
                print(f"{'='*60}")
                gate = input(f"\n  Review and send follow-ups now? (y = yes / n = skip): ").strip().lower()
                if gate != "y":
                    print("  Follow-ups skipped. Run: python send_emails.py --followup\n")
                    print(f"\nDone. {initial_sent} initial email(s) sent. Google Sheets updated.")
                    _run_organize()
                    return
        else:
            followup_rows = read_rows(TAB_NEEDS_FOLLOWUP)

        if followup_rows:
            fieldnames_fu = list(followup_rows[0].keys())
            for col in ("sent", "followup_sent", "thread_id", "message_id"):
                if col not in fieldnames_fu:
                    fieldnames_fu.append(col)
                    for row in followup_rows:
                        row[col] = ""
            followup_sent = send_batch(
                followup_rows, fieldnames_fu, service, signature_html,
                subject_col="subject", body_col="followup", sent_col="followup_sent",
                label="follow-up"
            )
            write_rows(followup_rows, TAB_NEEDS_FOLLOWUP, fieldnames=fieldnames_fu)

    if mode == "initial":
        print(f"\nDone. {initial_sent} initial email(s) sent. Google Sheets updated.")
    elif mode == "followup":
        print(f"\nDone. {followup_sent} follow-up email(s) sent. Google Sheets updated.")
    else:
        print(f"\nDone. {initial_sent} initial + {followup_sent} follow-up email(s) sent. Google Sheets updated.")

    _run_organize()


def _run_organize():
    import organize_sheets
    print("\nRefreshing tabs...")
    organize_sheets.main()


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if "--initial" in args:
        run(mode="initial")
    elif "--followup" in args:
        run(mode="followup")
    else:
        run(mode="both")
