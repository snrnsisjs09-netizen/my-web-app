"""요약 페이지: 이번 주 · 지난주 전체 가동률, 목표와의 차이, 장비별 이번 주 가동률."""
from pathlib import Path

import streamlit as st

import calc

DATA = Path(__file__).resolve().parents[1] / "data"
TARGET = 90.0  # 훈련 전 장비 가동률 목표(%)

prev = calc.load_readiness(DATA / "readiness_W44.csv")
cur = calc.load_readiness(DATA / "readiness_W45.csv")

rate_prev = calc.total_rate(prev)
rate_cur = calc.total_rate(cur)
change = round(rate_cur - rate_prev, 1)
gap = round(rate_cur - TARGET, 1)

st.title("요약")
st.caption("교육용 가상 데이터입니다. 실제 부대 · 장비 · 사람과 관계없습니다.")
st.write("2026-W45 (11/2 ~ 11/8) 장비 12대의 가동률입니다. 가동률 = 가동시간 합계 ÷ 계획시간 합계 × 100")

c1, c2, c3 = st.columns(3)
c1.metric("이번 주 가동률 (W45)", f"{rate_cur:.1f}%", f"{change:+.1f}%p (지난주 대비)")
c2.metric("지난주 가동률 (W44)", f"{rate_prev:.1f}%")
c3.metric(f"목표 {TARGET:.0f}%와의 차이", f"{gap:+.1f}%p", help="이번 주 가동률 − 목표")

st.subheader("장비별 이번 주 가동률 (%)")
by_eq = calc.rate_by_equipment(cur)
chart = by_eq.set_index("장비명")["가동률"]
st.bar_chart(chart, x_label="장비", y_label="가동률(%)")
