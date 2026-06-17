import json
import os
import hashlib
import hmac

SESSION_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "current_session.json"
)
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
    if st.session_state.get("logged_in"):
        return
    if not os.path.exists(SESSION_FILE):
        return
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    user_id = data.get("user_id")
    sig = data.get("sig")
    if not user_id or not sig:
        return
    expected = _make_sig(user_id)
    if not hmac.compare_digest(sig, expected):
        return

    users_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "users.json"
    )
    if not os.path.exists(users_file):
        return
    with open(users_file, "r", encoding="utf-8") as f:
        users = json.load(f)

    username = None
    for name in users.keys():
        if hashlib.sha256(name.encode("utf-8")).hexdigest()[:12] == user_id:
            username = name
            break
    if username is None:
        return

    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["user_id"] = user_id


def save_login(st, username, user_id):
    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["user_id"] = user_id
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    sig = _make_sig(user_id)
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"user_id": user_id, "sig": sig}, f, ensure_ascii=False, indent=2)


def clear_login(st):
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
