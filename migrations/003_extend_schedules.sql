ALTER TABLE schedules ADD COLUMN classroom TEXT;
ALTER TABLE schedules ADD COLUMN status TEXT DEFAULT 'active';
ALTER TABLE schedules ADD COLUMN note TEXT;
