"""
sheets_gateway.py
-----------------
1. build Google credentials, 2. create a gspread client,
and 3. open the targeted spreadsheet by ID.
"""

from __future__ import annotations

import json
import os
from typing import List, Optional

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials


DEFAULT_SCOPES: List[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


def _scopes_from_env() -> List[str]:
    """
    Return scopes from GOOGLE_SCOPES (comma-separated) or DEFAULT_SCOPES.
    """
    raw = os.getenv("GOOGLE_SCOPES")
    if not raw:
        return DEFAULT_SCOPES
    return [s.strip() for s in raw.split(",") if s.strip()]


def _credentials_from_env(scopes: Optional[List[str]] = None) -> Credentials:
    """
    Build a google.oauth2.service_account.Credentials object using either:
    - GOOGLE_CREDS_JSON (one-line JSON)
    - GOOGLE_CREDS_PATH (path to JSON file)

    Raises:
        RuntimeError: if neither env var is present or JSON is invalid.
    """
    scopes = scopes or _scopes_from_env()
    json_str = os.getenv("GOOGLE_CREDS_JSON")
    if json_str:
        try:
            info = json.loads(json_str)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Invalid GOOGLE_CREDS_JSON") from exc
        return Credentials.from_service_account_info(info, scopes=scopes)

    path = os.getenv("GOOGLE_CREDS_PATH", "service_account.json")
    if not os.path.exists(path):
        raise RuntimeError(
            "Missing service account credentials. Set GOOGLE_CREDS_JSON, or "
            f"place a file at GOOGLE_CREDS_PATH (current: {path})."
        )
    return Credentials.from_service_account_file(path, scopes=scopes)


def get_client() -> gspread.Client:
    """
    Return an authorized gspread client
    """
    load_dotenv()
    creds = _credentials_from_env()
    return gspread.authorize(creds)


def get_sheet(client: Optional[gspread.Client] = None) -> gspread.Spreadsheet:
    """
    Open and return the spreadsheet specified using SHEET_ID.
    """
    client = client or get_client()
    sheet_id = os.getenv("SHEET_ID")
    if not sheet_id:
        raise RuntimeError("SHEET_ID is missing. Add it to your .env file.")
    return client.open_by_key(sheet_id)


def verify_connection() -> None:
    """
    Test Google Sheets connectivity and print sheet title if successful.
    """
    try:
        client = get_client()
        sheet = get_sheet(client)
        print(f"Connected successfully to: {sheet.title}")
    except Exception as exc:
        print(f"Connection failed: {exc}")
        raise
