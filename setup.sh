#!/usr/bin/env bash
set -euo pipefail

printf "\n[RTWEB LMS] macOS/Linux setup 시작\n"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[오류] python3를 찾을 수 없습니다. 먼저 Python 3.10+ 설치 후 다시 실행하세요."
  echo "- macOS: brew install python"
  echo "- Ubuntu/Debian: sudo apt update && sudo apt install -y python3 python3-venv"
  exit 1
fi

echo "[1/4] Python 버전 확인"
python3 --version

echo "[2/4] 가상환경 생성(.venv)"
python3 -m venv .venv

echo "[3/4] 가상환경 활성화"
# shellcheck disable=SC1091
source .venv/bin/activate

echo "[4/4] requirements 설치"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
cat <<'EOF'
설치 완료!
실행 방법:
1) source .venv/bin/activate
2) python app.py
3) 브라우저 접속: http://127.0.0.1:8000/login

참고:
- app.py 실행 시 init_db()가 자동으로 실행되어 lms.db와 초기 계정이 자동 생성됩니다.
EOF
