param(
    [Parameter(Mandatory = $true)]
    [string]$Task
)

$prompt = @"
Follow docs/CODEX_RULES.md strictly.

Task:
$Task

Important execution rules:
- modify one route block at a time
- use Python patch scripts for multiline edits
- no large PowerShell multiline replacement
- run py_compile after each route block change
- stop immediately on failure
- preserve existing behavior
- keep changes minimal and localized

After finishing, update docs/SESSION_HANDOFF.md and output only:
IMPLEMENTATION SUMMARY
- files changed
- routes/pages updated
- key behavior added/fixed
- quick manual test checklist
"@

Set-Clipboard -Value $prompt
Write-Host "Copied Codex delta prompt to clipboard."
