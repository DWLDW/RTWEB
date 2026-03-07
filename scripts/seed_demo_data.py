import argparse
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import get_db, init_db, seed_demo_data


def build_options(args):
    options = {}
    for key in (
        "preset",
        "manager_count",
        "foreign_teacher_count",
        "chinese_teacher_count",
        "parent_count",
        "student_count",
        "course_count",
        "level_count",
        "class_count",
        "classroom_count",
        "book_count",
        "announcement_count",
    ):
        value = getattr(args, key)
        if value is not None:
            options[key] = value
    return options


def parse_args():
    parser = argparse.ArgumentParser(description="Seed demo data for ReadingTown LMS")
    parser.add_argument("--preset", choices=["large_school"], help="Named demo data preset")
    parser.add_argument("--manager-count", type=int)
    parser.add_argument("--foreign-teacher-count", type=int)
    parser.add_argument("--chinese-teacher-count", type=int)
    parser.add_argument("--parent-count", type=int)
    parser.add_argument("--student-count", type=int)
    parser.add_argument("--course-count", type=int)
    parser.add_argument("--level-count", type=int)
    parser.add_argument("--class-count", type=int)
    parser.add_argument("--classroom-count", type=int)
    parser.add_argument("--book-count", type=int)
    parser.add_argument("--announcement-count", type=int)
    return parser.parse_args()


def main():
    args = parse_args()
    init_db()
    conn = get_db()
    try:
        result = seed_demo_data(conn, force=True, options=build_options(args))
        conn.commit()
        print("seed_demo_data result:", result)
    finally:
        conn.close()


if __name__ == "__main__":
    main()