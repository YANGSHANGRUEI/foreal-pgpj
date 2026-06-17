import hashlib
import hmac
import os


_DEFAULT_SECRET = "law-essay-local-secret"


def get_session_secret() -> str:
    if secret := os.environ.get("SESSION_SECRET"):
        return secret
    try:
        import streamlit as st

        if "SESSION_SECRET" in st.secrets:
            return st.secrets["SESSION_SECRET"]
    except Exception:
        pass
    return _DEFAULT_SECRET


def _make_sig(user_id: str) -> str:
    return hmac.new(
        get_session_secret().encode("utf-8"),
        user_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def restore_login(st):
    """僅依瀏覽器自己的 session_state；不讀共用檔案（雲端多人安全）。"""
    if st.session_state.get("logged_in"):
        return


def save_login(st, username, user_id):
    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["user_id"] = user_id


def clear_login(st):
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
