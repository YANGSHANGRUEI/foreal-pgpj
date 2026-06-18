import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from utils.nav_pages import build_pages
from utils.session import restore_login
from utils.sheets_client import sheets_storage_label, test_sheets_connection, use_sheets

st.set_page_config(page_title="法律申論題眾包平台")

restore_login(st)

with st.sidebar:
    mode = sheets_storage_label()
    if use_sheets():
        st.info(f"資料儲存：{mode}")
    else:
        st.warning(f"資料儲存：{mode}")
    with st.expander("試算表連線測試"):
        if st.button("測試連線", key="test_sheets_btn"):
            ok, msg = test_sheets_connection()
            if ok:
                st.success(msg)
            else:
                st.error(msg)

pages = build_pages(st.session_state.get("logged_in"))
pg = st.navigation(pages)
pg.run()
