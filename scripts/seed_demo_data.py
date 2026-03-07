import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import get_db, init_db, seed_demo_data


def main():
    init_db()
    conn = get_db()
    try:
        result = seed_demo_data(conn, force=True)
        conn.commit()
        print("seed_demo_data result:", result)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
