from sheets import (
    _get_spreadsheet, LEADS_FIELDNAMES,
    TAB_NEW_LEADS, TAB_INITIAL_SENT, TAB_NEEDS_FOLLOWUP, TAB_NO_REPLY,
)

# Column widths in pixels for each field
COLUMN_WIDTHS = {
    "name": 160,
    "business_name": 160,
    "category": 110,
    "address": 180,
    "phone": 110,
    "website": 150,
    "email": 170,
    "rating": 70,
    "review_count": 70,
    "notes": 140,
    "details": 140,
    "subject": 160,
    "email_body": 120,
    "followup": 120,
    "date_drafted": 120,
    "sent": 120,
    "followup_sent": 120,
    "status": 90,
    "thread_id": 100,
    "message_id": 100,
    "aging_days": 80,
}

HEADER_BG = {"red": 0.909, "green": 0.918, "blue": 0.929}  # #E8EAED
FONT_SIZE = 10
ROW_HEIGHT = 21
HEADER_HEIGHT = 24


def _col_width_requests(sheet_id, headers):
    requests = []
    for idx, col in enumerate(headers):
        width = COLUMN_WIDTHS.get(col, 120)
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": idx,
                    "endIndex": idx + 1,
                },
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })
    return requests


def _row_height_requests(sheet_id, num_rows):
    requests = []
    # Header row height
    requests.append({
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "ROWS",
                "startIndex": 0,
                "endIndex": 1,
            },
            "properties": {"pixelSize": HEADER_HEIGHT},
            "fields": "pixelSize",
        }
    })
    # Data rows height
    if num_rows > 1:
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": 1,
                    "endIndex": max(num_rows, 2),
                },
                "properties": {"pixelSize": ROW_HEIGHT},
                "fields": "pixelSize",
            }
        })
    return requests


def _cell_format_requests(sheet_id, num_rows, num_cols):
    requests = []

    # All cells: font + clip wrapping
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": max(num_rows, 2),
                "startColumnIndex": 0,
                "endColumnIndex": num_cols,
            },
            "cell": {
                "userEnteredFormat": {
                    "textFormat": {"fontFamily": "Arial", "fontSize": FONT_SIZE},
                    "wrapStrategy": "CLIP",
                    "verticalAlignment": "MIDDLE",
                }
            },
            "fields": "userEnteredFormat(textFormat,wrapStrategy,verticalAlignment)",
        }
    })

    # Header row: bold + background color
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": 0,
                "endColumnIndex": num_cols,
            },
            "cell": {
                "userEnteredFormat": {
                    "textFormat": {"fontFamily": "Arial", "fontSize": FONT_SIZE, "bold": True},
                    "backgroundColor": HEADER_BG,
                    "wrapStrategy": "CLIP",
                    "verticalAlignment": "MIDDLE",
                }
            },
            "fields": "userEnteredFormat(textFormat,backgroundColor,wrapStrategy,verticalAlignment)",
        }
    })

    # Freeze header row
    requests.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {"frozenRowCount": 1},
            },
            "fields": "gridProperties.frozenRowCount",
        }
    })

    return requests


def format_all_tabs(spreadsheet=None):
    if spreadsheet is None:
        spreadsheet = _get_spreadsheet()

    tab_headers = {
        TAB_NEW_LEADS: LEADS_FIELDNAMES,
        TAB_INITIAL_SENT: LEADS_FIELDNAMES + ["aging_days"],
        TAB_NEEDS_FOLLOWUP: LEADS_FIELDNAMES + ["aging_days"],
        TAB_NO_REPLY: LEADS_FIELDNAMES + ["aging_days"],
    }

    for tab_name, headers in tab_headers.items():
        try:
            ws = spreadsheet.worksheet(tab_name)
        except Exception:
            continue

        sheet_id = ws.id
        num_rows = max(ws.row_count, 2)
        num_cols = len(headers)

        requests = (
            _col_width_requests(sheet_id, headers)
            + _row_height_requests(sheet_id, num_rows)
            + _cell_format_requests(sheet_id, num_rows, num_cols)
        )

        spreadsheet.batch_update({"requests": requests})
        print(f"[OK] Formatted: {tab_name}")


if __name__ == "__main__":
    format_all_tabs()
    print("Done.")
