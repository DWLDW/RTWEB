param(
  [switch]$Push
)

$ErrorActionPreference = 'Stop'

Write-Host '[1/6] Repo check'
git -C C:\RTWEB rev-parse --is-inside-work-tree | Out-Null

Write-Host '[2/6] Fetch latest refs/tags'
git -C C:\RTWEB fetch origin --tags --prune

Write-Host '[3/6] Show latest tags (top 20)'
git -C C:\RTWEB tag --sort=-creatordate | Select-Object -First 20

Write-Host '[4/6] Ensure main branch'
git -C C:\RTWEB checkout main

git -C C:\RTWEB pull --rebase origin main

Write-Host '[5/6] Conflict marker scan'
$conflicts = git -C C:\RTWEB grep -n "<<<<<<<\|=======\|>>>>>>>" -- app.py schema.sql README.md 2>$null
if ($LASTEXITCODE -eq 0 -and $conflicts) {
  Write-Error "Conflict markers found. Resolve before push.`n$conflicts"
}

Write-Host '[6/6] Status summary'
git -C C:\RTWEB status -sb

if ($Push) {
  Write-Host 'Push to origin/main'
  git -C C:\RTWEB push origin main
}
