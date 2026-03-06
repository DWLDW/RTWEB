#!/usr/bin/env python3
import argparse
import sqlite3
from collections import defaultdict

REQUIRED = {
    "users": ["id", "name", "username", "password_hash", "role", "teacher_type"],
    "students": ["id", "user_id", "student_no", "name_ko", "current_class_id", "status"],
    "courses": ["id", "name"],
    "levels": ["id", "course_id", "name"],
    "classes": ["id", "course_id", "level_id", "name", "teacher_id", "foreign_teacher_id", "chinese_teacher_id"],
    "classrooms": ["id", "name", "room_code", "room_name", "status"],
    "time_slots": ["id", "label", "start_time", "end_time"],
    "schedules": ["id", "class_id", "day_of_week", "start_time", "end_time", "teacher_id", "room_id", "classroom"],
    "attendance": ["id", "class_id", "student_id", "lesson_date", "status", "created_by"],
    "homework": ["id", "class_id", "title", "created_by"],
    "homework_submissions": ["id", "homework_id", "student_id"],
    "exams": ["id", "class_id", "name", "linked_book_id"],
    "exam_scores": ["id", "exam_id", "student_id", "score"],
    "counseling": ["id", "student_id", "parent_id", "memo", "created_by"],
    "payments": ["id", "student_id", "paid_date", "amount"],
    "books": ["id", "code", "title", "status"],
    "book_loans": ["id", "book_id", "student_id", "handled_by"],
    "notifications": ["id", "type", "target_user_id", "payload"],
    "app_logs": ["id", "level", "route", "user_id", "message", "created_at"],
}


def q(conn, sql):
    return conn.execute(sql).fetchall()


def has_col(conn, table, col):
    cols = {r[1] for r in q(conn, f"PRAGMA table_info({table})")}
    return col in cols


def print_table_inventory(conn):
    print("=== TABLES ===")
    tables = [r[0] for r in q(conn, "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    for t in tables:
        cols = q(conn, f"PRAGMA table_info({t})")
        fks = q(conn, f"PRAGMA foreign_key_list({t})")
        cdesc = ", ".join([f"{c[1]}{'*' if c[3] else ''}" for c in cols])
        fdesc = "; ".join([f"{fk[3]}->{fk[2]}.{fk[4]}" for fk in fks]) if fks else "-"
        print(f"- {t}: {cdesc}")
        print(f"  FK: {fdesc}")
    print()


def required_check(conn):
    print("=== REQUIRED TABLE/COLUMN CHECK ===")
    tables = {r[0] for r in q(conn, "SELECT name FROM sqlite_master WHERE type='table'")}
    missing = defaultdict(list)
    for t, cols in REQUIRED.items():
        if t not in tables:
            missing[t] = cols
            continue
        existing = {r[1] for r in q(conn, f"PRAGMA table_info({t})")}
        for c in cols:
            if c not in existing:
                missing[t].append(c)
    if not missing:
        print("OK: all required tables/columns present")
    else:
        for t, cols in missing.items():
            print(f"MISSING {t}: {', '.join(cols)}")
    print()


def orphan_checks(conn):
    print("=== ORPHAN / INTEGRITY CHECKS ===")
    checks = []
    checks.append(("student role without students profile", """
        SELECT u.id, u.username FROM users u
        LEFT JOIN students s ON s.user_id=u.id
        WHERE u.role='student' AND s.id IS NULL
    """))
    checks.append(("teacher role with NULL teacher_type", """
        SELECT id, username FROM users WHERE role='teacher' AND (teacher_type IS NULL OR teacher_type='')
    """))
    checks.append(("students.current_class_id missing class", """
        SELECT s.id, s.user_id, s.current_class_id FROM students s
        LEFT JOIN classes c ON c.id=s.current_class_id
        WHERE s.current_class_id IS NOT NULL AND c.id IS NULL
    """))
    checks.append(("classes.course_id missing course", """
        SELECT c.id, c.course_id FROM classes c
        LEFT JOIN courses co ON co.id=c.course_id
        WHERE c.course_id IS NOT NULL AND co.id IS NULL
    """))
    checks.append(("classes.level_id missing level", """
        SELECT c.id, c.level_id FROM classes c
        LEFT JOIN levels l ON l.id=c.level_id
        WHERE c.level_id IS NOT NULL AND l.id IS NULL
    """))
    checks.append(("classes.teacher_id missing teacher user", """
        SELECT c.id, c.teacher_id FROM classes c
        LEFT JOIN users u ON u.id=c.teacher_id
        WHERE c.teacher_id IS NOT NULL AND (u.id IS NULL OR u.role<>'teacher')
    """))
    checks.append(("schedules.class_id missing class", """
        SELECT sc.id, sc.class_id FROM schedules sc
        LEFT JOIN classes c ON c.id=sc.class_id
        WHERE c.id IS NULL
    """))
    checks.append(("schedules.teacher_id missing teacher user", """
        SELECT sc.id, sc.teacher_id FROM schedules sc
        LEFT JOIN users u ON u.id=sc.teacher_id
        WHERE sc.teacher_id IS NOT NULL AND (u.id IS NULL OR u.role<>'teacher')
    """))
    if has_col(conn, "schedules", "room_id"):
        checks.append(("schedules.room_id missing classroom", """
            SELECT sc.id, sc.room_id FROM schedules sc
            LEFT JOIN classrooms cr ON cr.id=sc.room_id
            WHERE sc.room_id IS NOT NULL AND cr.id IS NULL
        """))
    checks.append(("attendance.class_id missing class", """
        SELECT a.id, a.class_id FROM attendance a
        LEFT JOIN classes c ON c.id=a.class_id
        WHERE c.id IS NULL
    """))
    checks.append(("attendance.student_id missing student user", """
        SELECT a.id, a.student_id FROM attendance a
        LEFT JOIN users u ON u.id=a.student_id
        WHERE u.id IS NULL OR u.role<>'student'
    """))
    checks.append(("homework.class_id missing class", """
        SELECT h.id, h.class_id FROM homework h
        LEFT JOIN classes c ON c.id=h.class_id
        WHERE c.id IS NULL
    """))
    checks.append(("homework_submissions.homework_id missing homework", """
        SELECT hs.id, hs.homework_id FROM homework_submissions hs
        LEFT JOIN homework h ON h.id=hs.homework_id
        WHERE h.id IS NULL
    """))
    checks.append(("exam_scores.exam_id missing exam", """
        SELECT es.id, es.exam_id FROM exam_scores es
        LEFT JOIN exams e ON e.id=es.exam_id
        WHERE e.id IS NULL
    """))
    checks.append(("payments.student_id missing student user", """
        SELECT p.id, p.student_id FROM payments p
        LEFT JOIN users u ON u.id=p.student_id
        WHERE u.id IS NULL OR u.role<>'student'
    """))
    checks.append(("book_loans.book_id missing book", """
        SELECT bl.id, bl.book_id FROM book_loans bl
        LEFT JOIN books b ON b.id=bl.book_id
        WHERE b.id IS NULL
    """))

    total = 0
    for name, sql in checks:
        rows = q(conn, sql)
        total += len(rows)
        print(f"- {name}: {len(rows)}")
        if rows:
            sample = rows[:5]
            print(f"  sample: {sample}")
    print(f"TOTAL_ISSUES={total}")
    print()


def main():
    ap = argparse.ArgumentParser(description="LMS DB preflight checker")
    ap.add_argument("--db", default="lms.db", help="SQLite DB path")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        print_table_inventory(conn)
        required_check(conn)
        orphan_checks(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
