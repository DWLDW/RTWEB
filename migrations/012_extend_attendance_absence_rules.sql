ALTER TABLE classes ADD COLUMN credit_unit REAL DEFAULT 1;
ALTER TABLE attendance ADD COLUMN absence_charge_type TEXT;
ALTER TABLE attendance ADD COLUMN requires_makeup INTEGER DEFAULT 0;
ALTER TABLE attendance ADD COLUMN makeup_completed INTEGER DEFAULT 0;
ALTER TABLE attendance ADD COLUMN credit_delta REAL DEFAULT 0;
ALTER TABLE attendance ADD COLUMN makeup_attendance_id INTEGER;
