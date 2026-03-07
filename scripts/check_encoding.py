from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / 'app.py',
    ROOT / 'schema.sql',
]


def main() -> int:
    ok = True
    for path in TARGETS:
        if not path.exists():
            print(f'[MISS] {path}')
            ok = False
            continue

        raw = path.read_bytes()
        if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
            print(f'[FAIL] {path.name}: UTF-16 BOM detected')
            ok = False
            continue

        try:
            raw.decode('utf-8')
        except UnicodeDecodeError as e:
            print(f'[FAIL] {path.name}: not valid UTF-8 ({e})')
            ok = False
            continue

        crlf = raw.count(b'\r\n')
        lf = raw.count(b'\n')
        print(f'[OK]   {path.name}: utf-8, lines={lf}, crlf={crlf}')

    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
