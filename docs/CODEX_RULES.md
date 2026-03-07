# CODEX RULES

These rules must be followed for all development work in this repository.

## Core Principles
- Make minimal invasive changes.
- Preserve existing behavior unless explicitly instructed otherwise.
- Avoid large refactors unless explicitly requested.
- Maintain the current Flask + server-rendered HTML architecture.
- Prefer compatibility over redesign.

## Editing Rules
- Modify one route block at a time.
- Do NOT perform large PowerShell multiline string replacements.
- Use Python patch scripts for multiline edits.
- After each route block change, run py_compile.
- If py_compile fails, stop immediately and report.
- Write files as UTF-8 without BOM.

## Query Mode Rules
- Large admin pages must use explicit query mode.
- Initial page visit must NOT auto-load large lists.
- Show "Press Query to load data."
- Query with filters -> filtered results.
- Query with empty filters -> full list.
- Do NOT apply query gating to small dropdown reference data.

## Scroll Preservation Rules
- Preserve scroll position for same-context admin interactions.
- Applies to:
  - query/search forms
  - picker selection links
  - inline update flows
  - internal admin navigation returning to the same context

Whitelist approach preferred:
- form.query-form
- form.picker-form
- a[data-preserve-scroll="1"]

Do not apply to unrelated navigation.

## UI Modernization
- Gradually modernize legacy ID-driven admin pages.
- Prefer picker/search workflows.
- Keep raw ID inputs only as fallback.

## Table Readability
- Prevent vertical single-character wrapping.
- Prefer horizontal scroll over unreadable text.
- Use shared CSS instead of page-specific hacks.

## Modularization
- Modularization must be phased.
- Move code first, refactor later.
- Avoid large one-shot app.py splits.

## Output Format
After each change output:

IMPLEMENTATION SUMMARY
- files changed
- routes/pages updated
- key behavior added
- quick manual test checklist

Do not restate full code.
