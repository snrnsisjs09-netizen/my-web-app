"""주간 비교 페이지: W44 → W45 장비별 가동률 증감과 비고 칸 기록."""
from pathlib import Path

import pandas as pd
import streamlit as st

import calc

DATA = Path(__file__).resolve().parents[1] / "data"

st.title("주간 비교")
st.caption("교육용 가상 데이터입니다. 실제 부대 · 장비 · 사람과 관계없습니다.")
st.write("지난주(W44, 10/26 ~ 11/1)와 이번 주(W45, 11/2 ~ 11/8)의 장비별 가동률(%)을 비교합니다.")

prev = calc.load_readiness(DATA / "readiness_W44.csv")
cur = calc.load_readiness(DATA / "readiness_W45.csv")
cmp = calc.compare_weeks(prev, cur)

COLS = {"가동률_이전": st.column_config.NumberColumn("지난주(%)", format="%.1f"),
        "가동률_이번": st.column_config.NumberColumn("이번 주(%)", format="%.1f"),
        "증감": st.column_config.NumberColumn("증감(%p)", format="%+.1f")}

c1, c2 = st.columns(2)
with c1:
    st.subheader("상승 상위 3")
    st.dataframe(cmp.head(3), hide_index=True, column_config=COLS, width="stretch")
with c2:
    st.subheader("하락 상위 3")
    st.dataframe(cmp.tail(3).iloc[::-1], hide_index=True, column_config=COLS, width="stretch")

st.subheader("전체 (증감이 큰 순서)")
st.dataframe(cmp, hide_index=True, column_config=COLS, width="stretch")

st.subheader("비고 칸에 글이 있는 행")
st.caption("비고 칸의 글은 기록된 데이터 그대로 보여 줍니다. 계산에는 쓰지 않습니다.")
notes = pd.concat([prev.assign(주차="W44"), cur.assign(주차="W45")])
notes = notes[notes["비고"].str.strip() != ""]
if notes.empty:
    st.write("비고 칸에 글이 있는 행이 없습니다.")
else:
    st.dataframe(
        notes[["주차", "일자", "장비코드", "장비명", "계획시간", "가동시간", "비고"]],
        hide_index=True,
        width="stretch",
    )
