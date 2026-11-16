"""장비 가동률 대시보드 · 정비 요청 앱의 시작 파일 (페이지 연결)."""
import streamlit as st

import db

st.set_page_config(page_title="장비 가동률 대시보드", page_icon="🛠️", layout="wide")


@st.cache_resource
def _init_db_once() -> bool:
    """정비 요청 표가 없으면 만든다. 앱 프로세스당 한 번만 실행된다."""
    db.init_db()
    return True


_init_db_once()

pages = [
    st.Page("pages/summary.py", title="요약", icon="📊", default=True),
    st.Page("pages/equipment.py", title="장비별 상세", icon="🔧"),
    st.Page("pages/weekly.py", title="주간 비교", icon="📈"),
    st.Page("pages/requests.py", title="정비 요청", icon="📝"),
]
nav = st.navigation(pages)
nav.run()
