# ROADMAP

Project: ReadingTown LMS

This roadmap combines operational must-haves, access policy work, UI/UX cleanup, and later structure work into one execution order.

## Priority 0: Product Guardrails
- Lock role-based access rules before expanding more UI.
- Apply query-first behavior to large admin pages.
- Remove raw IDs, untranslated field keys, and internal-only strings from visible UI.

Reason:
- Without this, later UX work and feature additions will have to be reworked.

## Priority 1: Operational Must-Haves

### 1. Payments Ledger
- Replace simple payment snapshots with ledger-style payment records.
- Support discount, refund, unpaid balance, and adjustment history.
- Keep package purchases and credit recharge linked to the ledger model.

### 2. Outstanding / Refund / Discount Handling
- Add status and reason fields for partial payment, refund, discount, and manual adjustment.
- Show current balance clearly in student and payment views.

### 3. Student-Class History
- Track class moves over time instead of only the current class.
- Preserve who changed it and when.

### 4. Multi-Guardian Support
- Allow multiple guardians per student.
- Support primary/secondary guardian roles.
- Avoid storing guardian relationships only as a single text field.

### 5. Stronger Audit Logging
- Expand audit coverage for create/update/delete actions on critical domains.
- Prioritize payments, users, master data, attendance corrections, and class assignment changes.

## Priority 2: Workflow and UX Stabilization

### 1. Users Page
- Separate search/list from create/edit.
- Default list should not auto-load.
- Clarify which roles can be edited by owner vs manager.

### 2. Master Data Page
- Collapse create forms by section.
- Use section tabs or accordion groups.
- Avoid showing every registration form at once.

### 3. Attendance Page
- Enforce query-first loading.
- Reduce default row count.
- Make result actions denser and easier to scan.

### 4. Library Page
- Replace untranslated strings and field-key leaks.
- Separate student selection, book registration, loan/return actions, and history.
- Keep result tables operational and compact.

### 5. Schedule Page
- Keep timetable primary.
- Keep schedule create/edit panel compact and collapsible.
- Preserve quick-fill behavior from empty slots.

### 6. Shared Picker Modernization
- Replace raw link lists with compact result rows or cards.
- Show name + student number/class/status instead of raw IDs or extra phone data by default.

## Priority 3: Practical Efficiency

### 1. Admin Dashboard: Today View
- Missing attendance input
- Homework pending review
- Recent unpaid payments
- Students needing counseling follow-up

### 2. Saved Filters
- Save common filter presets for heavy admin pages.

### 3. Export Standardization
- Normalize CSV/XLSX export behavior and column naming.

### 4. Student Detail as Operations Hub
- Bring attendance, homework, exams, payments, counseling, and library into one strong student-centered operational view.

## Priority 4: Education Quality
- Score trend views
- Homework completion trend views
- Attendance pattern analysis
- Weekly student reports

## Priority 5: Parent Communication
- Automatic notification rules
- Counseling follow-up status
- Weekly parent summaries based on exams, homework, and attendance

## Priority 6: Branding and Visual Polish
- Add academy logo to shared layout
- Standardize labels and empty-state copy
- Apply a more intentional typography scale
- Change fonts only after page density and layout rules stabilize

## Priority 7: Structural Cleanup
- Split `app.py` by domain in phases
- Extract shared form, permission, and validation helpers
- Refactor only after role policy and operational flows are stable

## Phase 1 Execution Order
1. Access policy enforcement pass on `/users`, `/payments`, `/counseling`, `/attendance`
2. `/users` UX cleanup
3. `/masterdata` UX cleanup
4. `/attendance` UX cleanup
5. `/library` UX cleanup
6. shared picker cleanup
7. branding baseline: logo + common labels

## Not First
- Full visual redesign
- Heavy frontend rewrite
- Large one-shot modularization
