CREATE TABLE IF NOT EXISTS students (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE,
  student_no TEXT UNIQUE,
  name_ko TEXT NOT NULL,
  name_en TEXT,
  phone TEXT,
  guardian_name TEXT,
  guardian_phone TEXT,
  current_class_id INTEGER,
  remaining_credits REAL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active',
  enrolled_at TEXT,
  leave_start_date TEXT,
  leave_end_date TEXT,
  memo TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id),
  FOREIGN KEY(current_class_id) REFERENCES classes(id)
);

INSERT INTO students(user_id, student_no, name_ko, status, created_at)
SELECT u.id, printf('S%04d', u.id), u.name, 'active', datetime('now')
FROM users u
LEFT JOIN students s ON s.user_id = u.id
WHERE u.role = 'student' AND s.id IS NULL;
