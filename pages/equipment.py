"""장비별 상세 페이지: 주차와 장비를 골라 가동률 · 합계 · 일별 계획/가동시간을 본다."""
from pathlib import Path

import streamlit as st

import calc

DATA = Path(__file__).resolve().parents[1] / "data"
WEEKS = {
    "W45 (11/2 ~ 11/8)": "readiness_W45.csv",
    "W44 (10/26 ~ 11/1)": "readiness_W44.csv",
}

st.title("장비별 상세")
st.caption("교육용 가상 데이터입니다. 실제 부대 · 장비 · 사람과 관계없습니다.")

c1, c2 = st.columns(2)
week = c1.selectbox("주차", list(WEEKS))
df = calc.load_readiness(DATA / WEEKS[week])

by_eq = calc.rate_by_equipment(df)
labels = {f"{r.장비코드} · {r.장비명}": r.장비코드 for r in by_eq.itertuples()}
code = labels[c2.selectbox("장비", list(labels))]

row = by_eq[by_eq["장비코드"] == code].iloc[0]
m1, m2, m3 = st.columns(3)
m1.metric("가동률", f"{row['가동률']:.1f}%")
m2.metric("가동시간 합계", f"{row['가동시간']:,} h")
m3.metric("계획시간 합계", f"{row['계획시간']:,} h")

rows = df[df["장비코드"] == code]
daily = rows.groupby("일자", sort=True)[["계획시간", "가동시간"]].sum()

st.subheader("일별 계획시간 · 가동시간 (h)")
st.line_chart(daily, x_label="일자", y_label="시간(h)")
if (rows["가동시간"] < 0).any():
    st.info("이 장비에는 가동시간이 음수인 정정 행이 있습니다. 그래프는 같은 날짜의 행을 합친 값이고, 아래 표에는 원래 행을 그대로 보여 줍니다.")

st.subheader("일별 기록")
st.dataframe(
    rows[["일자", "계획시간", "가동시간", "비고"]],
    hide_index=True,
    width="stretch",
)
