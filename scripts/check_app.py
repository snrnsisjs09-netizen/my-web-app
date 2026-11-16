"""진행 확인 스크립트 (실습 묶음 제공 파일 · 고치지 않는다).

사용법 (my-web-app 폴더에서):
    python scripts/check_app.py          Lab 1 ~ 4 확인 (내 PC의 임시 SQLite로 시험)
    python scripts/check_app.py --db     지금 연결 주소(secrets.toml)의 DB에 실제로 접속해 본다 (Lab 5)

- 어떤 AI 도구로 만들었든 같은 기준으로 본다: 규칙 줄 수, calc.py 계산 값, 앱 실행 오류, 비밀 값 커밋 여부.
- 시험은 임시 폴더의 SQLite로 한다. 내 데이터(data/app.db)와 Supabase는 건드리지 않는다(--db 일 때만 접속).
"""
from __future__ import annotations

import importlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("STREAMLIT_LOGGER_LEVEL", "error")   # 시험 실행 때 나오는 Streamlit 경고 줄을 숨긴다

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

OK, TODO, BAD = "[통과]", "[아직]", "[다름]"
EXPECT_TOTAL = {"readiness_W44.csv": 81.4, "readiness_W45.csv": 82.8}
EXPECT_EQUIP = {("readiness_W45.csv", "GN-202"): 64.6, ("readiness_W45.csv", "VH-103"): 83.3,
                ("readiness_W44.csv", "UV-401"): 60.4}
EXPECT_TOP, EXPECT_BOTTOM = ("UV-401", 14.6), ("GN-202", -22.9)
results: list[tuple[str, str, str]] = []


def report(lab: str, mark: str, msg: str) -> None:
    results.append((lab, mark, msg))
    print(f"{mark} {lab} · {msg}")


def check_rules() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    m = re.search(r"(?ms)^## 규칙\s*\n(.*?)(?=^## |\Z)", text)
    rules = [ln for ln in (m.group(1) if m else "").splitlines() if ln.strip().startswith("- ")]
    if len(rules) >= 3:
        report("Lab 1", OK, f"AGENTS.md 규칙 {len(rules)}줄")
    else:
        report("Lab 1", TODO, f"AGENTS.md '## 규칙' 아래 규칙이 {len(rules)}줄입니다. 3줄 이상 씁니다")


def check_calc() -> bool:
    if not (ROOT / "calc.py").exists():
        report("Lab 2", TODO, "calc.py가 아직 없습니다")
        return False
    try:
        calc = importlib.import_module("calc")
    except Exception as e:
        report("Lab 2", BAD, f"calc.py를 불러오다 오류: {type(e).__name__}: {e}")
        return False
    need = ["load_readiness", "total_rate", "rate_by_equipment", "compare_weeks"]
    miss = [n for n in need if not hasattr(calc, n)]
    if miss:
        report("Lab 2", BAD, f"calc.py에 함수가 없습니다: {', '.join(miss)} (AGENTS.md '고정 약속')")
        return False
    good = True
    try:
        frames = {f: calc.load_readiness(str(ROOT / "data" / f)) for f in EXPECT_TOTAL}
        for f, want in EXPECT_TOTAL.items():
            got = round(float(calc.total_rate(frames[f])), 1)
            if got != want:
                good = False
                report("Lab 2", BAD, f"total_rate({f}) = {got} (기대 {want}). 가동률은 합계 ÷ 합계, 음수 정정 행도 포함")
        for (f, code), want in EXPECT_EQUIP.items():
            t = calc.rate_by_equipment(frames[f])
            row = t[t["장비코드"] == code]
            got = round(float(row["가동률"].iloc[0]), 1) if len(row) else None
            if got != want:
                good = False
                report("Lab 2", BAD, f"rate_by_equipment({f}) {code} 가동률 = {got} (기대 {want})")
        cmp = calc.compare_weeks(frames["readiness_W44.csv"], frames["readiness_W45.csv"])
        top = (cmp.iloc[0]["장비코드"], round(float(cmp.iloc[0]["증감"]), 1))
        bottom = (cmp.iloc[-1]["장비코드"], round(float(cmp.iloc[-1]["증감"]), 1))
        if top != EXPECT_TOP or bottom != EXPECT_BOTTOM:
            good = False
            report("Lab 2", BAD, f"compare_weeks 처음 · 끝 = {top} · {bottom} (기대 {EXPECT_TOP} · {EXPECT_BOTTOM}, 증감이 큰 순서)")
    except Exception as e:
        report("Lab 2", BAD, f"calc.py 실행 오류: {type(e).__name__}: {e}")
        return False
    if good:
        report("Lab 2", OK, "calc.py 계산 값이 기준값과 같습니다 (81.4% → 82.8%)")
    return good


def check_db_roundtrip() -> None:
    import db
    with tempfile.TemporaryDirectory() as d:
        url = f"sqlite:///{Path(d, 'check.db').as_posix()}"
        try:
            db.init_db(url)
            rid = db.add_request("GN-202", "점검 시험 요청", "높음", "정비 담당", url=url)
            db.update_status(rid, "진행", url=url)
            df = db.list_requests(url=url)
            assert len(df) == 1 and df.iloc[0]["status"] == "진행"
            report("Lab 3", OK, "db.py 저장 · 조회 · 상태 변경이 동작합니다 (임시 SQLite)")
        except Exception as e:
            report("Lab 3", BAD, f"db.py 시험 실패: {type(e).__name__}: {e} (db.py를 고쳤다면 묶음 원본으로 되돌립니다)")
        finally:
            db.get_engine(url).dispose()


def check_app_runs() -> None:
    if not (ROOT / "app.py").exists():
        report("Lab 3", TODO, "app.py가 아직 없습니다")
        return
    try:
        from streamlit.testing.v1 import AppTest
    except Exception:
        report("Lab 3", TODO, "streamlit이 설치되지 않았습니다 (python -m pip install -r requirements.txt)")
        return
    with tempfile.TemporaryDirectory() as d:
        os.environ["DATABASE_URL"] = f"sqlite:///{Path(d, 'app.db').as_posix()}"
        try:
            at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
            at.secrets["connections"] = {"sql": {"url": os.environ["DATABASE_URL"]}}
            at.run()
            if at.exception:
                report("Lab 3", BAD, f"앱 실행 오류: {at.exception[0].message}")
            else:
                report("Lab 3", OK, "app.py가 오류 없이 실행됩니다 (첫 화면)")
        except Exception as e:
            report("Lab 3", BAD, f"앱 실행 오류: {type(e).__name__}: {e}")
        finally:
            import db
            db.get_engine(os.environ["DATABASE_URL"]).dispose()
            os.environ.pop("DATABASE_URL", None)


def check_secrets_not_committed() -> None:
    try:
        tracked = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines()
    except Exception:
        report("Lab 4", TODO, "git 레포가 아닙니다 (GitHub 레포를 clone한 폴더에서 실행합니다)")
        return
    leaked = [f for f in tracked if f.endswith("secrets.toml") or f.endswith(".db")]
    for f in tracked:
        p = ROOT / f
        if p.is_file() and p.suffix in {".py", ".md", ".toml", ".txt", ".example"}:
            if re.search(r"postgres(ql)?://[^\s\"']*:(?!\[YOUR-PASSWORD\])[^@\s\"']+@", p.read_text(encoding="utf-8", errors="ignore")):
                leaked.append(f)
    if leaked:
        report("Lab 4", BAD, f"비밀 값이나 DB 파일이 커밋돼 있습니다: {', '.join(sorted(set(leaked)))} → 강사에게 알립니다")
    else:
        report("Lab 4", OK, "커밋된 파일에 비밀 값 · DB 파일이 없습니다")


def check_live_db() -> None:
    import db
    url = db.database_url()
    shown = re.sub(r"://([^:/@]+):[^@]+@", r"://\1:****@", url)
    print(f"\n연결 주소: {shown}  ({db.backend_name(url)})")
    try:
        db.init_db(url)
        n = len(db.list_requests(url=url))
        report("Lab 5", OK, f"DB 접속 성공 · 정비 요청 {n}건")
    except Exception as e:
        msg = str(e).splitlines()[0][:160]
        hint = ""
        if "password authentication failed" in msg:
            hint = " → 비밀번호를 확인합니다. [YOUR-PASSWORD]의 대괄호까지 지웠는지 봅니다"
        elif "timeout" in msg.lower() or "could not translate host" in msg or "Network is unreachable" in msg:
            hint = " → Session pooler 주소인지, 교육장 네트워크가 5432 포트를 막지 않는지 봅니다"
        report("Lab 5", BAD, f"DB 접속 실패: {msg}{hint}")


def main() -> None:
    if "--db" in sys.argv:
        check_live_db()
        return
    print("== 진행 확인 ==")
    check_rules()
    check_calc()
    check_db_roundtrip()
    check_app_runs()
    check_secrets_not_committed()
    bad = sum(1 for _, m, _ in results if m != OK)
    print(f"\n한 줄 요약: {len(results) - bad}/{len(results)} 통과" + ("" if bad else " · 배포해도 됩니다"))


if __name__ == "__main__":
    main()
