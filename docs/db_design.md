# RTWEB LMS DB Design Baseline (SQLite actual schema)

본 문서는 **현재 실제 `lms.db` + `schema.sql` + `migrations/*`**를 기준으로 작성했다.
추측 컬럼/테이블은 포함하지 않는다.

## 1) 전체 구조 요약 (실제 테이블)

- 인증/권한: `users`, `sessions`
- 학생 프로필: `students`
- 교사 프로필: `teachers`
- 학사 마스터: `courses`, `levels`, `classes`, `classrooms`, `time_slots`
- 운영 스케줄: `schedules`
- 학습 운영: `attendance`, `homework`, `homework_submissions`, `exams`, `exam_scores`, `counseling`, `payments`
- 도서: `books`, `book_loans`
- 알림/공지: `announcements`, `notifications`
- 로그: `app_logs`

---

## 2) 테이블별 역할/필수필드/FK/사용 기능

> 필수 필드는 SQLite `NOT NULL` 기준(`*`) + 운영상 사실상 필수로 구분.

### users
- 역할: 로그인 계정 + RBAC + 교사 유형(`teacher_type`)
- 주요 필드: `id*`, `name*`, `username*`, `password_hash*`, `role*`, `teacher_type`, `created_at*`
- FK: 없음
- 사용 화면/기능: 로그인, 권한체크, 모든 화면의 사용자 참조
- 이슈: parent/teacher 전용 프로필 테이블이 없음(학생만 `students` 분리)

### teachers
- 역할: 교사 프로필(Source of truth: 교사 표시/유형)
- 주요 필드: `id*`, `user_id*`, `teacher_type*`, `memo`, `created_at*`, `updated_at`
- FK: `user_id -> users.id`
- 사용 화면/기능: 마스터데이터 교사 목록, 스케줄/도서 교사 선택
- 이슈: 과거 DB에는 미존재 가능(런타임 보정 및 backfill 필요)

### sessions
- 역할: 세션 토큰
- 주요 필드: `id*`, `user_id*`, `token*`, `created_at*`
- FK: `user_id -> users.id`
- 사용 기능: `/login`, `/api/auth/login`, `require_login`

### students
- 역할: 학생 운영 프로필(Source of truth: 학생 운영 정보)
- 주요 필드: `id*`, `user_id*`, `student_no`, `name_ko*`, `name_en`, `phone`, `guardian_name`, `guardian_phone`, `current_class_id`, `remaining_credits`, `status*`, `enrolled_at`, `leave_start_date`, `leave_end_date`, `memo`
- FK: `user_id -> users.id`, `current_class_id -> classes.id`
- 사용 화면: 학생관리, 학생상세, 출결/숙제/수납/도서 picker
- 이슈: 학부모 연결이 `guardian_name` 텍스트 기반(정규화 부족)

### courses
- 역할: 코스 마스터
- 주요 필드: `id*`, `name*`, `created_at*`
- FK: 없음
- 사용 화면: 마스터데이터, 스케줄/반 조회 조인

### levels
- 역할: 레벨 마스터
- 주요 필드: `id*`, `course_id*`, `name*`, `created_at*`
- FK: `course_id -> courses.id`
- 사용 화면: 마스터데이터, 스케줄/반 조회 조인

### classes
- 역할: 반 마스터
- 주요 필드: `id*`, `course_id`, `level_id`, `name*`, `teacher_id`, `foreign_teacher_id`, `chinese_teacher_id`, `created_at*`
- FK: `course_id -> courses.id`, `level_id -> levels.id`, `teacher_id -> users.id` (foreign/chinese는 컬럼 존재, FK는 DB마다 불완전 가능)
- 사용 화면: 반 목록/상세, 스케줄 편성 기준
- 이슈: 학생-반 이력 구조 없음(현재 `students.current_class_id` 단일 포인터)

### classrooms
- 역할: 교실 마스터
- 주요 필드: `id*`, `name*`, `room_code`, `room_name`, `status`, `memo`, `created_at*`
- FK: 없음
- 사용 화면: 마스터데이터, 스케줄 교실 선택
- 이슈: `name`와 `room_name` 중복 의미

### time_slots
- 역할: 시간 슬롯 마스터
- 주요 필드: `id*`, `label*`, `start_time*`, `end_time*`, `created_at*`
- FK: 없음
- 사용 화면: 마스터데이터, 스케줄 등록 슬롯 선택

### schedules
- 역할: 주간 시간표(운영 배치 Source of truth)
- 주요 필드: `id*`, `class_id*`, `day_of_week*`, `start_time`, `end_time`, `classroom`, `status`, `note`, `teacher_id`, `room_id`, `foreign_teacher_id`, `chinese_teacher_id`, `substitute_foreign_teacher_id`, `substitute_chinese_teacher_id`, `substitute_reason`, `created_at*`
- FK: `class_id -> classes.id`, `teacher_id -> users.id` (room_id/foreign/chinese/substitute FK는 DB 상태에 따라 미적용 가능)
- 사용 화면: 스케줄 메인
- 이슈: 시간 기준이 `start/end`와 `time_slots` 이중 구조

### attendance
- 역할: 출결 기록
- 주요 필드: `id*`, `class_id*`, `student_id*`, `lesson_date*`, `status*`, `note`, `created_by*`, `created_at*`
- FK: `class_id -> classes.id`, `student_id -> users.id`, `created_by -> users.id`
- 사용 화면: 출결, 학생상세
- 이슈: 세션(수업회차) 엔티티 부재

### homework / homework_submissions
- 역할: 숙제 과제 / 제출 및 피드백
- 주요 필드: 
  - homework: `id*`, `class_id*`, `title*`, `due_date`, `created_by*`
  - submissions: `id*`, `homework_id*`, `student_id*`, `submitted`, `submitted_at`, `feedback`, `feedback_by`, `feedback_at`
- FK: 과제-반, 제출-과제, 제출-학생
- 사용 화면: 숙제, 학생상세

### exams / exam_scores
- 역할: 시험 / 성적
- 주요 필드:
  - exams: `id*`, `class_id*`, `name*`, `exam_date`, `report`, `linked_book_id`
  - exam_scores: `id*`, `exam_id*`, `student_id*`, `score*`
- FK: 시험-반, 점수-시험/학생
- 사용 화면: 시험/성적, 학생상세
- 이슈: 점수 스케일 표준(100점/5점) 메타 없음

### counseling
- 역할: 상담/특이사항
- 주요 필드: `id*`, `student_id*`, `parent_id`, `memo*`, `is_special_note`, `created_by*`, `created_at*`
- FK: 학생/학부모/작성자 -> users
- 사용 화면: 상담, 학생상세
- 이슈: parent_id 실사용과 guardian_name 텍스트 모델 혼재

### payments
- 역할: 수납 기록
- 주요 필드: `id*`, `student_id*`, `paid_date*`, `amount*`, `package_hours`, `remaining_classes`, `created_at*`
- FK: `student_id -> users.id`
- 사용 화면: 수납, 학생상세
- 이슈: 결제수단/영수증/트랜잭션 상태 부재

### books / book_loans
- 역할: 도서 마스터 / 대출 이력
- 주요 필드:
  - books: `id*`, `code*`, `title*`, `status*`, `created_at*`
  - loans: `id*`, `book_id*`, `student_id*`, `loaned_at*`, `returned_at`, `handled_by*`, `created_at*`
- FK: loan -> books/users
- 사용 화면: 도서대출, 학생상세

### announcements / notifications
- 역할: 공지 / 이벤트 알림 저장
- 주요 필드:
  - announcements: `id*`, `title*`, `content*`, `created_by*`, `created_at*`
  - notifications: `id*`, `type*`, `target_user_id`, `payload*`, `created_at*`
- FK: 작성자/타겟 -> users
- 사용 화면: 공지/알림, 출결/숙제에서 생성

### app_logs
- 역할: 서버 검증/예외 로그
- 주요 필드: `id*`, `level*`, `route`, `user_id`, `message*`, `detail`, `created_at*`
- FK: `user_id -> users.id`
- 사용 화면: 시스템로그(`/logs`)

---

## 3) 데이터 트리 / 관계 구조 (텍스트)

- `users` (계정/권한 루트)
  - 1:1 `students.user_id`
  - 1:N `sessions.user_id`
  - 1:N (`classes.teacher_id`, `schedules.teacher_id`, `attendance.created_by`, `homework.created_by`, `counseling.created_by`, `announcements.created_by`, `book_loans.handled_by`, `app_logs.user_id`)
- `courses` -> `levels` -> `classes`
- `classes` -> `schedules`, `attendance`, `homework`, `exams`
- `students` -> `attendance`(via `users.id`), `homework_submissions`, `exam_scores`, `payments`, `book_loans`, `counseling`
- `books` -> `book_loans`; `exams.linked_book_id -> books`
- `classrooms` / `time_slots` -> `schedules` (부분 참조)

---

## 4) Source of truth 표준

- 로그인/권한: `users`
- 학생 검색/운영 프로필: `students` (계정 연결은 `students.user_id -> users.id`)
- 교사 검색/운영 프로필: `teachers` + `users` 조인 (`teachers.user_id -> users.id`)
- 반 목록/기본 구조: `classes` (+ `courses`/`levels` 조인)
- 시간표: `schedules` 중심, 표시 보강은 `classes/classrooms/users` 조인
- 출결: `attendance`
- 숙제: `homework`, `homework_submissions`
- 시험/성적: `exams`, `exam_scores`
- 상담: `counseling`
- 수납: `payments`
- 도서대출: `books`, `book_loans`
- 시스템 로그: `app_logs`

**통일 제안**
- 학생 식별자는 운영 화면에서 `students.id`, 이벤트/기록 저장은 `users.id`로 혼용됨 → 변환 규칙을 공통 유틸로 고정(이미 일부 구현됨, 전면 일관화 필요).

---

## 5) 현재 문제점 목록

1. **학생-학부모 연결 정규화 부족**: `guardian_name` 문자열 매칭에 의존.
2. **교사 모델 이행 단계**: `teachers` 테이블이 도입됐지만 기존 `users.teacher_type`와 이중 관리 구간이 있어 동기화 규칙이 필요.
3. **스케줄 시간 이중 구조**: `schedules.start/end` vs `time_slots` 동시 존재.
4. **수업 회차(session) 부재**: 출결/숙제/시험이 동일 수업 인스턴스를 공유하지 못함.
5. **FK 일관성 격차**: 코드상 컬럼은 있으나 실제 DB마다 FK/컬럼 누락 가능(런타임 ALTER 보정 의존).
6. **notification_logs 상세 부재**: 발송 결과/채널/재시도 이력 없음.
7. **audit 범위 제한**: `app_logs`는 존재하지만 데이터 변경 감사(audit trail) 수준은 아님.

---

## 6) 누락 필드/관계 분석 (지금/나중/불필요)

### 지금 필요한 것(권장 1차)
- `users.preferred_language` (i18n 개인화)
- `notifications` 확장 또는 `notification_logs` 신설 (`channel`, `status`, `sent_at`, `error`)
- 스케줄 기준 통일용 `schedules.time_slot_id` (선택형 UX와 DB 정합)

### 나중에 필요한 것(권장 2~3차)
- `teachers` 상세 확장(자격/소속/언어/활성상태)
- `student_parents` 관계 테이블
- `class_enrollments` (학생-반 이력)
- `class_sessions` / `session_student_records` (수업 회차 중심 출결/학습 기록)
- `audit_logs`(행 단위 변경 이력)

### 아직 불필요/보류
- 대규모 시험엔진 전용 테이블(문항은행/랜덤출제 본격화 전)
- 외부 연동 전용 webhook/event bus 테이블

---

## 7) 신규 기능 추가 전 검증 절차 (Codex Preflight)

1. `PRAGMA table_info` / `PRAGMA foreign_key_list`로 실제 컬럼/FK 확인
2. 해당 기능의 기존 Source of truth 확인(본 문서 기준)
3. 필요한 필드/관계 존재 여부 점검
4. 누락 시 migration 필요 여부 판단(기존 데이터 호환성 포함)
5. 영향 라우트/쿼리 목록화(`SELECT/INSERT/UPDATE/JOIN` 검색)
6. 구현 후 최소 라우트 smoke test + 무결성 점검 스크립트 실행
7. 결과를 PR에 체크리스트로 기록

---

## 8) 추천 마이그레이션 단계(계획만)

### 1차 (구조 정합)
- `users.preferred_language` 추가
- `schedules.time_slot_id` 추가 + 기존 `start/end`와 병행
- `notification_logs` 신설

### 2차 (관계 정규화)
- `student_parents` 도입, `guardian_name` 의존 축소
- `class_enrollments` 도입(현재반 + 이력)

### 3차 (운영 단위 고도화)
- `class_sessions`, `session_student_records` 도입
- 출결/숙제/시험을 session 기준으로 연결

### 4차 (감사/운영)
- `audit_logs` 도입(누가/언제/무엇 변경)

