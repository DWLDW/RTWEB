# RTWEB LMS (MVP)

영어학원용 LMS MVP 프로젝트입니다. 로컬 환경에서 바로 실행할 수 있도록 구성되어 있습니다.

## 가장 빠른 실행 요약 (복붙용)

### macOS / Linux
```bash
cd /workspace/RTWEB
bash setup.sh
source .venv/bin/activate
python app.py
```

### Windows PowerShell
```powershell
cd /workspace/RTWEB
.\setup_windows.ps1
python app.py
```

접속 주소: `http://127.0.0.1:8000/login`

---

## 1) Python이 없는 경우 먼저 할 일

- **Windows**: https://www.python.org/downloads/windows/ 에서 Python 3.10+ 설치
  - 설치 시 **Add Python to PATH** 체크
- **macOS**(Homebrew):
  ```bash
  brew install python
  ```
- **Ubuntu/Debian**:
  ```bash
  sudo apt update
  sudo apt install -y python3 python3-venv
  ```

설치 확인:
- Windows: `python --version`
- macOS/Linux: `python3 --version`

---

## 2) 초보자용 설치/실행 방법

### A. Windows PowerShell
1. 프로젝트 폴더 이동
   ```powershell
   cd /workspace/RTWEB
   ```
2. 설치 스크립트 실행
   ```powershell
   .\setup_windows.ps1
   ```
3. 서버 실행
   ```powershell
   python app.py
   ```
4. 브라우저 접속: `http://127.0.0.1:8000/login`

#### PowerShell 실행 정책 오류가 나는 경우
아래 명령 1회 실행 후 다시 시도하세요.
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### B. macOS / Linux
1. 프로젝트 폴더 이동
   ```bash
   cd /workspace/RTWEB
   ```
2. 설치 스크립트 실행
   ```bash
   bash setup.sh
   ```
3. 가상환경 활성화
   ```bash
   source .venv/bin/activate
   ```
4. 서버 실행
   ```bash
   python app.py
   ```
5. 브라우저 접속: `http://127.0.0.1:8000/login`

---

## 3) init_db 자동 실행 흐름

`app.py`를 실행하면 내부에서 `init_db()`가 자동으로 실행됩니다.

자동으로 처리되는 내용:
- `schema.sql` 기반 테이블 생성
- 기본 계정 생성(원장/매니저/강사/학부모/학생)
- 학생(`role=student`)에 대한 `students` 프로필 기본 생성
- 결과 DB 파일: `lms.db`

---

## 4) 접속 주소 / 기본 계정

- 로그인 페이지: `http://127.0.0.1:8000/login`

기본 계정:
- 원장: `owner / 1234`
- 매니저: `manager / 1234`
- 강사: `teacher / 1234`
- 학부모: `parent / 1234`
- 학생: `student / 1234`

---

## 5) 로컬 최소 테스트 순서

1. 로그인 (`/login`)
2. 사용자 관리 (`/users`)
3. 학생 상세 (`/students`)
4. 학사구조 (`/academics`)
5. 출결 (`/attendance`)
6. 숙제 (`/homework`)
7. 시험/성적 (`/exams`)
8. 상담 (`/counseling`)
9. 수납 (`/payments`)
10. 공지/알림 (`/announcements`)
11. 도서 대출 (`/library`)

---

## 6) 참고

- `requirements.txt`는 현재 최소 구성(외부 필수 패키지 없음)입니다.
- 설치 스크립트는 표준 절차를 유지하기 위해 `pip install -r requirements.txt`를 수행합니다.
- DB 마이그레이션 SQL:
  - `migrations/001_init.sql`
  - `migrations/002_add_students_table.sql`


## 7) 다국어 메뉴 (한국어/English/中文)

- 로그인 후 상단 네비게이션의 언어 드롭다운에서 **한국어 / English / 中文** 전환이 가능합니다.
- 현재 버전은 메뉴/학생관리 화면 중심으로 3개 언어 라벨을 제공합니다.


## 8) RBAC(역할 기반 접근 제어) 기본 적용

- owner: 전체 접근
- manager: 대부분 운영 접근(단, `/users` 차단)
- teacher: 수업 운영 기능 중심 접근(`payments` 차단)
- parent/student: 조회 중심 접근, 운영 관리 화면 일부 차단
- 권한 없는 페이지/API 접근 시 403 응답을 반환합니다.


## 9) i18n 기본 구조 (ko/zh/en)

### 언어 파일 분리/확장 (Addon 방식)
- `locales/*.json` 파일을 자동 로드합니다.
- 예: `locales/ja.json` 추가 시 `ja` 언어 코드가 자동으로 지원 목록에 포함됩니다.
- 파일 형식:
  - `__labels__.lang`: 드롭다운 표시명
  - 나머지 키: 번역 키-값(`menu.dashboard`, `common.save` 등)
- 앱 내 기본 사전(`I18N_TEXTS`)을 기본값으로 두고, 파일의 값이 있으면 덮어씁니다.

- 현재 언어 저장: `lang` 쿠키 (`?lang=ko|zh|en` 선택 시 자동 저장)
- 공통 번역 사전: `app.py`의 `I18N_TEXTS`
- 공통 함수:
  - `t(key)` : 일반 문구
  - `menu_t(key)` : 메뉴 문구
  - `status_t(status)` : 상태(active/leave/ended)

### 이번 단계 적용 범위
- 상단 메뉴
- 로그인 화면
- 공통 버튼 일부(저장/검색/로그인/로그아웃)
- 학생 상태값(active/leave/ended) 표기

### 향후 확대 적용 포인트
1. 페이지 제목/폼 라벨을 `t()`로 단계적 치환
2. 에러/알림 메시지 키 분리
3. 상태값 외 도메인 코드(출결 상태 등) 번역 테이블화
4. API 응답 메시지의 다국어 처리 정책 수립

## 10) 입력 검증/오류 메시지 강화

- 공통 검증 유틸 추가:
  - 필수값, 숫자, 날짜(`YYYY-MM-DD`), 시간(`HH:MM`) 검증
  - enum 허용값 검증
  - 참조값 존재 검증(`ensure_exists`)
- 적용 화면:
  - 학생 등록/수정 (`/students`, `/students/{id}`)
  - 마스터데이터 (`/masterdata`)
  - 스케줄 (`/schedule`)
  - 출결 (`/attendance`)
  - 시험/성적 (`/exams`)
  - 수납 (`/payments`)
  - 상담 (`/counseling`)
- 실패 시 조용히 무시하지 않고, 필드 단위 오류 메시지를 플래시로 표시합니다.

### 시스템 로그 확인
- owner 전용: `/logs`
- 검증 실패 및 주요 저장 예외가 DB(`app_logs`)에 적재됩니다.

### 마스터데이터 삭제
- `/masterdata`의 코스/레벨/반/교실/시간슬롯 목록에 삭제 버튼 추가.
- 참조 중 데이터는 삭제 차단(예: 시간표에서 사용 중인 반).

## 11) 마스터데이터/시간표 선택 UX 개선

- 시간표의 반 선택 picker는 검색어가 없어도 전체 반(최대 20개)을 표시합니다.
- 반 선택 리스트는 `반명/코스/레벨/담당강사/학생수` 컬럼으로 표시됩니다.
- 시간표 등록은 시작/종료 직접 선택 대신 `시간 슬롯` 선택(`start|end`) 중심으로 동작합니다.
- 마스터데이터는 `반 / 코스·레벨 / 교사 / 교실·시간대` 섹션 버튼으로 분리되어 기본 진입 시 과다 노출을 줄였습니다.

## 12) DB 구조 진단/사전 점검

- 설계 기준 문서: `docs/db_design.md`
- 개발 전 점검 스크립트:
  ```bash
  python3 scripts/db_preflight.py --db lms.db
  ```
- 점검 항목:
  - 테이블/컬럼/FK 현황
  - 주요 필수 컬럼 누락
  - 역할-프로필 불일치(`role=student`인데 `students` 없음, `role=teacher`인데 `teachers` 프로필 없음)
  - `teachers.teacher_type` 유효성 및 `users.teacher_type` 누락 여부
  - 참조 무결성 이상(클래스/학생/교실/시험/도서 참조 깨짐)
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours

## Handoff
- Latest Codex handoff: `docs/handoff_latest.md`
=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
