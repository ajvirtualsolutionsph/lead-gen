import os
import time
from datetime import datetime, date

import gspread
from dotenv import load_dotenv

from sheets import (
    get_creds, LEADS_FIELDNAMES,
    TAB_NEW_LEADS, TAB_INITIAL_SENT, TAB_NEEDS_FOLLOWUP, TAB_NO_REPLY, ALL_TABS,
    read_rows, write_rows, move_rows_between_tabs, _get_spreadsheet,
)
from format_sheets import format_all_tabs

load_dotenv()

FOLLOWUP_AGE_DAYS = 5
NOREPLY_AGE_DAYS = 2
FIELDNAMES_WITH_AGING = LEADS_FIELDNAMES + ["aging_days"]


def parse_date(date_str):
    for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def days_since(date_str):
    d = parse_date(date_str)
    if d is None:
        return None
    return (date.today() - d).days


def add_aging(row):
    if row.get("followup_sent") not in ("", "SKIPPED_NO_EMAIL"):
        age = days_since(row["followup_sent"])
    elif row.get("sent") not in ("", "SKIPPED_NO_EMAIL"):
        age = days_since(row["sent"])
    else:
        age = None
    row["aging_days"] = age if age is not None else ""
    return row


def write_tab_with_aging(spreadsheet, tab_name, rows):
    try:
        ws = spreadsheet.worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=len(FIELDNAMES_WITH_AGING))

    existing_headers = ws.row_values(1)
    extra_cols = [h for h in existing_headers if h not in FIELDNAMES_WITH_AGING]
    all_cols = FIELDNAMES_WITH_AGING + extra_cols

    rows_with_aging = [add_aging(dict(r)) for r in rows]
    data = [all_cols]
    for row in rows_with_aging:
        data.append([row.get(col, "") for col in all_cols])
    ws.clear()
    ws.update(data, value_input_option="RAW")
    return len(rows)


def lead_key(r):
    return (r.get("business_name", "").lower().strip(), r.get("address", "").lower().strip())


def main():
    spreadsheet = _get_spreadsheet()

    # --- Move rows from Needs Follow Up → No Reply/Declined ---
    followup_rows = read_rows(TAB_NEEDS_FOLLOWUP)
    to_no_reply = [
        r for r in followup_rows
        if r.get("followup_sent") not in ("", "SKIPPED_NO_EMAIL")
        and isinstance(days_since(r.get("followup_sent", "")), int)
        and days_since(r["followup_sent"]) >= NOREPLY_AGE_DAYS
    ]
    if to_no_reply:
        move_rows_between_tabs(to_no_reply, TAB_NEEDS_FOLLOWUP, TAB_NO_REPLY)
    time.sleep(1)

    # --- Move rows from Initial Email Sent → Needs Follow Up ---
    initial_rows = read_rows(TAB_INITIAL_SENT)
    to_followup = [
        r for r in initial_rows
        if r.get("sent") not in ("", "SKIPPED_NO_EMAIL")
        and r.get("followup", "").strip()
        and not r.get("followup_sent", "").strip()
        and isinstance(days_since(r.get("sent", "")), int)
        and days_since(r["sent"]) >= FOLLOWUP_AGE_DAYS
    ]
    if to_followup:
        move_rows_between_tabs(to_followup, TAB_INITIAL_SENT, TAB_NEEDS_FOLLOWUP)
    time.sleep(1)

    # --- Move rows from New Leads → Initial Email Sent ---
    new_rows = read_rows(TAB_NEW_LEADS)
    to_initial = [
        r for r in new_rows
        if r.get("sent") not in ("", "SKIPPED_NO_EMAIL") and r.get("sent", "").strip()
    ]
    if to_initial:
        # Check if any of these also immediately qualify for Needs Follow Up
        directly_to_followup = [
            r for r in to_initial
            if r.get("followup", "").strip()
            and not r.get("followup_sent", "").strip()
            and isinstance(days_since(r.get("sent", "")), int)
            and days_since(r["sent"]) >= FOLLOWUP_AGE_DAYS
        ]
        directly_to_followup_keys = {lead_key(r) for r in directly_to_followup}
        go_to_initial = [r for r in to_initial if lead_key(r) not in directly_to_followup_keys]

        if go_to_initial:
            move_rows_between_tabs(go_to_initial, TAB_NEW_LEADS, TAB_INITIAL_SENT)
        if directly_to_followup:
            move_rows_between_tabs(directly_to_followup, TAB_NEW_LEADS, TAB_NEEDS_FOLLOWUP)
    time.sleep(1)

    # --- Refresh aging_days display on static tabs (in-place rewrite) ---
    for tab_name in [TAB_INITIAL_SENT, TAB_NEEDS_FOLLOWUP, TAB_NO_REPLY]:
        rows = read_rows(tab_name)
        n = write_tab_with_aging(spreadsheet, tab_name, rows)
        print(f"[OK] {tab_name}: {n} rows")

    new_count = len(read_rows(TAB_NEW_LEADS))
    print(f"[OK] {TAB_NEW_LEADS}: {new_count} rows")

    format_all_tabs(spreadsheet)
    print("[OK] Sheet formatting applied")


if __name__ == "__main__":
    main()
