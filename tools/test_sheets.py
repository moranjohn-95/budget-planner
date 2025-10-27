import os
import json
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials


def load_scopes():
    s = os.environ.get("GOOGLE_SCOPES", "").strip()
    return [x.strip() for x in s.split(",") if x.strip()] or \
           ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def build_creds():
    scopes = load_scopes()
    path = os.environ.get("GOOGLE_CREDS_PATH")
    inline = os.environ.get("GOOGLE_CREDS_JSON")
    if path:
        return Credentials.from_service_account_file(path, scopes=scopes)
    if inline:
        return Credentials.from_service_account_info(json.loads(inline),
                                                     scopes=scopes)
    raise RuntimeError(
        "Missing GOOGLE_CREDS_PATH or GOOGLE_CREDS_JSON in .env"
    )


def main():
    load_dotenv()
    sheet_id = os.environ["SHEET_ID"]
    creds = build_creds()
    client = gspread.authorize(creds)

    sh = client.open_by_key(sheet_id)
    ws = sh.sheet1  # first tab
    first_row = ws.row_values(1)
    print("Connected to:", sh.title)
    print("Sheet1 row1:", first_row)

    # optional write test (comment out if using readonly scope)
    ws.append_row(["hello", "from", "test_sheets.py"],
                  value_input_option="USER_ENTERED")
    print("Append OK.")


if __name__ == "__main__":
    main()
