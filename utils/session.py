import os

from utils.sheets_client import (
    get_streamlit_session_id,
    get_worksheet,
    use_sheets,
)

SESSION_COLUMNS = ["session_id", "user_id", "username"]


def _load_session_rows() -> list[dict]:
    ws = get_worksheet("session")
    return ws.get_all_records()


def _save_session_rows(rows: list[dict]) -> None:
    ws = get_worksheet("session")
    out = [SESSION_COLUMNS]
    for row in rows:
        out.append(
            [
                str(row.get("session_id", "")),
                str(row.get("user_id", "")),
                str(row.get("username", "")),
            ]
        )
    ws.clear()
    if len(out) > 1:
        ws.update(out, value_input_option="RAW")
    else:
        ws.update([SESSION_COLUMNS], value_input_option="RAW")


def restore_login(st):
    if st.session_state.get("logged_in"):
        return
    if not use_sheets():
        return

    session_id = get_streamlit_session_id()
    if not session_id:
        return

    for row in _load_session_rows():
        if str(row.get("session_id", "")) != session_id:
            continue
        user_id = str(row.get("user_id", "")).strip()
        username = str(row.get("username", "")).strip()
        if not user_id or not username:
            return
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_id"] = user_id
        return


def save_login(st, username, user_id):
    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["user_id"] = user_id

    if not use_sheets():
        return

    session_id = get_streamlit_session_id()
    if not session_id:
        return

    rows = _load_session_rows()
    rows = [r for r in rows if str(r.get("session_id", "")) != session_id]
    rows.append(
        {
            "session_id": session_id,
            "user_id": user_id,
            "username": username,
        }
    )
    _save_session_rows(rows)


def clear_login(st):
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None

    if not use_sheets():
        return

    session_id = get_streamlit_session_id()
    if not session_id:
        return

    rows = _load_session_rows()
    rows = [r for r in rows if str(r.get("session_id", "")) != session_id]
    _save_session_rows(rows)
