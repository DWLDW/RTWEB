# RTWEB LMS (MVP)

영어학원용 LMS MVP를 **표준 라이브러리 기반(Python + SQLite)** 으로 구현한 프로젝트입니다.

## 1) 초보자용 설치 명령어

### macOS / Linux
```bash
cd /workspace/RTWEB
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python3 app.py
```

### Windows (PowerShell)
```powershell
cd /workspace/RTWEB
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python app.py
```

> 외부 패키지 설치가 필요 없습니다.

## 2) 실행
- 서버: `http://127.0.0.1:8000`
- 최초 실행 시 `lms.db` 파일과 초기 데이터가 자동 생성됩니다.

기본 계정:
- 원장: `owner / 1234`
- 매니저: `manager / 1234`
- 강사: `teacher / 1234`
- 학부모: `parent / 1234`
- 학생: `student / 1234`

## 3) 로컬 테스트 절차
1. 로그인 (`/login`)
2. 사용자 관리 (`/users`)
3. 학사구조 (`/academics`)
4. 출결 (`/attendance`)
5. 숙제 (`/homework`)
6. 시험/성적 (`/exams`)
7. 상담 (`/counseling`)
8. 수납 (`/payments`)
9. 공지/알림 (`/announcements`)
10. 학생 상세 (`/students`)
11. 도서 대출 (`/library`)

## 4) API 예시
- `POST /api/auth/login`
- `GET /api/announcements`
- `POST /api/books/loan-by-code`

예시:
```bash
curl -i -X POST http://127.0.0.1:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"owner","password":"1234"}'
```

## 5) DB 마이그레이션
- 초기 마이그레이션 SQL: `migrations/001_init.sql`
- 실제 앱 초기화 SQL: `schema.sql`

## 6) Tencent Light Application Server 배포 메모
- Python 런타임 설치 후 `python3 app.py`로 단일 프로세스 실행 가능
- 운영에서는 Nginx reverse proxy + systemd 서비스 구성 권장
- DB는 MVP에서 SQLite 사용, 운영 확장 시 MySQL/PostgreSQL 전환 권장

## 7) 학생 데이터 확장 필드
- `students.user_id` (users와 1:1)
- `student_no`
- `name_ko`, `name_en(optional)`
- `phone`
- `guardian_name`, `guardian_phone`
- `current_class_id`
- `remaining_credits`
- `status` (`active`/`leave`/`ended`)
- `enrolled_at`, `leave_start_date`, `leave_end_date`
- `memo`
