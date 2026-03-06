ALTER TABLE homework ADD COLUMN teacher_id INTEGER;
ALTER TABLE homework ADD COLUMN description TEXT;
ALTER TABLE homework ADD COLUMN status TEXT DEFAULT 'active';
ALTER TABLE homework ADD COLUMN updated_at TEXT;
UPDATE homework SET teacher_id=COALESCE(teacher_id, created_by) WHERE teacher_id IS NULL;

ALTER TABLE homework_submissions ADD COLUMN feedback_teacher_id INTEGER;
ALTER TABLE homework_submissions ADD COLUMN updated_at TEXT;
UPDATE homework_submissions SET feedback_teacher_id=COALESCE(feedback_teacher_id, feedback_by) WHERE feedback_teacher_id IS NULL;
