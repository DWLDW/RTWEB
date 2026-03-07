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
- `/payments` now uses package master values, stores package/list price/discount, and recharges `students.remaining_credits` on save
- sample packages seeded: `RT30`, `RT60`, `WK24`, `VIP12`
- request body parsing is now cached, so CSRF checks and route handlers do not consume POST bodies twice
- dev server now runs with a threaded WSGI server so one stalled browser request does not freeze the whole app
- added a repository-level access policy document to lock role visibility/edit rules before more UI changes
- added shared admin UX guidelines to standardize query-first pages, collapsed forms, picker output, and result density
- updated project priorities to move role policy and UX structure ahead of cosmetic polish
- added an integrated roadmap that combines operational must-haves, UX stabilization, branding timing, and phased structural cleanup

Known issues:
- broader admin query-mode consistency still needs another pass in modules outside the routes touched above
- schedule quick-fill still requires selecting a class before saving; it only fills slot context
- browser verification is still pending for the latest `/counseling`, `/payments`, `/masterdata`, `/schedule`, `/attendance`, `/library`, and `/exams` UI changes
- payments still use a snapshot-style table and need a true ledger model in the next operational phase

Quick verification done:
- `C:\Users\tooya\AppData\Local\Python\bin\python.exe -m py_compile app.py`
- package rows confirmed in `lms.db`
- local HTTP replay confirmed `/payments` POST returns and stores package payment with discount and credit recharge

Next recommended task:
- continue Phase 1 with `/masterdata` and `/attendance`, using the `/users` page as the baseline pattern for collapsed forms and focused edit flows
