param()

$prompt = @"
After finishing this task, update docs/SESSION_HANDOFF.md with:
- files changed
- routes/pages modified
- behavior added or fixed
- known issues
- quick verification done
- next recommended task

Keep it short and practical.
Do not restate full code.
"@

Set-Clipboard -Value $prompt
Write-Host "Copied Codex finish prompt to clipboard."
