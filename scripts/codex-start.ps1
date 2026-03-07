param()

$prompt = @"
Before coding, read:
- docs/CODEX_RULES.md
- docs/PROJECT_STATE.md
- docs/SESSION_HANDOFF.md
- docs/DEV_ENV.md

Summarize current project state and constraints before coding.
Do not modify code yet.
"@

Set-Clipboard -Value $prompt
Write-Host "Copied Codex start prompt to clipboard."
