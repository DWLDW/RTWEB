[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$branch = git branch --show-current

Write-Host "현재 브랜치: $branch"

if ($branch -like "codex/*") {

    Write-Host "Codex 브랜치 확인. main 최신 내용 가져오는 중..."

    git fetch origin

    Write-Host "main을 현재 브랜치에 merge (codex 변경 우선)..."

    git merge -X ours origin/main

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Merge 충돌 발생. 자동 해결..."
        git checkout --ours .
        git add .
        git commit -m "auto resolve conflicts keeping codex changes"
    }

    Write-Host "GitHub로 push..."

    git push

    Write-Host "완료"
}
else {
    Write-Host "현재 브랜치가 codex 브랜치가 아님. 실행 중단."
}