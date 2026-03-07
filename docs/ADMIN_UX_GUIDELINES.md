# ADMIN UX GUIDELINES

This document defines the shared UI/UX rules for large admin pages in this repository.

## Objectives
- Reduce cognitive load.
- Avoid loading large lists by default.
- Separate lookup flows from create/edit flows.
- Keep dense operational pages readable on desktop.

## Shared Page Pattern

### 1. Query First
- Large admin pages must start in an empty state.
- Show `Press Query to load data.` until the user searches.
- Empty filters plus Query may load the full list only when the page is intended to support that.

### 2. Search and Input Separation
- Search/filter area should be visually separate from create/edit forms.
- Create/edit forms should be collapsed by default on heavy pages.
- Use a clear `Add`, `New`, or `Open Form` trigger to reveal forms.

### 3. Result Density
- Prefer compact rows/cards over oversized forms.
- Keep only operationally relevant columns visible.
- Move secondary metadata into detail panels, tooltips, or expandable rows.

### 4. Picker Behavior
- Pickers should not dump long raw link lists without structure.
- Picker results should show:
  - primary label
  - one or two secondary identifiers such as student number or class
  - optional status badge
- Avoid showing raw IDs in visible picker rows.

### 5. Edit Pattern
- Do not mix inline editing with large result tables unless the action is truly high frequency.
- Prefer:
  - result list
  - selected detail panel
  - focused edit form

### 6. Empty State Copy
- Use short operational copy.
- Good:
  - `Press Query to load data.`
  - `No matching students.`
  - `No class selected.`
- Avoid raw debug-like placeholders such as `ID: -`.

## Page-Specific Guidance

### Users
- Split `search/list` from `create/edit`.
- Default list should not auto-load.
- Replace raw ID table emphasis with role, status, and action entry points.

### Master Data
- Use section tabs or accordion groups.
- Only the active section's form should be visible.
- Class creation should not sit beside course, level, room, and time-slot creation all at once.

### Schedule
- Keep timetable primary.
- Secondary forms should be compact and collapsible.
- Empty slot actions should prefill context.

### Attendance
- Default to date-bounded query.
- Avoid rendering large full tables on first load.
- Put edit actions in a more compact pattern than multiple large controls per row.

### Library
- Separate:
  - student selection
  - book registration
  - loan/return processing
  - result history
- Replace untranslated field keys with operational labels.

## Visual Direction
- Preserve the current server-rendered approach.
- Improve spacing and hierarchy before applying heavier branding changes.
- Add logo support and a cleaner type scale after the structural cleanup starts landing.
- Font changes should come after layout density rules are stabilized.

## Phase 1 Targets
1. `/users`
2. `/masterdata`
3. `/attendance`
4. `/library`
5. `/schedule`

## Out of Scope For Phase 1
- Full app redesign
- Mobile-first redesign of dense admin pages
- Complex client-side component frameworks
