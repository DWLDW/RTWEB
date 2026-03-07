# RTWEB handoff

## Current baseline
- Single-file WSGI app (`app.py`) with SQLite.
- Runtime schema ensures + profile integrity repair in `init_db()`.
- English default i18n, ko/en/zh supported.

## Key routes in use
- `/students`
- `/classes/<id>`
- `/masterdata`
- `/schedule`
- `/attendance`
- `/homework`

## Source of truth
- auth/role: `users`
- student profile: `students`
- teacher profile: `teachers` (+ `users`)
- class master: `classes`
- timetable: `schedules`
- attendance/evaluation: `attendance`

## Already implemented highlights
- weekly schedule copy with duplicate-skip
- attendance absence charge fields + makeup flags + `credit_delta`
- correction-safe credit recalculation helper logic
- responsive/mobile stabilization + mobile typography uplift in shared CSS

## DB notes
- `classes`: `status` / `memo` / `credit_unit`
- `attendance`: `absence_charge_type` / `requires_makeup` / `makeup_completed` / `credit_delta` / `makeup_attendance_id`
- migration `012` included (`012_extend_attendance_absence_rules.sql`)

## Verification helpers
- `python app.py`
- `python scripts/db_preflight.py`

## Commands previously used for verification
- `git status -sb && wc -l app.py schema.sql scripts/db_preflight.py README.md docs/db_design.md`
- `git log --oneline --decorate -8`
- `rg -n "^def (init_db|render_html|copy_week_schedules|repair_profile_integrity|ensure_extended_columns|ensure_attendance_columns|load_locale_files|app)\\b|if path == \"/schedule\"|if path == \"/attendance\"|if path == \"/homework\"|if path == \"/students\"|if path == \"/masterdata\"|if path.startswith\\(\"/classes/\"\\)" app.py`
- `nl -ba app.py | sed -n '720,870p'`
- `nl -ba app.py | sed -n '904,980p'`
- `nl -ba schema.sql | sed -n '1,180p'`
- `nl -ba docs/db_design.md | sed -n '1,170p'`
- `nl -ba scripts/db_preflight.py | sed -n '1,198p'`
- `nl -ba README.md | sed -n '1,140p'`
