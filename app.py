import json
import os
import sqlite3
import uuid
from datetime import datetime
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lms.db")

ROLE_OWNER = "owner"
ROLE_MANAGER = "manager"
ROLE_TEACHER = "teacher"
ROLE_PARENT = "parent"
ROLE_STUDENT = "student"

ROLE_LABELS = {
    ROLE_OWNER: "원장",
    ROLE_MANAGER: "매니저",
    ROLE_TEACHER: "강사",
    ROLE_PARENT: "학부모",
    ROLE_STUDENT: "학생",
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_pw(pw: str) -> str:
    # 단순 데모용
    import hashlib
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def now():
    return datetime.utcnow().isoformat()


def init_db():
    conn = get_db()
    with open(os.path.join(BASE_DIR, "schema.sql"), "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    cur = conn.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()["c"] == 0:
        users = [
            ("원장", "owner", "owner", "1234"),
            ("매니저", "manager", "manager", "1234"),
            ("강사", "teacher", "teacher", "1234"),
            ("학부모", "parent", "parent", "1234"),
            ("학생", "student", "student", "1234"),
        ]
        for name, username, role, pw in users:
            conn.execute(
                "INSERT INTO users(name, username, password_hash, role, created_at) VALUES(?,?,?,?,?)",
                (name, username, hash_pw(pw), role, now()),
            )
    # 기존 student 역할 사용자에 대한 학생 프로필 보강
    student_users = conn.execute("SELECT id, name FROM users WHERE role=?", (ROLE_STUDENT,)).fetchall()
    for su in student_users:
        exists = conn.execute("SELECT id FROM students WHERE user_id=?", (su["id"],)).fetchone()
        if not exists:
            conn.execute(
                """INSERT INTO students(
                user_id, student_no, name_ko, status, created_at
                ) VALUES(?,?,?,?,?)""",
                (su["id"], f"S{su['id']:04d}", su["name"], "active", now()),
            )
    conn.commit()
    conn.close()


def parse_body(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length) if length > 0 else b""
    ctype = environ.get("CONTENT_TYPE", "")
    if "application/json" in ctype:
        return json.loads(body.decode("utf-8") or "{}")
    return {k: v[0] for k, v in parse_qs(body.decode("utf-8")).items()}


def parse_cookie(cookie):
    out = {}
    if not cookie:
        return out
    for part in cookie.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            out[k] = v
    return out


def current_user(environ):
    cookies = parse_cookie(environ.get("HTTP_COOKIE", ""))
    token = cookies.get("session")
    if not token:
        return None
    conn = get_db()
    row = conn.execute(
        "SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?", (token,)
    ).fetchone()
    conn.close()
    return row


def render_html(title, body, user=None):
    nav = ""
    if user:
        nav = f"""
        <div style='margin-bottom:16px'>
            로그인: {user['name']}({ROLE_LABELS.get(user['role'], user['role'])}) |
            <a href='/dashboard'>대시보드</a> |
            <a href='/users'>사용자</a> |
            <a href='/students'>학생상세</a> |
            <a href='/academics'>학사구조</a> |
            <a href='/attendance'>출결</a> |
            <a href='/homework'>숙제</a> |
            <a href='/exams'>시험/성적</a> |
            <a href='/counseling'>상담/특이사항</a> |
            <a href='/payments'>수납</a> |
            <a href='/announcements'>공지/알림</a> |
            <a href='/library'>도서대출</a> |
            <a href='/logout'>로그아웃</a>
        </div>
        """
    return f"""
    <html><head><meta charset='utf-8'><title>{title}</title></head>
    <body style='font-family:Arial; max-width:1200px; margin:24px auto'>
      <h2>{title}</h2>
      {nav}
      {body}
    </body></html>
    """.encode("utf-8")


def require_login(environ):
    user = current_user(environ)
    if not user:
        return None, redirect('/login')
    return user, None


def redirect(path):
    return "302 Found", [("Location", path)], b""


def has_role(user, roles):
    return user and user["role"] in roles


def json_resp(data, status="200 OK"):
    return status, [("Content-Type", "application/json; charset=utf-8")], json.dumps(data, ensure_ascii=False).encode("utf-8")


def text_resp(text, status="200 OK"):
    return status, [("Content-Type", "text/html; charset=utf-8")], text


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    # 인증 API
    if path == "/api/auth/login" and method == "POST":
        data = parse_body(environ)
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password_hash=?",
            (data.get("username", ""), hash_pw(data.get("password", ""))),
        ).fetchone()
        if not user:
            conn.close()
            status, headers, body = json_resp({"error": "로그인 실패"}, "401 Unauthorized")
            start_response(status, headers)
            return [body]
        token = str(uuid.uuid4())
        conn.execute("INSERT INTO sessions(user_id, token, created_at) VALUES(?,?,?)", (user["id"], token, now()))
        conn.commit()
        conn.close()
        status, headers, body = json_resp({"message": "ok", "role": user["role"]})
        headers.append(("Set-Cookie", f"session={token}; Path=/; HttpOnly"))
        start_response(status, headers)
        return [body]

    if path == "/login":
        if method == "GET":
            html = render_html("LMS 로그인", """
            <form method='post'>
              <div>아이디 <input name='username'></div>
              <div>비밀번호 <input name='password' type='password'></div>
              <button type='submit'>로그인</button>
            </form>
            <p>기본 계정: owner/1234, manager/1234, teacher/1234, parent/1234, student/1234</p>
            """)
            status, headers, body = text_resp(html)
            start_response(status, headers)
            return [body]
        data = parse_body(environ)
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password_hash=?",
            (data.get("username", ""), hash_pw(data.get("password", ""))),
        ).fetchone()
        if not user:
            conn.close()
            html = render_html("LMS 로그인", "<p style='color:red'>로그인 실패</p>")
            status, headers, body = text_resp(html, "401 Unauthorized")
            start_response(status, headers)
            return [body]
        token = str(uuid.uuid4())
        conn.execute("INSERT INTO sessions(user_id, token, created_at) VALUES(?,?,?)", (user["id"], token, now()))
        conn.commit()
        conn.close()
        status, headers, body = redirect('/dashboard')
        headers.append(("Set-Cookie", f"session={token}; Path=/; HttpOnly"))
        start_response(status, headers)
        return [body]

    if path == "/logout":
        status, headers, body = redirect('/login')
        headers.append(("Set-Cookie", "session=; Path=/; Max-Age=0"))
        start_response(status, headers)
        return [body]

    if path == "/":
        status, headers, body = redirect('/dashboard')
        start_response(status, headers)
        return [body]

    user, resp = require_login(environ)
    if resp:
        status, headers, body = resp
        start_response(status, headers)
        return [body]

    # Dashboard
    if path == "/dashboard":
        html = render_html("영어학원 LMS 대시보드", "<p>MVP 관리 화면입니다.</p>", user)
        status, headers, body = text_resp(html)
        start_response(status, headers)
        return [body]

    conn = get_db()

    # 사용자 관리
    if path == "/users":
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            data = parse_body(environ)
            conn.execute(
                "INSERT INTO users(name, username, password_hash, role, created_at) VALUES(?,?,?,?,?)",
                (data.get("name"), data.get("username"), hash_pw(data.get("password", "1234")), data.get("role"), now()),
            )
            conn.commit()
        users = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
        rows = "".join([f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['username']}</td><td>{ROLE_LABELS.get(u['role'],u['role'])}</td></tr>" for u in users])
        form = ""
        if has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            form = """
            <h3>사용자 추가</h3>
            <form method='post'>
            이름<input name='name'> 아이디<input name='username'> 비밀번호<input name='password'>
            역할<select name='role'>
              <option value='owner'>원장</option><option value='manager'>매니저</option><option value='teacher'>강사</option>
              <option value='parent'>학부모</option><option value='student'>학생</option>
            </select><button>저장</button></form>
            """
        html = render_html("학생/학부모/강사 관리(사용자 기반)", form + f"<table border='1'><tr><th>ID</th><th>이름</th><th>아이디</th><th>역할</th></tr>{rows}</table>", user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path == "/students":
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            d = parse_body(environ)
            student_user_id = d.get("user_id")
            exists = conn.execute("SELECT id FROM students WHERE user_id=?", (student_user_id,)).fetchone()
            if exists:
                conn.execute(
                    """UPDATE students SET
                    student_no=?, name_ko=?, name_en=?, phone=?, guardian_name=?, guardian_phone=?,
                    current_class_id=?, remaining_credits=?, status=?, enrolled_at=?, leave_start_date=?, leave_end_date=?, memo=?, updated_at=?
                    WHERE user_id=?""",
                    (
                        d.get("student_no"), d.get("name_ko"), d.get("name_en"), d.get("phone"), d.get("guardian_name"), d.get("guardian_phone"),
                        d.get("current_class_id"), d.get("remaining_credits") or 0, d.get("status") or "active", d.get("enrolled_at"), d.get("leave_start_date"), d.get("leave_end_date"), d.get("memo"), now(), student_user_id,
                    ),
                )
            else:
                conn.execute(
                    """INSERT INTO students(
                    user_id, student_no, name_ko, name_en, phone, guardian_name, guardian_phone,
                    current_class_id, remaining_credits, status, enrolled_at, leave_start_date, leave_end_date, memo, created_at, updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        student_user_id, d.get("student_no"), d.get("name_ko"), d.get("name_en"), d.get("phone"), d.get("guardian_name"), d.get("guardian_phone"),
                        d.get("current_class_id"), d.get("remaining_credits") or 0, d.get("status") or "active", d.get("enrolled_at"), d.get("leave_start_date"), d.get("leave_end_date"), d.get("memo"), now(), now(),
                    ),
                )
            conn.commit()

        students = conn.execute(
            """SELECT s.*, u.username FROM students s
            JOIN users u ON u.id=s.user_id
            ORDER BY s.id DESC"""
        ).fetchall()
        student_users = conn.execute("SELECT id, name, username FROM users WHERE role='student' ORDER BY id DESC").fetchall()
        html = render_html("학생 상세 정보(운영형 필드)", f"""
        <form method='post'>
          학생 사용자ID <input name='user_id'> 학생번호 <input name='student_no'> 한글이름 <input name='name_ko'> 영문이름 <input name='name_en'><br>
          연락처 <input name='phone'> 보호자명 <input name='guardian_name'> 보호자 연락처 <input name='guardian_phone'><br>
          현재반ID <input name='current_class_id'> 남은크레딧 <input name='remaining_credits'> 상태
          <select name='status'><option value='active'>정상</option><option value='leave'>휴학</option><option value='ended'>종료</option></select><br>
          입학일 <input name='enrolled_at' placeholder='2026-03-01'> 휴학시작 <input name='leave_start_date'> 휴학종료 <input name='leave_end_date'><br>
          메모 <input name='memo' style='width:400px'> <button>저장/수정</button>
        </form>
        <h4>학생 사용자 목록</h4><pre>{[dict(r) for r in student_users]}</pre>
        <h4>학생 상세</h4><pre>{[dict(r) for r in students]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    # 학사 구조
    if path == "/academics":
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            data = parse_body(environ)
            typ = data.get("type")
            if typ == "course":
                conn.execute("INSERT INTO courses(name, created_at) VALUES(?,?)", (data.get("name"), now()))
            elif typ == "level":
                conn.execute("INSERT INTO levels(course_id, name, created_at) VALUES(?,?,?)", (data.get("course_id"), data.get("name"), now()))
            elif typ == "class":
                conn.execute("INSERT INTO classes(course_id, level_id, name, teacher_id, created_at) VALUES(?,?,?,?,?)", (data.get("course_id"), data.get("level_id"), data.get("name"), data.get("teacher_id"), now()))
            elif typ == "schedule":
                conn.execute("INSERT INTO schedules(class_id, day_of_week, start_time, end_time, created_at) VALUES(?,?,?,?,?)", (data.get("class_id"), data.get("day_of_week"), data.get("start_time"), data.get("end_time"), now()))
            conn.commit()
        courses = conn.execute("SELECT * FROM courses").fetchall()
        levels = conn.execute("SELECT * FROM levels").fetchall()
        classes = conn.execute("SELECT c.*,u.name as teacher_name FROM classes c LEFT JOIN users u ON c.teacher_id=u.id").fetchall()
        schedules = conn.execute("SELECT * FROM schedules").fetchall()
        html = render_html("코스/레벨/반/시간표 관리", f"""
        <h3>등록</h3>
        <form method='post'>코스 <input name='name'><input type='hidden' name='type' value='course'><button>추가</button></form>
        <form method='post'>레벨명 <input name='name'> 코스ID <input name='course_id'><input type='hidden' name='type' value='level'><button>추가</button></form>
        <form method='post'>반명 <input name='name'> 코스ID <input name='course_id'> 레벨ID <input name='level_id'> 강사ID <input name='teacher_id'><input type='hidden' name='type' value='class'><button>추가</button></form>
        <form method='post'>시간표 반ID <input name='class_id'> 요일 <input name='day_of_week'> 시작 <input name='start_time'> 종료 <input name='end_time'><input type='hidden' name='type' value='schedule'><button>추가</button></form>
        <h4>코스</h4><pre>{[dict(r) for r in courses]}</pre>
        <h4>레벨</h4><pre>{[dict(r) for r in levels]}</pre>
        <h4>반</h4><pre>{[dict(r) for r in classes]}</pre>
        <h4>시간표</h4><pre>{[dict(r) for r in schedules]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    # 출결
    if path == "/attendance":
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            conn.execute("INSERT INTO attendance(class_id, student_id, lesson_date, status, note, created_by, created_at) VALUES(?,?,?,?,?,?,?)",
                         (d.get("class_id"), d.get("student_id"), d.get("lesson_date"), d.get("status"), d.get("note"), user["id"], now()))
            if d.get("status") == "absent":
                conn.execute("INSERT INTO notifications(type, target_user_id, payload, created_at) VALUES(?,?,?,?)",
                             ("absence", d.get("student_id"), json.dumps({"student_id": d.get("student_id"), "date": d.get("lesson_date")}, ensure_ascii=False), now()))
            conn.commit()
        rows = conn.execute("SELECT * FROM attendance ORDER BY id DESC LIMIT 200").fetchall()
        html = render_html("출결 관리", f"""
        <form method='post'>반ID<input name='class_id'> 학생ID<input name='student_id'> 날짜<input name='lesson_date' placeholder='2026-03-06'>
        상태<select name='status'><option value='present'>출석</option><option value='late'>지각</option><option value='absent'>결석</option><option value='makeup'>보강</option></select>
        메모<input name='note'><button>저장</button></form>
        <pre>{[dict(r) for r in rows]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path == "/homework":
        if method == "POST":
            d = parse_body(environ)
            typ = d.get("type")
            if typ == "homework" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
                conn.execute("INSERT INTO homework(class_id, title, due_date, created_by, created_at) VALUES(?,?,?,?,?)", (d.get("class_id"), d.get("title"), d.get("due_date"), user["id"], now()))
                conn.execute("INSERT INTO notifications(type, target_user_id, payload, created_at) VALUES(?,?,?,?)", ("homework", None, json.dumps({"title": d.get("title")}, ensure_ascii=False), now()))
            elif typ == "submission" and has_role(user, [ROLE_STUDENT]):
                conn.execute("INSERT INTO homework_submissions(homework_id, student_id, submitted, submitted_at) VALUES(?,?,?,?)", (d.get("homework_id"), user["id"], 1, now()))
            elif typ == "feedback" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
                conn.execute("UPDATE homework_submissions SET feedback=?, feedback_by=?, feedback_at=? WHERE id=?", (d.get("feedback"), user["id"], now(), d.get("submission_id")))
            conn.commit()
        hw = conn.execute("SELECT * FROM homework ORDER BY id DESC").fetchall()
        sub = conn.execute("SELECT * FROM homework_submissions ORDER BY id DESC").fetchall()
        html = render_html("숙제 관리", f"""
        <form method='post'><input type='hidden' name='type' value='homework'>반ID<input name='class_id'> 제목<input name='title'> 마감일<input name='due_date'><button>등록</button></form>
        <form method='post'><input type='hidden' name='type' value='submission'>숙제ID<input name='homework_id'><button>학생 제출</button></form>
        <form method='post'><input type='hidden' name='type' value='feedback'>제출ID<input name='submission_id'> 피드백<input name='feedback'><button>피드백 저장</button></form>
        <h4>숙제</h4><pre>{[dict(r) for r in hw]}</pre>
        <h4>제출/피드백</h4><pre>{[dict(r) for r in sub]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path == "/exams":
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            typ = d.get("type")
            if typ == "exam":
                conn.execute("INSERT INTO exams(class_id, name, exam_date, report, linked_book_id, created_at) VALUES(?,?,?,?,?,?)", (d.get("class_id"), d.get("name"), d.get("exam_date"), d.get("report"), d.get("linked_book_id"), now()))
            elif typ == "score":
                conn.execute("INSERT INTO exam_scores(exam_id, student_id, score, created_at) VALUES(?,?,?,?)", (d.get("exam_id"), d.get("student_id"), d.get("score"), now()))
            conn.commit()
        exams = conn.execute("SELECT * FROM exams ORDER BY id DESC").fetchall()
        scores = conn.execute("SELECT * FROM exam_scores ORDER BY id DESC").fetchall()
        html = render_html("시험/성적 관리", f"""
        <form method='post'><input type='hidden' name='type' value='exam'>반ID<input name='class_id'> 시험명<input name='name'> 날짜<input name='exam_date'> 리포트<input name='report'> 연계도서ID<input name='linked_book_id'><button>시험 등록</button></form>
        <form method='post'><input type='hidden' name='type' value='score'>시험ID<input name='exam_id'> 학생ID<input name='student_id'> 점수<input name='score'><button>점수 등록</button></form>
        <h4>시험</h4><pre>{[dict(r) for r in exams]}</pre>
        <h4>점수</h4><pre>{[dict(r) for r in scores]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path == "/counseling":
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            conn.execute("INSERT INTO counseling(student_id, parent_id, memo, is_special_note, created_by, created_at) VALUES(?,?,?,?,?,?)", (d.get("student_id"), d.get("parent_id"), d.get("memo"), 1 if d.get("is_special_note") else 0, user["id"], now()))
            conn.commit()
        rows = conn.execute("SELECT * FROM counseling ORDER BY id DESC").fetchall()
        html = render_html("상담 기록/학생 특이사항", f"""
        <form method='post'>학생ID<input name='student_id'> 학부모ID<input name='parent_id'> 메모<input name='memo'> 특이사항<input type='checkbox' name='is_special_note' value='1'><button>저장</button></form>
        <pre>{[dict(r) for r in rows]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path == "/payments":
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            d = parse_body(environ)
            conn.execute("INSERT INTO payments(student_id, paid_date, amount, package_hours, remaining_classes, created_at) VALUES(?,?,?,?,?,?)", (d.get("student_id"), d.get("paid_date"), d.get("amount"), d.get("package_hours"), d.get("remaining_classes"), now()))
            conn.commit()
        rows = conn.execute("SELECT * FROM payments ORDER BY id DESC").fetchall()
        html = render_html("수납 기록", f"""
        <form method='post'>학생ID<input name='student_id'> 결제일<input name='paid_date'> 금액<input name='amount'> 패키지시간<input name='package_hours'> 잔여수업수<input name='remaining_classes'><button>저장</button></form>
        <pre>{[dict(r) for r in rows]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path == "/announcements":
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            conn.execute("INSERT INTO announcements(title, content, created_by, created_at) VALUES(?,?,?,?)", (d.get("title"), d.get("content"), user["id"], now()))
            conn.commit()
        rows = conn.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
        noti = conn.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50").fetchall()
        html = render_html("공지/알림 구조", f"""
        <form method='post'>제목<input name='title'> 내용<input name='content'><button>공지 등록</button></form>
        <h4>공지</h4><pre>{[dict(r) for r in rows]}</pre>
        <h4>알림 데이터(숙제/결석)</h4><pre>{[dict(r) for r in noti]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path == "/library":
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            typ = d.get("type")
            if typ == "book":
                conn.execute("INSERT INTO books(code, title, status, created_at) VALUES(?,?,?,?)", (d.get("code"), d.get("title"), "available", now()))
            elif typ == "loan":
                book = conn.execute("SELECT * FROM books WHERE code=?", (d.get("code"),)).fetchone()
                if book:
                    conn.execute("UPDATE books SET status='borrowed' WHERE id=?", (book["id"],))
                    conn.execute("INSERT INTO book_loans(book_id, student_id, loaned_at, handled_by, created_at) VALUES(?,?,?,?,?)", (book["id"], d.get("student_id"), now(), user["id"], now()))
            elif typ == "return":
                book = conn.execute("SELECT * FROM books WHERE code=?", (d.get("code"),)).fetchone()
                if book:
                    conn.execute("UPDATE books SET status='available' WHERE id=?", (book["id"],))
                    conn.execute("UPDATE book_loans SET returned_at=? WHERE book_id=? AND returned_at IS NULL", (now(), book["id"]))
            conn.commit()
        books = conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
        loans = conn.execute("SELECT * FROM book_loans ORDER BY id DESC").fetchall()
        html = render_html("도서 대출 관리", f"""
        <form method='post'><input type='hidden' name='type' value='book'>코드<input name='code'> 제목<input name='title'><button>도서 등록</button></form>
        <form method='post'><input type='hidden' name='type' value='loan'>코드입력<input name='code'> 학생ID<input name='student_id'><button>대여 처리</button></form>
        <form method='post'><input type='hidden' name='type' value='return'>코드입력<input name='code'><button>반납 처리</button></form>
        <h4>도서</h4><pre>{[dict(r) for r in books]}</pre>
        <h4>대출/반납 이력</h4><pre>{[dict(r) for r in loans]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    # 기본 API 샘플
    if path == "/api/announcements" and method == "GET":
        rows = conn.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
        conn.close()
        status, headers, body = json_resp([dict(r) for r in rows])
        start_response(status, headers)
        return [body]

    if path == "/api/books/loan-by-code" and method == "POST":
        d = parse_body(environ)
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            conn.close()
            status, headers, body = json_resp({"error": "권한 없음"}, "403 Forbidden")
            start_response(status, headers)
            return [body]
        book = conn.execute("SELECT * FROM books WHERE code=?", (d.get("code"),)).fetchone()
        if not book:
            conn.close()
            status, headers, body = json_resp({"error": "도서 없음"}, "404 Not Found")
            start_response(status, headers)
            return [body]
        conn.execute("UPDATE books SET status='borrowed' WHERE id=?", (book["id"],))
        conn.execute("INSERT INTO book_loans(book_id, student_id, loaned_at, handled_by, created_at) VALUES(?,?,?,?,?)", (book["id"], d.get("student_id"), now(), user["id"], now()))
        conn.commit()
        conn.close()
        status, headers, body = json_resp({"message": "대여 완료"})
        start_response(status, headers)
        return [body]

    conn.close()
    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
    return ["Not Found".encode("utf-8")]


if __name__ == "__main__":
    init_db()
    with make_server("0.0.0.0", 8000, app) as httpd:
        print("LMS 서버 실행: http://127.0.0.1:8000")
        httpd.serve_forever()
