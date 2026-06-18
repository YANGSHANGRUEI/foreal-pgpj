"""Google Sheets 後端（部署用）。需在 Streamlit Secrets 設定 gcp_service_account。"""

import json

ANSWERS_SHEET_ID = "1lasUgPoaDM5O909Cu87EOCcazm3DU7QShuGwjXuS8gM"
USERS_SHEET_ID = "1G3aM4qNQEyY__yvi-WQi1fA9DRIxk87FFnIU8d0C9jc"
SESSION_SHEET_ID = "1PkNw_5ckpiHLTW6ikaelutCBCsrElxElujiPj-IUCac"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def use_sheets() -> bool:
    try:
        import streamlit as st

        return "gcp_service_account" in st.secrets
    except Exception:
        return False


def get_streamlit_session_id() -> str:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        if ctx and ctx.session_id:
            return str(ctx.session_id)
    except Exception:
        pass
    return ""


def _get_client():
    import gspread
    import streamlit as st
    from google.oauth2.service_account import Credentials

    creds_info = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(creds)


def get_worksheet(sheet_key: str):
    import gspread

    sheet_ids = {
        "answers": ANSWERS_SHEET_ID,
        "users": USERS_SHEET_ID,
        "session": SESSION_SHEET_ID,
    }
    client = _get_client()
    spreadsheet = client.open_by_key(sheet_ids[sheet_key])
    return spreadsheet.sheet1


def parse_unlocked(value) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    text = str(value).strip()
    if not text:
        return []
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []
