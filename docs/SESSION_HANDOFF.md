# SESSION HANDOFF

Files changed:
- app.py
- schema.sql
- docs/ACCESS_POLICY.md
- docs/ADMIN_UX_GUIDELINES.md
- docs/ROADMAP.md
- docs/PROJECT_STATE.md
- docs/SESSION_HANDOFF.md

Routes/pages modified:
- /users
- /schedule
- /attendance
- /payments
- /library
- /exams
- /counseling
- /masterdata

Behavior added or fixed:
- `/users` now follows the Phase 1 UX direction more closely: create form is collapsed by default, search/list stays separate, and list rows now open a focused edit panel instead of exposing only a raw ID table
- `/users` now supports owner-side editing of name, username, teacher type, and optional password reset for existing users without exposing password hashes or mixing edit controls into the result table
- `/users` now has a guarded delete action; self-delete, owner delete, and delete of accounts tied to operational data are blocked
- restored `app.py` from the clean HEAD version after a workspace encoding corruption and then reapplied the current admin UX fixes
- `/schedule` now supports deleting the selected schedule from the lesson detail panel
- `/schedule` class list no longer auto-loads by default; it stays collapsed until Query is pressed
- `/schedule` class list now shows a visible delete action inside the schedule screen for owner/manager users
- empty timetable cells now show an add action that pre-fills the schedule form with the clicked day/time/teacher and a single known room when available
- `/attendance` class picker no longer auto-expands the full class list when no class query is provided
- `/payments` now shows student name, student number, class, paid date, amount, package hours, and remaining classes instead of raw IDs/field keys
- `/library` no longer asks to search/select a teacher for loans; the logged-in user is used as the handler automatically
- `/library` loan history now shows book code/title, student name/student number, loan/return times, and handler name
- `/exams` now uses selected class/student context, exam dropdowns, and readable exam/score tables instead of raw internal IDs
- `/counseling` now hides raw student/parent IDs in the search/form/list UI and uses picker context with readable names
- `/masterdata` now has a `수납 패키지` section for package code/name/credits/list price management
- `/masterdata` payment package labels now use translation keys and the ambiguous teacher-only tab was removed because teacher management belongs under `/users`
- `/payments` now uses package master values, stores package/list price/discount, and recharges `students.remaining_credits` on save
- sample packages seeded: `RT30`, `RT60`, `WK24`, `VIP12`
- request body parsing is now cached, so CSRF checks and route handlers do not consume POST bodies twice
- dev server now runs with a threaded WSGI server so one stalled browser request does not freeze the whole app
- added a repository-level access policy document to lock role visibility/edit rules before more UI changes
- added shared admin UX guidelines to standardize query-first pages, collapsed forms, picker output, and result density
- updated project priorities to move role policy and UX structure ahead of cosmetic polish
- added an integrated roadmap that combines operational must-haves, UX stabilization, branding timing, and phased structural cleanup
- `/attendance` now stays in a true query-first state and does not render large result tables until Search is pressed
- `/attendance` row editing now uses a collapsible edit panel instead of always showing every dropdown in the table cell
- added `makeup_assignments` to connect original absences to target schedule lessons instead of only flipping a boolean on the source attendance row
- `/schedule` now supports assigning pending makeup students to a specific lesson and shows assigned makeup students in the lesson detail/card context
- lesson attendance save now auto-completes matching makeup assignments and writes back to the original absence via `makeup_completed` + `makeup_attendance_id`
- attendance rule handling is now server-driven: `present/late` always deduct credit, `absent + deduct` means charge now with no makeup, and `absent + no_deduct` means pending makeup with no immediate charge
- attendance absence options are now labeled by business meaning in the UI: `Deduct Credit` vs `Need Makeup`
- `Students Needing Makeup` now forces query-first load parameters so the pending makeup list actually renders instead of showing an empty pre-query state
- the schedule-side makeup picker now allows blank search as a valid query and treats it as "show all pending makeup students for assignment"
- makeup candidate labels in `/schedule` now show `absence date / original class / student / homeroom teacher` so operators can assign the right student without guessing
- fixed a schedule makeup picker crash when blank-search results reused the generic student picker branch without a `phone` field
- fixed the generic picker so row-provided `label` values are actually used for SQLite row candidates, which restores the detailed makeup candidate text in `/schedule`
- `/schedule` makeup assignment UI is now collapsed by default under lesson detail instead of always occupying the right-side column
- lesson attendance entry now includes assigned makeup students for that schedule so they can be marked present/late in the actual class roster flow
- class detail now shows makeup-assigned students targeting that class, and class attendance CSV exports now include makeup-related columns
- global attendance CSV exports now include `makeup_attendance_id`, `target_schedule_id`, and assignment status for auditability
- fixed two route-entry crashes caused by late variable initialization: `/attendance?lesson_mode=1` now initializes `target_schedule_id` before the makeup-student query, and `/exams` now initializes `score_exam_id` on GET as well as POST

Known issues:
- broader admin query-mode consistency still needs another pass in modules outside the routes touched above
- schedule quick-fill still requires selecting a class before saving; it only fills slot context
- browser verification is still pending for the latest `/counseling`, `/payments`, `/masterdata`, `/schedule`, `/attendance`, `/library`, and `/exams` UI changes
- payments still use a snapshot-style table and need a true ledger model in the next operational phase
- makeup assignment UI is implemented server-side but still needs browser validation for the end-to-end schedule -> attendance -> auto-complete flow
- attendance edit UI still needs one more browser pass to visually hide/show absence-only fields based on selected status

Quick verification done:
- `C:\Users\tooya\AppData\Local\Python\bin\python.exe -m py_compile app.py`
- package rows confirmed in `lms.db`
- local HTTP replay confirmed `/payments` POST returns and stores package payment with discount and credit recharge
- one-off Python validation confirmed `makeup_assignments` table is created in `lms.db`
- `C:\Users\tooya\AppData\Local\Python\bin\python.exe -m py_compile C:\RTWEB\app.py` passed after the attendance rule normalization changes

Next recommended task:
- browser-verify the attendance/makeup rule flow end-to-end, then continue Phase 1 cleanup on `/library` and remaining translation/raw-key leaks
