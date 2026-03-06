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

CURRENT_LANG = "ko"

LANG_LABELS = {"ko": "한국어", "en": "English", "zh": "中文"}

NAV_LABELS = {
    "dashboard": "menu.dashboard",
    "users": "menu.users",
    "students": "menu.students",
    "academics": "menu.academics",
    "attendance": "menu.attendance",
    "homework": "menu.homework",
    "exams": "menu.exams",
    "counseling": "menu.counseling",
    "payments": "menu.payments",
    "announcements": "menu.announcements",
    "library": "menu.library",
    "logout": "common.logout",
    "login_as": "common.login_as",
    "lang": "common.language",
}


I18N_TEXTS = {
    "ko": {
        "menu.dashboard": "대시보드", "menu.users": "사용자", "menu.students": "학생관리", "menu.academics": "학사구조",
        "menu.attendance": "출결", "menu.homework": "숙제", "menu.exams": "시험/성적", "menu.counseling": "상담/특이사항",
        "menu.payments": "수납", "menu.announcements": "공지/알림", "menu.library": "도서대출",
        "common.login_as": "로그인", "common.language": "언어", "common.login": "로그인", "common.logout": "로그아웃",
        "common.save": "저장", "common.edit": "수정", "common.delete": "삭제", "common.search": "검색",
        "common.no_data": "데이터 없음", "common.selected": "선택됨", "common.forbidden": "접근 권한이 없습니다",
        "login.title": "LMS 로그인", "login.username": "아이디", "login.password": "비밀번호", "login.failed": "로그인 실패",
        "status.active": "정상", "status.leave": "휴학", "status.ended": "종료",
    },
    "en": {
        "menu.dashboard": "Dashboard", "menu.users": "Users", "menu.students": "Students", "menu.academics": "Academics",
        "menu.attendance": "Attendance", "menu.homework": "Homework", "menu.exams": "Exams/Scores", "menu.counseling": "Counseling",
        "menu.payments": "Payments", "menu.announcements": "Announcements", "menu.library": "Library",
        "common.login_as": "Signed in", "common.language": "Language", "common.login": "Login", "common.logout": "Logout",
        "common.save": "Save", "common.edit": "Edit", "common.delete": "Delete", "common.search": "Search",
        "common.no_data": "No Data", "common.selected": "Selected", "common.forbidden": "Forbidden",
        "login.title": "LMS Login", "login.username": "Username", "login.password": "Password", "login.failed": "Login failed",
        "status.active": "Active", "status.leave": "Leave", "status.ended": "Ended",
    },
    "zh": {
        "menu.dashboard": "仪表盘", "menu.users": "用户", "menu.students": "学生管理", "menu.academics": "学术结构",
        "menu.attendance": "考勤", "menu.homework": "作业", "menu.exams": "考试/成绩", "menu.counseling": "咨询/备注",
        "menu.payments": "收费", "menu.announcements": "公告/通知", "menu.library": "图书借阅",
        "common.login_as": "当前登录", "common.language": "语言", "common.login": "登录", "common.logout": "退出登录",
        "common.save": "保存", "common.edit": "编辑", "common.delete": "删除", "common.search": "搜索",
        "common.no_data": "无数据", "common.selected": "已选择", "common.forbidden": "无权限",
        "login.title": "LMS 登录", "login.username": "账号", "login.password": "密码", "login.failed": "登录失败",
        "status.active": "正常", "status.leave": "休学", "status.ended": "结束",
    },
}


NAV_PATHS = {
    "dashboard": "/dashboard",
    "users": "/users",
    "students": "/students",
    "academics": "/academics",
    "attendance": "/attendance",
    "homework": "/homework",
    "exams": "/exams",
    "counseling": "/counseling",
    "payments": "/payments",
    "announcements": "/announcements",
    "library": "/library",
}

ROLE_MENU_KEYS = {
    ROLE_OWNER: ["dashboard", "users", "students", "academics", "attendance", "homework", "exams", "counseling", "payments", "announcements", "library"],
    ROLE_MANAGER: ["dashboard", "students", "academics", "attendance", "homework", "exams", "counseling", "payments", "announcements", "library"],
    ROLE_TEACHER: ["dashboard", "students", "attendance", "homework", "exams", "counseling", "announcements", "library"],
    ROLE_PARENT: ["dashboard", "students", "attendance", "homework", "exams", "payments", "announcements"],
    ROLE_STUDENT: ["dashboard", "students", "attendance", "homework", "exams", "announcements"],
}


def t(key, lang=None):
    lang = lang or CURRENT_LANG
    table = I18N_TEXTS.get(lang, I18N_TEXTS["ko"])
    return table.get(key, I18N_TEXTS["ko"].get(key, key))


def menu_t(key, lang=None):
    token = NAV_LABELS.get(key, key)
    return t(token, lang)


def status_t(status, lang=None):
    return t(f"status.{status}", lang)


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


def parse_query(environ):
    return {k: v[0] for k, v in parse_qs(environ.get("QUERY_STRING", "")).items()}


def get_lang(environ):
    q = parse_query(environ)
    lang = q.get("lang", "").strip().lower()
    if lang in ("ko", "en", "zh"):
        return lang
    cookies = parse_cookie(environ.get("HTTP_COOKIE", ""))
    cookie_lang = (cookies.get("lang") or "").strip().lower()
    if cookie_lang in ("ko", "en", "zh"):
        return cookie_lang
    return "ko"


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


def render_html(title, body, user=None, lang=None):
    lang = lang or CURRENT_LANG
    nav = ""
    if user:
        lang_options = "".join([
            f"<option value='{code}' {'selected' if lang == code else ''}>{label}</option>"
            for code, label in LANG_LABELS.items()
        ])
        keys = ROLE_MENU_KEYS.get(user["role"], ["dashboard"])
        menu_links = " | ".join([f"<a href='{NAV_PATHS[k]}?lang={lang}'>{menu_t(k, lang)}</a>" for k in keys])
        nav = f"""
        <div style='margin-bottom:16px'>
            {menu_t('login_as', lang)}: {user['name']}({ROLE_LABELS.get(user['role'], user['role'])}) |
            {menu_links} |
            <a href='/logout'>{menu_t('logout', lang)}</a>
            <span style='margin-left:10px'>{menu_t('lang', lang)}:</span>
            <select onchange="const u=new URL(window.location.href);u.searchParams.set('lang', this.value);window.location=u.toString();">
              {lang_options}
            </select>
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


def route_allowed(user, route_key):
    if not user:
        return False
    return route_key in ROLE_MENU_KEYS.get(user["role"], [])


def forbidden_html(user, msg=None):
    if msg is None:
        msg = t("common.forbidden")
    html = render_html("403 Forbidden", f"<p style='color:red'>{msg}</p>", user)
    return "403 Forbidden", [("Content-Type", "text/html; charset=utf-8")], html


def forbidden_json(msg="권한 없음"):
    return json_resp({"error": msg}, "403 Forbidden")


def can_view_student_row(user, st):
    if user["role"] in (ROLE_OWNER, ROLE_MANAGER):
        return True
    if user["role"] == ROLE_TEACHER:
        return st["current_class_teacher_id"] == user["id"]
    if user["role"] == ROLE_PARENT:
        return (st["guardian_name"] or "") == user["name"]
    if user["role"] == ROLE_STUDENT:
        return st["user_id"] == user["id"]
    return False


def json_resp(data, status="200 OK"):
    return status, [("Content-Type", "application/json; charset=utf-8")], json.dumps(data, ensure_ascii=False).encode("utf-8")


def text_resp(text, status="200 OK"):
    return status, [("Content-Type", "text/html; charset=utf-8")], text


def fetch_student_candidates(conn, keyword, limit=10):
    kw = (keyword or "").strip()
    if not kw:
        return []
    like = f"%{kw}%"
    return conn.execute(
        """SELECT id, student_no, name_ko, phone FROM students
        WHERE name_ko LIKE ? OR student_no LIKE ? OR phone LIKE ?
        ORDER BY id DESC LIMIT ?""",
        (like, like, like, limit),
    ).fetchall()


def fetch_class_candidates(conn, keyword, limit=10):
    kw = (keyword or "").strip()
    if not kw:
        return []
    like = f"%{kw}%"
    return conn.execute(
        """SELECT c.id, c.name, COALESCE(co.name, '') AS course_name
        FROM classes c
        LEFT JOIN courses co ON co.id=c.course_id
        WHERE c.name LIKE ? OR co.name LIKE ?
        ORDER BY c.id DESC LIMIT ?""",
        (like, like, limit),
    ).fetchall()


def fetch_teacher_candidates(conn, keyword, limit=10):
    kw = (keyword or "").strip()
    if not kw:
        return []
    like = f"%{kw}%"
    return conn.execute(
        """SELECT id, name, username FROM users
        WHERE role='teacher' AND (name LIKE ? OR username LIKE ?)
        ORDER BY id DESC LIMIT ?""",
        (like, like, limit),
    ).fetchall()


def render_picker_block(title, search_name, search_value, selected_name, selected_id, selected_label, candidates, base_path, lang, query_keep=None):
    query_keep = query_keep or {}
    hidden = "".join([f"<input type='hidden' name='{k}' value='{v}'>" for k, v in query_keep.items() if v not in (None, "")])
    cand_rows = ""
    for c in candidates:
        cid = c['id']
        label = c.get('label', '') if isinstance(c, dict) else ''
        if not label:
            if 'student_no' in c.keys():
                label = f"{c['name_ko']} ({c['student_no'] or '-'}, {c['phone'] or '-'})"
            elif 'course_name' in c.keys():
                label = f"{c['name']} / {c['course_name'] or '-'}"
            else:
                label = f"{c['name']} ({c['username']})"
        qp = "&".join([f"{k}={v}" for k, v in query_keep.items() if v not in (None, "")])
        sep = "&" if qp else ""
        cand_rows += f"<li><a href='{base_path}?lang={lang}{sep}{qp}&{selected_name}={cid}'>{label}</a></li>"
    return f"""
    <div style='border:1px solid #ddd; padding:8px; margin:8px 0'>
      <strong>{title}</strong><br>
      <form method='get' style='margin:6px 0'>
        <input type='hidden' name='lang' value='{lang}'>
        {hidden}
        <input name='{search_name}' value='{search_value or ''}' placeholder='search'>
        <button>{t("common.search")}</button>
      </form>
      <div>{t("common.selected")}: <strong>{selected_label or '-'}</strong> (ID: {selected_id or '-'})</div>
      <ul>{cand_rows or f'<li>{t("common.no_data")}</li>'}</ul>
    </div>
    """


def app(environ, start_response):
    global CURRENT_LANG
    query = parse_query(environ)
    CURRENT_LANG = get_lang(environ)

    _orig_start_response = start_response

    def start_response(status, headers, exc_info=None):
        if query.get("lang", "").strip().lower() in ("ko", "en", "zh"):
            headers.append(("Set-Cookie", f"lang={CURRENT_LANG}; Path=/; Max-Age=31536000"))
        return _orig_start_response(status, headers, exc_info)

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
            html = render_html(t("login.title"), f"""
            <form method='post'>
              <div>{t('login.username')} <input name='username'></div>
              <div>{t('login.password')} <input name='password' type='password'></div>
              <button type='submit'>{t('common.login')}</button>
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
            html = render_html(t("login.title"), f"<p style='color:red'>{t('login.failed')}</p>")
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
        if not has_role(user, [ROLE_OWNER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
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
            form = f"""
            <h3>사용자 추가</h3>
            <form method='post'>
            이름<input name='name'> 아이디<input name='username'> 비밀번호<input name='password'>
            역할<select name='role'>
              <option value='owner'>원장</option><option value='manager'>매니저</option><option value='teacher'>강사</option>
              <option value='parent'>학부모</option><option value='student'>학생</option>
            </select><button>{t("common.save")}</button></form>
            """
        html = render_html("학생/학부모/강사 관리(사용자 기반)", form + f"<table border='1'><tr><th>ID</th><th>이름</th><th>아이디</th><th>역할</th></tr>{rows}</table>", user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path.startswith("/students/"):
        student_id = path.split("/")[-1]
        if not student_id.isdigit():
            conn.close()
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return ["Not Found".encode("utf-8")]

        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            d = parse_body(environ)
            action = d.get("action")
            if action == "save":
                conn.execute(
                    """UPDATE students SET
                    student_no=?, name_ko=?, name_en=?, phone=?, guardian_name=?, guardian_phone=?,
                    current_class_id=?, remaining_credits=?, status=?, enrolled_at=?, leave_start_date=?, leave_end_date=?, memo=?, updated_at=?
                    WHERE id=?""",
                    (
                        d.get("student_no"), d.get("name_ko"), d.get("name_en"), d.get("phone"), d.get("guardian_name"), d.get("guardian_phone"),
                        d.get("current_class_id") or None, d.get("remaining_credits") or 0, d.get("status") or "active", d.get("enrolled_at"),
                        d.get("leave_start_date"), d.get("leave_end_date"), d.get("memo"), now(), student_id,
                    ),
                )
                conn.commit()
                status, headers, body = redirect(f"/students/{student_id}?lang={CURRENT_LANG}&msg=saved")
                conn.close()
                start_response(status, headers)
                return [body]
            if action == "password":
                new_password = d.get("new_password", "").strip()
                student_row = conn.execute("SELECT user_id FROM students WHERE id=?", (student_id,)).fetchone()
                if not student_row or not student_row["user_id"]:
                    status, headers, body = redirect(f"/students/{student_id}?lang={CURRENT_LANG}&msg=no_user")
                    conn.close()
                    start_response(status, headers)
                    return [body]
                if not new_password:
                    status, headers, body = redirect(f"/students/{student_id}?lang={CURRENT_LANG}&msg=empty_pw")
                    conn.close()
                    start_response(status, headers)
                    return [body]
                conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_pw(new_password), student_row["user_id"]))
                conn.commit()
                status, headers, body = redirect(f"/students/{student_id}?lang={CURRENT_LANG}&msg=pw_saved")
                conn.close()
                start_response(status, headers)
                return [body]

        student = conn.execute(
            """SELECT s.*, u.username, c.name AS class_name, c.teacher_id AS current_class_teacher_id FROM students s
            LEFT JOIN users u ON u.id=s.user_id
            LEFT JOIN classes c ON c.id=s.current_class_id
            WHERE s.id=?""",
            (student_id,),
        ).fetchone()
        classes = conn.execute("SELECT id, name FROM classes ORDER BY id DESC").fetchall()
        if not student:
            conn.close()
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return ["Student Not Found".encode("utf-8")]
        if not can_view_student_row(user, student):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        msg_key = query.get("msg", "")
        msg_map = {
            "saved": "저장되었습니다 / Saved / 已保存",
            "pw_saved": "비밀번호가 변경되었습니다 / Password updated / 密码已更新",
            "no_user": "연결된 계정이 없습니다 / No linked user / 未关联用户账号",
            "empty_pw": "비밀번호를 입력하세요 / Enter password / 请输入密码",
        }
        message = msg_map.get(msg_key, "")
        class_opts = ["<option value=''>-</option>"]
        for c in classes:
            selected = "selected" if student["current_class_id"] == c["id"] else ""
            class_opts.append(f"<option value='{c['id']}' {selected}>{c['name']}</option>")
        class_options = "".join(class_opts)
        edit_form = ""
        pw_form = ""
        if has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            edit_form = f"""
            <form method='post' style='margin-bottom:16px'>
              <input type='hidden' name='action' value='save'>
              <h4>수정 / Edit / 编辑</h4>
              학생번호 <input name='student_no' value='{student['student_no'] or ''}'>
              한글이름 <input name='name_ko' value='{student['name_ko'] or ''}'>
              영문이름 <input name='name_en' value='{student['name_en'] or ''}'><br>
              연락처 <input name='phone' value='{student['phone'] or ''}'>
              보호자명 <input name='guardian_name' value='{student['guardian_name'] or ''}'>
              보호자연락처 <input name='guardian_phone' value='{student['guardian_phone'] or ''}'><br>
              현재 반 <select name='current_class_id'>{class_options}</select>
              남은 크레딧 <input name='remaining_credits' value='{student['remaining_credits'] or 0}'>
              상태 <select name='status'>
                <option value='active' {'selected' if student['status']=='active' else ''}>{status_t('active')}</option>
                <option value='leave' {'selected' if student['status']=='leave' else ''}>{status_t('leave')}</option>
                <option value='ended' {'selected' if student['status']=='ended' else ''}>{status_t('ended')}</option>
              </select><br>
              입학일 <input name='enrolled_at' value='{student['enrolled_at'] or ''}'>
              휴학시작 <input name='leave_start_date' value='{student['leave_start_date'] or ''}'>
              휴학종료 <input name='leave_end_date' value='{student['leave_end_date'] or ''}'><br>
              메모 <input name='memo' style='width:500px' value='{student['memo'] or ''}'><br>
              <button>저장 / Save / 保存</button>
            </form>
            """
            pw_form = """
            <form method='post'>
              <input type='hidden' name='action' value='password'>
              <h4>학생 계정 비밀번호 변경 / Password Reset / 重置密码</h4>
              새 비밀번호 <input name='new_password' type='password'>
              <button>변경 / Update / 更新</button>
            </form>
            """

        body_html = f"""
        <div><a href='/students?lang={CURRENT_LANG}'>← 학생 목록 / Student List / 学生列表</a></div>
        {f"<p style='color:green'>{message}</p>" if message else ''}
        <h3>{student['name_ko']} ({student['student_no'] or '-'})</h3>
        <table border='1' cellpadding='6'>
          <tr><th>기본정보 / Basic / 基本信息</th><td>한글이름: {student['name_ko'] or '-'} / 영문이름: {student['name_en'] or '-'} / 연락처: {student['phone'] or '-'}</td></tr>
          <tr><th>보호자정보 / Guardian / 监护人</th><td>{student['guardian_name'] or '-'} ({student['guardian_phone'] or '-'})</td></tr>
          <tr><th>현재반 / Class / 当前班级</th><td>{student['class_name'] or '-'}</td></tr>
          <tr><th>남은크레딧 / Credits / 剩余学分</th><td>{student['remaining_credits'] or 0}</td></tr>
          <tr><th>상태 / Status / 状态</th><td>{status_t(student['status']) if student['status'] else '-'}</td></tr>
          <tr><th>입/휴학 / Enrollment-Leave / 入学休学</th><td>입학일: {student['enrolled_at'] or '-'} / 휴학: {student['leave_start_date'] or '-'} ~ {student['leave_end_date'] or '-'}</td></tr>
          <tr><th>메모 / Memo / 备注</th><td>{student['memo'] or '-'}</td></tr>
        </table>
        {edit_form}
        {pw_form}
        """
        html = render_html("학생 상세 / Student Detail / 学生详情", body_html, user)
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
                        d.get("current_class_id") or None, d.get("remaining_credits") or 0, d.get("status") or "active", d.get("enrolled_at"), d.get("leave_start_date"), d.get("leave_end_date"), d.get("memo"), now(), student_user_id,
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
                        d.get("current_class_id") or None, d.get("remaining_credits") or 0, d.get("status") or "active", d.get("enrolled_at"), d.get("leave_start_date"), d.get("leave_end_date"), d.get("memo"), now(), now(),
                    ),
                )
            conn.commit()

        where = []
        params = []
        q_name = query.get("name", "").strip()
        q_student_no = query.get("student_no", "").strip()
        q_phone = query.get("phone", "").strip()
        if q_name:
            where.append("(s.name_ko LIKE ? OR s.name_en LIKE ?)")
            params += [f"%{q_name}%", f"%{q_name}%"]
        if q_student_no:
            where.append("s.student_no LIKE ?")
            params.append(f"%{q_student_no}%")
        if q_phone:
            where.append("s.phone LIKE ?")
            params.append(f"%{q_phone}%")
        where_sql = ("WHERE " + " AND ".join(where)) if where else ""

        students = conn.execute(
            f"""SELECT s.*, c.name AS class_name, c.teacher_id AS current_class_teacher_id
            FROM students s
            LEFT JOIN classes c ON c.id=s.current_class_id
            {where_sql}
            ORDER BY s.id DESC""",
            params,
        ).fetchall()

        rows = ""
        for st in students:
            if not can_view_student_row(user, st):
                continue
            rows += f"""
            <tr>
              <td>{st['student_no'] or '-'}</td>
              <td><a href='/students/{st['id']}?lang={CURRENT_LANG}'>{st['name_ko'] or '-'}</a></td>
              <td>{st['name_en'] or '-'}</td>
              <td>{st['phone'] or '-'}</td>
              <td>{st['guardian_name'] or '-'}</td>
              <td>{st['guardian_phone'] or '-'}</td>
              <td>{st['class_name'] or '-'}</td>
              <td>{st['remaining_credits'] or 0}</td>
              <td>{status_t(st['status']) if st['status'] else '-'}</td>
            </tr>
            """

        html = render_html("학생 관리 / Student Management / 学生管理", f"""
        <form method='get' style='margin-bottom:10px'>
          <input type='hidden' name='lang' value='{CURRENT_LANG}'>
          이름 <input name='name' value='{q_name}'>
          학생번호 <input name='student_no' value='{q_student_no}'>
          연락처 <input name='phone' value='{q_phone}'>
          <button>{t("common.search")}</button>
          <a href='/students?lang={CURRENT_LANG}'>초기화 / Reset / 重置</a>
        </form>
        <table border='1' cellpadding='6' cellspacing='0'>
          <tr>
            <th>학생번호</th><th>한글이름</th><th>영문이름</th><th>연락처</th><th>보호자명</th><th>보호자 연락처</th><th>현재 반</th><th>남은 크레딧</th><th>상태</th>
          </tr>
          {rows or "<tr><td colspan='9'>데이터 없음 / No Data / 无数据</td></tr>"}
        </table>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    # 학사 구조
    if path == "/academics":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
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
        if has_role(user, [ROLE_TEACHER]):
            classes = conn.execute("SELECT c.*,u.name as teacher_name FROM classes c LEFT JOIN users u ON c.teacher_id=u.id WHERE c.teacher_id=?", (user["id"],)).fetchall()
        else:
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
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        selected_student_id = query.get("selected_student_id", "")
        selected_class_id = query.get("selected_class_id", "")
        selected_teacher_id = query.get("selected_teacher_id", "")
        student_candidates = fetch_student_candidates(conn, query.get("student_q", ""), limit=10)
        class_candidates = fetch_class_candidates(conn, query.get("class_q", ""), limit=10)
        teacher_candidates = fetch_teacher_candidates(conn, query.get("teacher_q", ""), limit=10)

        selected_student = conn.execute("SELECT id, name_ko, student_no FROM students WHERE id=?", (selected_student_id,)).fetchone() if selected_student_id else None
        selected_class = conn.execute("SELECT id, name FROM classes WHERE id=?", (selected_class_id,)).fetchone() if selected_class_id else None
        selected_teacher = conn.execute("SELECT id, name, username FROM users WHERE id=? AND role='teacher'", (selected_teacher_id,)).fetchone() if selected_teacher_id else None

        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            class_id = d.get("class_id") or selected_class_id
            student_input_id = d.get("student_id") or selected_student_id
            student_row = conn.execute("SELECT user_id FROM students WHERE id=?", (student_input_id,)).fetchone() if str(student_input_id).isdigit() else None
            student_id = student_row["user_id"] if student_row else student_input_id
            if has_role(user, [ROLE_TEACHER]):
                class_ok = conn.execute("SELECT id FROM classes WHERE id=? AND teacher_id=?", (class_id, user["id"])).fetchone()
                if not class_ok:
                    conn.close()
                    status, headers, body = forbidden_html(user, "담당 반만 처리할 수 있습니다 / Teacher class only / 仅限负责班级")
                    start_response(status, headers)
                    return [body]
            created_by = d.get("teacher_id") or selected_teacher_id or user["id"]
            conn.execute("INSERT INTO attendance(class_id, student_id, lesson_date, status, note, created_by, created_at) VALUES(?,?,?,?,?,?,?)",
                         (class_id, student_id, d.get("lesson_date"), d.get("status"), d.get("note"), created_by, now()))
            if d.get("status") == "absent":
                conn.execute("INSERT INTO notifications(type, target_user_id, payload, created_at) VALUES(?,?,?,?)",
                             ("absence", student_id, json.dumps({"student_id": student_id, "date": d.get("lesson_date")}, ensure_ascii=False), now()))
            conn.commit()

        if has_role(user, [ROLE_TEACHER]):
            rows = conn.execute("SELECT a.* FROM attendance a JOIN classes c ON c.id=a.class_id WHERE c.teacher_id=? ORDER BY a.id DESC LIMIT 200", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_STUDENT]):
            rows = conn.execute("SELECT * FROM attendance WHERE student_id=? ORDER BY id DESC LIMIT 200", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_PARENT]):
            rows = conn.execute("""SELECT a.* FROM attendance a JOIN students s ON s.user_id=a.student_id WHERE s.guardian_name=? ORDER BY a.id DESC LIMIT 200""", (user["name"],)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM attendance ORDER BY id DESC LIMIT 200").fetchall()
        picker_keep = {
            "selected_student_id": selected_student_id,
            "selected_class_id": selected_class_id,
            "selected_teacher_id": selected_teacher_id,
            "student_q": query.get("student_q", ""),
            "class_q": query.get("class_q", ""),
            "teacher_q": query.get("teacher_q", ""),
        }
        student_picker = render_picker_block("학생 검색 선택", "student_q", query.get("student_q", ""), "selected_student_id", selected_student_id,
                                            (f"{selected_student['name_ko']} ({selected_student['student_no'] or '-'})" if selected_student else ""),
                                            student_candidates, "/attendance", CURRENT_LANG,
                                            {"selected_class_id": selected_class_id, "selected_teacher_id": selected_teacher_id, "class_q": query.get("class_q", ""), "teacher_q": query.get("teacher_q", "")})
        class_picker = render_picker_block("반 검색 선택", "class_q", query.get("class_q", ""), "selected_class_id", selected_class_id,
                                          (selected_class["name"] if selected_class else ""),
                                          class_candidates, "/attendance", CURRENT_LANG,
                                          {"selected_student_id": selected_student_id, "selected_teacher_id": selected_teacher_id, "student_q": query.get("student_q", ""), "teacher_q": query.get("teacher_q", "")})
        teacher_picker = render_picker_block("강사 검색 선택", "teacher_q", query.get("teacher_q", ""), "selected_teacher_id", selected_teacher_id,
                                            (f"{selected_teacher['name']} ({selected_teacher['username']})" if selected_teacher else ""),
                                            teacher_candidates, "/attendance", CURRENT_LANG,
                                            {"selected_student_id": selected_student_id, "selected_class_id": selected_class_id, "student_q": query.get("student_q", ""), "class_q": query.get("class_q", "")})
        html = render_html("출결 관리", f"""
        {student_picker}
        {class_picker}
        {teacher_picker}
        <form method='post'>
        <input type='hidden' name='student_id' value='{selected_student_id}'>
        <input type='hidden' name='class_id' value='{selected_class_id}'>
        <input type='hidden' name='teacher_id' value='{selected_teacher_id}'>
        학생ID <input name='student_id_manual' value='{selected_student_id}' readonly> 반ID <input name='class_id_manual' value='{selected_class_id}' readonly> 강사ID <input name='teacher_id_manual' value='{selected_teacher_id}' readonly>
        날짜<input name='lesson_date' placeholder='2026-03-06'>
        상태<select name='status'><option value='present'>출석</option><option value='late'>지각</option><option value='absent'>결석</option><option value='makeup'>보강</option></select>
        메모<input name='note'><button>{t("common.save")}</button></form>
        <pre>{[dict(r) for r in rows]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path == "/homework":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        selected_class_id = query.get("selected_class_id", "")
        selected_teacher_id = query.get("selected_teacher_id", "")
        class_candidates = fetch_class_candidates(conn, query.get("class_q", ""), limit=10)
        teacher_candidates = fetch_teacher_candidates(conn, query.get("teacher_q", ""), limit=10)
        selected_class = conn.execute("SELECT id, name FROM classes WHERE id=?", (selected_class_id,)).fetchone() if selected_class_id else None
        selected_teacher = conn.execute("SELECT id, name, username FROM users WHERE id=? AND role='teacher'", (selected_teacher_id,)).fetchone() if selected_teacher_id else None

        if method == "POST":
            d = parse_body(environ)
            typ = d.get("type")
            if typ == "homework" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
                class_id = d.get("class_id") or selected_class_id
                if has_role(user, [ROLE_TEACHER]):
                    class_ok = conn.execute("SELECT id FROM classes WHERE id=? AND teacher_id=?", (class_id, user["id"])).fetchone()
                    if not class_ok:
                        conn.close()
                        status, headers, body = forbidden_html(user, "담당 반만 등록 가능 / Teacher class only / 仅限负责班级")
                        start_response(status, headers)
                        return [body]
                created_by = d.get("teacher_id") or selected_teacher_id or user["id"]
                conn.execute("INSERT INTO homework(class_id, title, due_date, created_by, created_at) VALUES(?,?,?,?,?)", (class_id, d.get("title"), d.get("due_date"), created_by, now()))
                conn.execute("INSERT INTO notifications(type, target_user_id, payload, created_at) VALUES(?,?,?,?)", ("homework", None, json.dumps({"title": d.get("title")}, ensure_ascii=False), now()))
            elif typ == "submission" and has_role(user, [ROLE_STUDENT]):
                conn.execute("INSERT INTO homework_submissions(homework_id, student_id, submitted, submitted_at) VALUES(?,?,?,?)", (d.get("homework_id"), user["id"], 1, now()))
            elif typ == "feedback" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
                conn.execute("UPDATE homework_submissions SET feedback=?, feedback_by=?, feedback_at=? WHERE id=?", (d.get("feedback"), user["id"], now(), d.get("submission_id")))
            conn.commit()
        if has_role(user, [ROLE_TEACHER]):
            hw = conn.execute("SELECT h.* FROM homework h JOIN classes c ON c.id=h.class_id WHERE c.teacher_id=? ORDER BY h.id DESC", (user["id"],)).fetchall()
            sub = conn.execute("SELECT hs.* FROM homework_submissions hs JOIN homework h ON h.id=hs.homework_id JOIN classes c ON c.id=h.class_id WHERE c.teacher_id=? ORDER BY hs.id DESC", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_STUDENT]):
            hw = conn.execute("SELECT * FROM homework ORDER BY id DESC").fetchall()
            sub = conn.execute("SELECT * FROM homework_submissions WHERE student_id=? ORDER BY id DESC", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_PARENT]):
            hw = conn.execute("SELECT * FROM homework ORDER BY id DESC").fetchall()
            sub = conn.execute("""SELECT hs.* FROM homework_submissions hs JOIN students s ON s.user_id=hs.student_id WHERE s.guardian_name=? ORDER BY hs.id DESC""", (user["name"],)).fetchall()
        else:
            hw = conn.execute("SELECT * FROM homework ORDER BY id DESC").fetchall()
            sub = conn.execute("SELECT * FROM homework_submissions ORDER BY id DESC").fetchall()
        class_picker = render_picker_block("반 검색 선택", "class_q", query.get("class_q", ""), "selected_class_id", selected_class_id,
                                          (selected_class["name"] if selected_class else ""), class_candidates, "/homework", CURRENT_LANG,
                                          {"selected_teacher_id": selected_teacher_id, "teacher_q": query.get("teacher_q", "")})
        teacher_picker = render_picker_block("강사 검색 선택", "teacher_q", query.get("teacher_q", ""), "selected_teacher_id", selected_teacher_id,
                                            (f"{selected_teacher['name']} ({selected_teacher['username']})" if selected_teacher else ""), teacher_candidates, "/homework", CURRENT_LANG,
                                            {"selected_class_id": selected_class_id, "class_q": query.get("class_q", "")})
        html = render_html("숙제 관리", f"""
        {class_picker}
        {teacher_picker}
        <form method='post'><input type='hidden' name='type' value='homework'><input type='hidden' name='class_id' value='{selected_class_id}'><input type='hidden' name='teacher_id' value='{selected_teacher_id}'>반ID<input value='{selected_class_id}' readonly> 강사ID<input value='{selected_teacher_id}' readonly> 제목<input name='title'> 마감일<input name='due_date'><button>등록</button></form>
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
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER, ROLE_PARENT, ROLE_STUDENT]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            typ = d.get("type")
            if has_role(user, [ROLE_TEACHER]):
                if typ == "exam":
                    class_ok = conn.execute("SELECT id FROM classes WHERE id=? AND teacher_id=?", (d.get("class_id"), user["id"])).fetchone()
                    if not class_ok:
                        conn.close()
                        status, headers, body = forbidden_html(user, "담당 반만 처리할 수 있습니다 / Teacher class only / 仅限负责班级")
                        start_response(status, headers)
                        return [body]
                elif typ == "score":
                    exam_ok = conn.execute("""SELECT e.id FROM exams e JOIN classes c ON c.id=e.class_id WHERE e.id=? AND c.teacher_id=?""", (d.get("exam_id"), user["id"])).fetchone()
                    if not exam_ok:
                        conn.close()
                        status, headers, body = forbidden_html(user, "담당 시험만 처리할 수 있습니다 / Teacher exam only / 仅限负责考试")
                        start_response(status, headers)
                        return [body]
            if typ == "exam":
                conn.execute("INSERT INTO exams(class_id, name, exam_date, report, linked_book_id, created_at) VALUES(?,?,?,?,?,?)", (d.get("class_id"), d.get("name"), d.get("exam_date"), d.get("report"), d.get("linked_book_id"), now()))
            elif typ == "score":
                conn.execute("INSERT INTO exam_scores(exam_id, student_id, score, created_at) VALUES(?,?,?,?)", (d.get("exam_id"), d.get("student_id"), d.get("score"), now()))
            conn.commit()
        if has_role(user, [ROLE_TEACHER]):
            exams = conn.execute("SELECT e.* FROM exams e JOIN classes c ON c.id=e.class_id WHERE c.teacher_id=? ORDER BY e.id DESC", (user["id"],)).fetchall()
            scores = conn.execute("SELECT es.* FROM exam_scores es JOIN exams e ON e.id=es.exam_id JOIN classes c ON c.id=e.class_id WHERE c.teacher_id=? ORDER BY es.id DESC", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_STUDENT]):
            exams = conn.execute("SELECT e.* FROM exams e JOIN exam_scores es ON es.exam_id=e.id WHERE es.student_id=? ORDER BY e.id DESC", (user["id"],)).fetchall()
            scores = conn.execute("SELECT * FROM exam_scores WHERE student_id=? ORDER BY id DESC", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_PARENT]):
            exams = conn.execute("SELECT DISTINCT e.* FROM exams e JOIN exam_scores es ON es.exam_id=e.id JOIN students s ON s.user_id=es.student_id WHERE s.guardian_name=? ORDER BY e.id DESC", (user["name"],)).fetchall()
            scores = conn.execute("SELECT es.* FROM exam_scores es JOIN students s ON s.user_id=es.student_id WHERE s.guardian_name=? ORDER BY es.id DESC", (user["name"],)).fetchall()
        else:
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
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            conn.execute("INSERT INTO counseling(student_id, parent_id, memo, is_special_note, created_by, created_at) VALUES(?,?,?,?,?,?)", (d.get("student_id"), d.get("parent_id"), d.get("memo"), 1 if d.get("is_special_note") else 0, user["id"], now()))
            conn.commit()
        rows = conn.execute("SELECT * FROM counseling ORDER BY id DESC").fetchall()
        html = render_html("상담 기록/학생 특이사항", f"""
        <form method='post'>학생ID<input name='student_id'> 학부모ID<input name='parent_id'> 메모<input name='memo'> 특이사항<input type='checkbox' name='is_special_note' value='1'><button>{t("common.save")}</button></form>
        <pre>{[dict(r) for r in rows]}</pre>
        """, user)
        status, headers, body = text_resp(html)
        conn.close()
        start_response(status, headers)
        return [body]

    if path == "/payments":
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_PARENT, ROLE_STUDENT]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER]):
            d = parse_body(environ)
            conn.execute("INSERT INTO payments(student_id, paid_date, amount, package_hours, remaining_classes, created_at) VALUES(?,?,?,?,?,?)", (d.get("student_id"), d.get("paid_date"), d.get("amount"), d.get("package_hours"), d.get("remaining_classes"), now()))
            conn.commit()
        if has_role(user, [ROLE_STUDENT]):
            rows = conn.execute("SELECT * FROM payments WHERE student_id=? ORDER BY id DESC", (user["id"],)).fetchall()
        elif has_role(user, [ROLE_PARENT]):
            rows = conn.execute("SELECT p.* FROM payments p JOIN students s ON s.user_id=p.student_id WHERE s.guardian_name=? ORDER BY p.id DESC", (user["name"],)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM payments ORDER BY id DESC").fetchall()
        html = render_html("수납 기록", f"""
        <form method='post'>학생ID<input name='student_id'> 결제일<input name='paid_date'> 금액<input name='amount'> 패키지시간<input name='package_hours'> 잔여수업수<input name='remaining_classes'><button>{t("common.save")}</button></form>
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
        if not has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            conn.close()
            status, headers, body = forbidden_html(user)
            start_response(status, headers)
            return [body]
        selected_student_id = query.get("selected_student_id", "")
        selected_teacher_id = query.get("selected_teacher_id", "")
        student_candidates = fetch_student_candidates(conn, query.get("student_q", ""), limit=10)
        teacher_candidates = fetch_teacher_candidates(conn, query.get("teacher_q", ""), limit=10)
        selected_student = conn.execute("SELECT id, name_ko, student_no FROM students WHERE id=?", (selected_student_id,)).fetchone() if selected_student_id else None
        selected_teacher = conn.execute("SELECT id, name, username FROM users WHERE id=? AND role='teacher'", (selected_teacher_id,)).fetchone() if selected_teacher_id else None

        if method == "POST" and has_role(user, [ROLE_OWNER, ROLE_MANAGER, ROLE_TEACHER]):
            d = parse_body(environ)
            typ = d.get("type")
            if typ == "book":
                conn.execute("INSERT INTO books(code, title, status, created_at) VALUES(?,?,?,?)", (d.get("code"), d.get("title"), "available", now()))
            elif typ == "loan":
                book = conn.execute("SELECT * FROM books WHERE code=?", (d.get("code"),)).fetchone()
                if book:
                    conn.execute("UPDATE books SET status='borrowed' WHERE id=?", (book["id"],))
                    student_input_id = d.get("student_id") or selected_student_id
                    student_row = conn.execute("SELECT user_id FROM students WHERE id=?", (student_input_id,)).fetchone() if str(student_input_id).isdigit() else None
                    student_user_id = student_row["user_id"] if student_row else student_input_id
                    conn.execute("INSERT INTO book_loans(book_id, student_id, loaned_at, handled_by, created_at) VALUES(?,?,?,?,?)", (book["id"], student_user_id, now(), d.get("teacher_id") or selected_teacher_id or user["id"], now()))
            elif typ == "return":
                book = conn.execute("SELECT * FROM books WHERE code=?", (d.get("code"),)).fetchone()
                if book:
                    conn.execute("UPDATE books SET status='available' WHERE id=?", (book["id"],))
                    conn.execute("UPDATE book_loans SET returned_at=? WHERE book_id=? AND returned_at IS NULL", (now(), book["id"]))
            conn.commit()
        books = conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
        loans = conn.execute("SELECT * FROM book_loans ORDER BY id DESC").fetchall()
        student_picker = render_picker_block("학생 검색 선택", "student_q", query.get("student_q", ""), "selected_student_id", selected_student_id,
                                            (f"{selected_student['name_ko']} ({selected_student['student_no'] or '-'})" if selected_student else ""),
                                            student_candidates, "/library", CURRENT_LANG,
                                            {"selected_teacher_id": selected_teacher_id, "teacher_q": query.get("teacher_q", "")})
        teacher_picker = render_picker_block("강사 검색 선택", "teacher_q", query.get("teacher_q", ""), "selected_teacher_id", selected_teacher_id,
                                            (f"{selected_teacher['name']} ({selected_teacher['username']})" if selected_teacher else ""),
                                            teacher_candidates, "/library", CURRENT_LANG,
                                            {"selected_student_id": selected_student_id, "student_q": query.get("student_q", "")})
        html = render_html("도서 대출 관리", f"""
        {student_picker}
        {teacher_picker}
        <form method='post'><input type='hidden' name='type' value='book'>코드<input name='code'> 제목<input name='title'><button>도서 등록</button></form>
        <form method='post'><input type='hidden' name='type' value='loan'><input type='hidden' name='student_id' value='{selected_student_id}'><input type='hidden' name='teacher_id' value='{selected_teacher_id}'>코드입력<input name='code'> 학생ID<input value='{selected_student_id}' readonly> 강사ID<input value='{selected_teacher_id}' readonly><button>대여 처리</button></form>
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
            status, headers, body = forbidden_json("권한 없음")
            start_response(status, headers)
            return [body]
        book = conn.execute("SELECT * FROM books WHERE code=?", (d.get("code"),)).fetchone()
        if not book:
            conn.close()
            status, headers, body = json_resp({"error": "도서 없음"}, "404 Not Found")
            start_response(status, headers)
            return [body]
        conn.execute("UPDATE books SET status='borrowed' WHERE id=?", (book["id"],))
        student_input_id = d.get("student_id")
        student_row = conn.execute("SELECT user_id FROM students WHERE id=?", (student_input_id,)).fetchone() if str(student_input_id).isdigit() else None
        student_user_id = student_row["user_id"] if student_row else student_input_id
        conn.execute("INSERT INTO book_loans(book_id, student_id, loaned_at, handled_by, created_at) VALUES(?,?,?,?,?)", (book["id"], student_user_id, now(), user["id"], now()))
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
