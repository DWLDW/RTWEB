Write-Host "`n[RTWEB LMS] Windows PowerShell setup 시작" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[오류] python 명령을 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "먼저 Python 3.10+ 설치 후 다시 실행하세요: https://www.python.org/downloads/windows/"
    Write-Host "설치 시 'Add Python to PATH' 옵션을 체크하세요."
    exit 1
}

Write-Host "[1/5] Python 버전 확인" -ForegroundColor Yellow
python --version

Write-Host "[2/5] 가상환경 생성(.venv)" -ForegroundColor Yellow
python -m venv .venv

Write-Host "[3/5] 실행 정책 안내" -ForegroundColor Yellow
Write-Host "스크립트 실행 오류가 나면 아래 명령을 1회 실행하세요:"
Write-Host "Set-ExecutionPolicy -Scope CurrentUser RemoteSigned"

Write-Host "[4/5] 가상환경 활성화" -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

Write-Host "[5/5] requirements 설치" -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "`n설치 완료!" -ForegroundColor Green
Write-Host "실행 방법:"
Write-Host "1) .\.venv\Scripts\Activate.ps1"
Write-Host "2) python app.py"
Write-Host "3) 브라우저 접속: http://127.0.0.1:8000/login"
Write-Host "`n참고: app.py 실행 시 init_db()가 자동 실행되어 lms.db와 초기 계정이 생성됩니다."
