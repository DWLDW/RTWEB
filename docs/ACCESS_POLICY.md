# ACCESS POLICY

Project: ReadingTown LMS

This document defines the intended visibility and edit permissions for each role.
Use this before changing UI, route behavior, or data exposure.

## Core Rules
- Hide internal numeric IDs from normal UI unless the value is explicitly needed for admin debugging.
- Default to least privilege.
- Parent and student access must be scoped to linked student records only.
- Manager can operate day-to-day workflows but should not own global security settings.
- Owner is the only role with full system authority.

## Role Matrix

### Owner
- Can view and edit all domains.
- Can manage users, roles, master data, schedules, attendance, homework, exams, counseling, payments, library, announcements, and logs.
- Can delete operational records where the product allows deletion.
- Can manage package master, class master, and user credentials.

### Manager
- Can view and edit most operational domains.
- Can manage students, classes, schedules, attendance, homework, exams, counseling, payments, library, and announcements.
- Can manage master data needed for operation.
- Cannot manage owner accounts or platform-level security settings.
- Should not see raw password values or hidden debug data.

### Teacher
- Can view assigned classes, assigned students, schedule context, attendance, homework, exams, counseling, announcements, and library handling needed for daily work.
- Can create and update teaching records tied to their scope.
- Cannot manage users, package pricing, or global master data outside teaching scope.
- Should not see financial internals beyond what is operationally required.

### Parent
- Can view only linked child data.
- Can view attendance summary, homework, exam results, announcements, and payment history for linked children.
- Cannot edit academic or operational records.
- Counseling visibility should be limited to records explicitly intended for guardian sharing.

### Student
- Can view only own data.
- Can view attendance summary, homework, exam results, and announcements.
- Cannot view guardian-only financial context unless explicitly approved.
- Cannot edit operational records.

## Domain Rules

### Users
- Owner: full management.
- Manager: limited operational management only if explicitly allowed.
- Teacher/Parent/Student: no access.

### Students
- Owner/Manager: full view and edit.
- Teacher: only assigned/related students.
- Parent: linked children only.
- Student: self only.

### Counseling
- Owner/Manager: full operational access.
- Teacher: create and view teaching-relevant records in scope.
- Parent: only guardian-shareable counseling summaries if product policy enables it.
- Student: hidden by default unless a separate student-safe note type is introduced.

### Payments
- Owner/Manager: full create/view.
- Teacher: no payment editing.
- Parent: linked children payment history only.
- Student: payment history only if explicitly enabled by policy.

### Library
- Owner/Manager/Teacher: operational access.
- Parent/Student: history only if later required; not default.

### Logs
- Owner only.

## Data Exposure Rules
- Replace raw IDs in tables with human-readable names, student number, class, role, or code.
- Keep internal IDs in hidden inputs or route parameters only when necessary.
- Avoid exposing phone numbers in picker result lists unless the workflow requires phone-based confirmation.
- Do not expose password hashes, raw session tokens, or internal audit payloads in UI.

## Open Decisions
- Whether students can view payment history directly.
- Whether parents can view all counseling notes or only guardian-shareable notes.
- Whether managers can edit all users or only student/parent/teacher operational accounts.
