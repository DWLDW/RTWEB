# PROJECT STATE

Project: ReadingTown LMS

Stack:
- Python
- Flask
- SQLite
- Server-rendered HTML

Main file:
app.py (~5000 lines)

Architecture:
Single dispatcher function handling path-based routing.

Major Domains:
- auth
- dashboard
- users/admin
- students
- classes
- schedule
- attendance
- homework
- exams
- counseling
- payments
- announcements
- library
- logs

Recent Improvements:
- Explicit query mode added to major admin pages
- Scroll preservation introduced
- Student homeroom teacher support
- Schedule class picker improvements
- Operational student/class list improvements

Current Pain Points:
- Large monolithic app.py
- Inconsistent query UX on some pages
- Scroll jumping on certain interactions
- Legacy ID-driven admin UI in some modules

Current Priorities:
1. Product guardrails: role policy, query-first loading, raw-ID/internal-key cleanup
2. Operational must-haves: payments ledger, refund/unpaid/discount handling, class history, multi-guardian support, stronger audit logs
3. Workflow stabilization: search vs create/edit separation on heavy admin pages
4. Practical efficiency: dashboard today-view, saved filters, export standardization, stronger student detail
5. Education quality and parent communication after operations stabilize
6. Branding and structural cleanup after workflow rules are stable

Current UX Focus:
- collapse create/edit forms by default on heavy admin pages
- remove raw ID and untranslated internal field-key exposure
- reduce first-load data volume
- standardize picker results and empty states
- define parent vs student visibility boundaries before more UI work

Roadmap Reference:
- see `docs/ROADMAP.md` for the integrated execution order

Testing Expectations:
- py_compile must pass
- query mode behavior correct
- scroll restore works
- tables readable
- POST flows preserved
