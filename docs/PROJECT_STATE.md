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
1. Global admin scroll stabilization
2. Shared table readability improvements
3. Explicit query mode consistency
4. Modernize legacy admin pages
5. Gradual modularization

Testing Expectations:
- py_compile must pass
- query mode behavior correct
- scroll restore works
- tables readable
- POST flows preserved
