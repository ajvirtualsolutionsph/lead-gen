import os

import gspread
from dotenv import load_dotenv, set_key
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

CREDENTIALS_FILE = "gmail_credentials.json"
TOKEN_FILE = "gmail_token.json"
SHEET_NAME = "Lead Gen Pipeline"
ENV_FILE = ".env"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.settings.basic",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

LEADS_FIELDNAMES = [
    "name", "business_name", "category", "address", "phone", "website", "email",
    "operating_hours", "rating", "review_count", "notes", "details",
    "subject", "email_body", "followup",
    "date_drafted", "sent", "followup_sent", "status", "thread_id",
]

TAB_NEW_LEADS = "New Leads"
TAB_INITIAL_SENT = "Initial Email Sent"
TAB_NEEDS_FOLLOWUP = "Needs Follow Up"
TAB_NO_REPLY = "Ready for Call"
ALL_TABS = [TAB_NEW_LEADS, TAB_INITIAL_SENT, TAB_NEEDS_FOLLOWUP, TAB_NO_REPLY]


def get_creds():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"'{CREDENTIALS_FILE}' not found. Download it from Google Cloud Console → "
                    "APIs & Services → Credentials → OAuth 2.0 Client IDs → Download JSON, "
                    f"then save it as '{CREDENTIALS_FILE}' in this folder."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def _get_spreadsheet():
    creds = get_creds()
    gc = gspread.Client(auth=creds)
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()
    if sheet_id:
        return gc.open_by_key(sheet_id)
    spreadsheet = gc.create(SHEET_NAME)
    spreadsheet.share(os.getenv("GMAIL_ADDRESS", ""), perm_type="user", role="writer")
    sheet_id = spreadsheet.id
    set_key(ENV_FILE, "GOOGLE_SHEET_ID", sheet_id)
    print(f"[OK] Created Google Sheet: {SHEET_NAME}")
    print(f"    URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
    print(f"    Sheet ID saved to .env\n")
    return spreadsheet


def get_worksheet(tab_name):
    spreadsheet = _get_spreadsheet()
    try:
        ws = spreadsheet.worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=len(LEADS_FIELDNAMES))
    current_headers = ws.row_values(1)
    if not current_headers:
        ws.append_row(LEADS_FIELDNAMES)
    else:
        missing = [col for col in LEADS_FIELDNAMES if col not in current_headers]
        if missing:
            new_headers = current_headers + missing
            ws.update([new_headers], range_name="1:1", value_input_option="RAW")
    return ws


def read_rows(tab_name=TAB_NEW_LEADS):
    ws = get_worksheet(tab_name)
    actual_headers = ws.row_values(1)
    records = ws.get_all_records(default_blank="", expected_headers=actual_headers)
    for row in records:
        row.pop("aging_days", None)
        for col in LEADS_FIELDNAMES:
            row.setdefault(col, "")
    return records


def write_rows(rows, tab_name=TAB_NEW_LEADS, fieldnames=None):
    ws = get_worksheet(tab_name)
    cols = fieldnames or LEADS_FIELDNAMES

    current_headers = ws.row_values(1)
    for col in cols:
        if col not in current_headers:
            current_headers.append(col)

    all_data = [current_headers]
    for row in rows:
        all_data.append([row.get(col, "") for col in current_headers])

    ws.clear()
    ws.update(all_data, value_input_option="RAW")


def read_all_rows():
    """Read from all 4 tabs combined (used for deduplication)."""
    all_rows = []
    spreadsheet = _get_spreadsheet()
    for tab in ALL_TABS:
        try:
            ws = spreadsheet.worksheet(tab)
            actual_headers = ws.row_values(1)
            records = ws.get_all_records(default_blank="", expected_headers=actual_headers)
            for row in records:
                row.pop("aging_days", None)
                for col in LEADS_FIELDNAMES:
                    row.setdefault(col, "")
            all_rows.extend(records)
        except gspread.exceptions.WorksheetNotFound:
            pass
    return all_rows


def move_rows_between_tabs(rows_to_move, from_tab, to_tab):
    """Remove rows_to_move from from_tab and append them to to_tab."""
    if not rows_to_move:
        return

    move_keys = {
        (r.get("business_name", "").lower().strip(), r.get("address", "").lower().strip())
        for r in rows_to_move
    }

    current = read_rows(from_tab)
    remaining = [r for r in current if (r.get("business_name", "").lower().strip(), r.get("address", "").lower().strip()) not in move_keys]
    write_rows(remaining, from_tab)

    ws_to = get_worksheet(to_tab)
    headers = ws_to.row_values(1) or LEADS_FIELDNAMES
    for row in rows_to_move:
        def _safe(v):
            import math
            if isinstance(v, float) and (math.isinf(v) or math.isnan(v)):
                return ""
            return v
        ws_to.append_row([_safe(row.get(col, "")) for col in headers], value_input_option="RAW")


def append_new_rows(new_rows):
    """Append only net-new leads to New Leads tab, deduplicating across all 4 tabs.

    Returns (added, skipped) counts.
    """
    existing = read_all_rows()
    existing_keys = {
        (r.get("business_name", "").lower().strip(), r.get("address", "").lower().strip())
        for r in existing
    }

    to_add = []
    skipped = 0
    for row in new_rows:
        key = (row.get("business_name", "").lower().strip(), row.get("address", "").lower().strip())
        if key in existing_keys:
            skipped += 1
        else:
            existing_keys.add(key)
            to_add.append(row)

    if to_add:
        ws = get_worksheet(TAB_NEW_LEADS)
        headers = ws.row_values(1) or LEADS_FIELDNAMES
        for row in to_add:
            ws.append_row([row.get(col, "") for col in headers], value_input_option="RAW")

    return len(to_add), skipped
