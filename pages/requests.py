"""정비 요청 페이지: 등록 · 상태 변경 · 목록. 저장 · 조회는 db.py 함수로만 한다."""
from pathlib import Path

import streamlit as st

import calc
import db

DATA = Path(__file__).resolve().parents[1] / "data"
ALL = "전체"
SHOW = {"id": "번호", "created_at": "등록 시각", "equipment_code": "장비코드", "title": "요청 내용",
        "priority": "우선순위", "requester_role": "요청자 역할", "status": "상태"}

st.title("정비 요청")
st.caption("교육용 가상 데이터입니다. 실제 부대 · 장비 · 사람과 관계없습니다.")
st.info(f"지금 저장소: {db.backend_name()}")

equip = calc.rate_by_equipment(calc.load_readiness(DATA / "readiness_W45.csv"))
equip_labels = {f"{r.장비코드} · {r.장비명}": r.장비코드 for r in equip.itertuples()}

# 1. 등록
st.subheader("요청 등록")
with st.form("new_request", clear_on_submit=True):
    label = st.selectbox("장비", list(equip_labels))
    title = st.text_input("요청 내용", max_chars=200)
    c1, c2 = st.columns(2)
    priority = c1.selectbox("우선순위", db.PRIORITIES, index=db.PRIORITIES.index("보통"))
    role = c2.text_input("요청자 역할명", placeholder="예: 정비 담당", help="사람 이름 대신 역할명을 씁니다.")
    if st.form_submit_button("등록"):
        try:
            rid = db.add_request(equip_labels[label], title, priority, role)
            st.success(f"{rid}번 요청을 '접수' 상태로 등록했습니다.")
        except ValueError as e:
            st.error(str(e))

# 2. 상태 변경
st.subheader("상태 변경")
everything = db.list_requests()
if everything.empty:
    st.write("등록된 요청이 없습니다.")
else:
    ids = [int(i) for i in everything["id"]]
    names = {int(r.id): f"{int(r.id)}번 · {r.equipment_code} · {r.title}" for r in everything.itertuples()}
    c1, c2, c3 = st.columns([3, 1, 1])
    rid = c1.selectbox("요청 번호", ids, format_func=lambda i: names.get(i, str(i)), key="status_request_id")
    new_status = c2.selectbox("바꿀 상태", db.STATUSES)
    c3.write("")
    if c3.button("상태 변경", width="stretch"):
        db.update_status(rid, new_status)
        st.success(f"{rid}번 요청을 '{new_status}' 상태로 바꿨습니다.")

# 3. 목록
st.subheader("요청 목록")
status = st.selectbox("상태로 거르기", [ALL] + db.STATUSES)
table = db.list_requests(status=None if status == ALL else status)
if table.empty:
    st.write("해당하는 요청이 없습니다.")
else:
    st.dataframe(table.rename(columns=SHOW), hide_index=True, width="stretch")
