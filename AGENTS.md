# AGENTS.md

## 목적

- 장비 가동률 대시보드와 정비 요청 접수 기능이 있는 Streamlit 웹 앱을 만든다.
- 데이터는 교육용 가상 데이터다. 실제 부대 · 장비 · 사람 정보는 넣지 않는다.

## 폴더

- `data/readiness_W44.csv` · `data/readiness_W45.csv`: 장비 12대의 지난주 · 이번 주 일별 계획 · 가동시간 (읽기만 한다)
- `db.py`: 정비 요청 저장소 (제공 파일)
- `calc.py`: 가동률 계산 함수 (만들 파일)
- `app.py` · `pages/`: 화면 (만들 파일)
- `scripts/check_app.py`: 진행 확인 스크립트 (제공 파일)

## 실행 명령

- 설치: `python -m pip install -r requirements.txt`
- 실행: `streamlit run app.py`
- 확인: `python scripts/check_app.py`

## 고정 약속 (바꾸지 않는다)

- `db.py` · `scripts/check_app.py` · `data/` 는 고치지 않는다.
- 정비 요청은 `db.py`의 `init_db` · `add_request` · `list_requests` · `update_status`로만 저장 · 조회한다.
- `calc.py`에는 아래 네 함수를 둔다. 이름과 반환 형식을 바꾸지 않는다.
  - `load_readiness(path) -> DataFrame`: CSV를 읽는다
  - `total_rate(df) -> float`: 전체 가동률(%), 소수 첫째 자리
  - `rate_by_equipment(df) -> DataFrame`: 열 `장비코드 · 장비명 · 계획시간 · 가동시간 · 가동률`
  - `compare_weeks(prev, cur) -> DataFrame`: 열 `장비코드 · 장비명 · 가동률_이전 · 가동률_이번 · 증감`, 증감이 큰 순서

## 규칙

<!-- Lab 1에서 직접 쓴다. 한 줄에 하나, '- '로 시작한다. -->
