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
- fixed schedule lesson-date generation so `Attendance & Evaluation` now passes the actual date for the selected weekday in the current week instead of reusing the raw reference date
- fixed attendance boolean filters for `requires_makeup` and `makeup_completed`; they now bind integer params instead of string params, which restores the `Students Needing Makeup` query results
- makeup completion now moves credit ownership back to the original absence row: when a makeup lesson is completed, the source absence is updated to `absence_charge_type=deduct`, `makeup_completed=1`, and a deducted credit delta
- lesson-mode attendance rows for makeup students now keep `credit_delta=0` on the makeup lesson itself so makeup completion does not double-deduct credits
- completed makeup assignments now remain visible in the target lesson context for that lesson date instead of disappearing immediately after save
- schedule lesson cards, lesson detail, class detail, and attendance CSV/list now include the makeup lesson date so operators can see when the makeup actually happened
- lesson-mode attendance now continues to include makeup-assigned students even after completion for the same lesson date, so Monday lesson rosters/history remain stable after save
- `/schedule` lesson cards now use a primary `Attendance & Evaluation` action plus a compact `More` dropdown for secondary actions, which frees space for student names and makeup labels
- the schedule-side makeup assignment UI is no longer a separate collapsed card in the right column; it now sits open under the schedule create/edit form when a lesson is selected
- schedule makeup-student search now paginates in 12-row pages with previous/next navigation instead of silently truncating the result set
- the schedule card `Attendance & Evaluation` button was reduced so its visual weight is closer to the `More` control and the card layout stays denser
- `/users`, `/attendance`, `/payments`, and `/library` large tables now show total result counts and numeric page links instead of only prev/next-style paging
- schedule makeup-student search now shows total candidate count and numeric page links as well, not just a truncated first page
- `/counseling`, `/homework`, `/students`, and `/masterdata` class list now also use page-sized result views with total counts and numeric page links

Known issues:
- broader admin query-mode consistency still needs another pass in modules outside the routes touched above
- schedule quick-fill still requires selecting a class before saving; it only fills slot context
- browser verification is still pending for the latest `/counseling`, `/payments`, `/masterdata`, `/schedule`, `/attendance`, `/library`, and `/exams` UI changes
- payments still use a snapshot-style table and need a true ledger model in the next operational phase
- makeup assignment UI is implemented server-side but still needs browser validation for the end-to-end schedule -> attendance -> auto-complete flow
- attendance edit UI still needs one more browser pass to visually hide/show absence-only fields based on selected status
- completed makeup status labels in some schedule/detail tables still show raw `assigned/completed` values and should be translated in the next UX pass
- schedule `More` dropdown behavior was validated by compile only; browser layout verification is still needed for overlap/z-index edge cases
- the makeup search pager range text is currently English-only (`Showing x-y`) and should be moved to translations in the next i18n pass
- library sort headers now reset the correct page key for each table (`book_page`, `loan_page`); browser verification is still pending
- masterdata pagination currently covers the class list first; course/level/room/package tables can be paged later if they become large enough

Quick verification done:
- `C:\Users\tooya\AppData\Local\Python\bin\python.exe -m py_compile app.py`
- package rows confirmed in `lms.db`
- local HTTP replay confirmed `/payments` POST returns and stores package payment with discount and credit recharge
- one-off Python validation confirmed `makeup_assignments` table is created in `lms.db`
- `C:\Users\tooya\AppData\Local\Python\bin\python.exe -m py_compile C:\RTWEB\app.py` passed after the attendance rule normalization changes
- `C:\Users\tooya\AppData\Local\Python\bin\python.exe -m py_compile C:\RTWEB\app.py` passed after the makeup credit/date persistence changes
- `C:\Users\tooya\AppData\Local\Python\bin\python.exe -m py_compile C:\RTWEB\app.py` passed after the schedule action/menu cleanup
- `C:\Users\tooya\AppData\Local\Python\bin\python.exe -m py_compile C:\RTWEB\app.py` passed after makeup-search pagination and schedule button-size adjustments
- `C:\Users\tooya\AppData\Local\Python\bin\python.exe -m py_compile C:\RTWEB\app.py` passed after total-count/numeric-pagination updates
- `C:\Users\tooya\AppData\Local\Python\bin\python.exe -m py_compile C:\RTWEB\app.py` passed after counseling/homework/students/masterdata pagination updates

Next recommended task:
- browser-verify total-count and numeric page links on `/users`, `/students`, `/attendance`, `/counseling`, `/homework`, `/payments`, `/library`, `/masterdata`, and schedule makeup search, then clean up remaining table i18n/raw-key leaks
