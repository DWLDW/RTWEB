[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "원격 정보 갱신 중..."
git fetch origin --prune

$defaultBase = "origin/main"
$currentBranch = git branch --show-current

Write-Host "기준 브랜치: $defaultBase"
Write-Host "현재 브랜치: $currentBranch"
Write-Host "머지된 원격 codex 브랜치 검색 중..."

$mergedRemoteBranches = git branch -r --merged $defaultBase |
    ForEach-Object { $_.Trim() } |
    Where-Object {
        $_ -like "origin/codex/*" -and
        $_ -ne "origin/HEAD" -and
        ($_ -replace "^origin/", "") -ne $currentBranch
    } |
    Sort-Object -Unique

if (-not $mergedRemoteBranches -or $mergedRemoteBranches.Count -eq 0) {
    Write-Host "삭제할 머지 완료 codex 브랜치가 없음."
    exit 0
}

Write-Host ""
Write-Host "삭제 대상 브랜치 목록:"
$mergedRemoteBranches | ForEach-Object { Write-Host " - $_" }
Write-Host ""

$confirm = Read-Host "위 브랜치들을 삭제할까? (y/n)"

if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "취소됨."
    exit 0
}

foreach ($remoteBranch in $mergedRemoteBranches) {
    $branchName = $remoteBranch -replace "^origin/", ""

    Write-Host ""
    Write-Host "삭제 중: $branchName"

    git push origin --delete $branchName

    $localExists = git branch --list $branchName
    if ($localExists) {
        git branch -D $branchName
    }
}

Write-Host ""
Write-Host "정리 완료."
git fetch origin --prune