"""가동률 계산 함수 (AGENTS.md '고정 약속'의 네 함수).

- 가동률 = 가동시간 합계 ÷ 계획시간 합계 × 100 (일별 가동률의 평균을 쓰지 않는다)
- 가동시간이 음수인 정정 행도 지우지 않고 합계에 포함한다.
- 가동률과 증감은 소수 첫째 자리로 반올림한다.
- 비고 칸의 글은 데이터로만 읽고 계산에 쓰지 않는다.
"""
from __future__ import annotations

import pandas as pd

PLAN, RUN = "계획시간", "가동시간"
KEYS = ["장비코드", "장비명"]


def _rate(run: float, plan: float) -> float:
    """가동시간 ÷ 계획시간 × 100, 소수 첫째 자리. 계획시간이 0이면 0.0."""
    return round(float(run) / float(plan) * 100, 1) if plan else 0.0


def load_readiness(path) -> pd.DataFrame:
    """가동률 CSV를 읽는다. 계획시간(h) · 가동시간(h) 열 이름을 계획시간 · 가동시간으로 바꾼다."""
    df = pd.read_csv(path, encoding="utf-8-sig", dtype={"비고": str})
    df = df.rename(columns={"계획시간(h)": PLAN, "가동시간(h)": RUN})
    df[PLAN] = pd.to_numeric(df[PLAN])
    df[RUN] = pd.to_numeric(df[RUN])
    df["비고"] = df["비고"].fillna("")
    return df


def total_rate(df: pd.DataFrame) -> float:
    """전체 가동률(%), 소수 첫째 자리."""
    return _rate(df[RUN].sum(), df[PLAN].sum())


def rate_by_equipment(df: pd.DataFrame) -> pd.DataFrame:
    """장비별 계획시간 · 가동시간 합계와 가동률. CSV에 나온 장비 순서를 따른다."""
    out = df.groupby(KEYS, sort=False, as_index=False)[[PLAN, RUN]].sum()
    out["가동률"] = [_rate(r, p) for r, p in zip(out[RUN], out[PLAN])]
    return out[KEYS + [PLAN, RUN, "가동률"]].reset_index(drop=True)


def compare_weeks(prev: pd.DataFrame, cur: pd.DataFrame) -> pd.DataFrame:
    """두 주의 장비별 가동률 비교. 증감(부호 포함) 내림차순, 한쪽에만 있는 장비는 맨 뒤."""
    a = rate_by_equipment(prev)[KEYS + ["가동률"]].rename(columns={"가동률": "가동률_이전"})
    b = rate_by_equipment(cur)[KEYS + ["가동률"]].rename(columns={"가동률": "가동률_이번"})
    out = a.merge(b, on=KEYS, how="outer", sort=False)
    out["증감"] = (out["가동률_이번"] - out["가동률_이전"]).round(1)
    out = out.sort_values("증감", ascending=False, na_position="last", kind="stable")
    return out[KEYS + ["가동률_이전", "가동률_이번", "증감"]].reset_index(drop=True)
