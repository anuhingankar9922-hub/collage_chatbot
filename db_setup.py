"""Run once to initialize and seed the database: python database/db_setup.py"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_connection import get_connection

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    lead_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    preferred_course TEXT,
    source_query TEXT,
    status TEXT DEFAULT 'new',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL UNIQUE,
    department TEXT,
    duration_years INTEGER,
    fee_per_year REAL,
    seats_available INTEGER,
    eligibility TEXT
);

CREATE TABLE IF NOT EXISTS placements (
    placement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    year INTEGER,
    avg_package_lpa REAL,
    highest_package_lpa REAL,
    placement_percent REAL,
    top_recruiters TEXT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE IF NOT EXISTS chat_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    predicted_intent TEXT,
    confidence_score REAL,
    bot_response TEXT,
    was_fallback BOOLEAN DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

SEED_COURSES = """
INSERT OR IGNORE INTO courses (course_name, department, duration_years, fee_per_year, seats_available, eligibility)
VALUES
('Computer Engineering', 'CE', 4, 120000, 120, '12th with PCM, min 45%'),
('Information Technology', 'IT', 4, 115000, 60, '12th with PCM, min 45%'),
('Mechanical Engineering', 'Mech', 4, 100000, 90, '12th with PCM, min 45%'),
('Civil Engineering', 'Civil', 4, 95000, 60, '12th with PCM, min 45%');
"""

SEED_PLACEMENTS = """
INSERT INTO placements (course_id, year, avg_package_lpa, highest_package_lpa, placement_percent, top_recruiters)
SELECT course_id, 2025, 5.5, 18.0, 88.0, 'TCS, Infosys, Wipro, Capgemini, Persistent'
FROM courses WHERE course_name = 'Computer Engineering'
AND NOT EXISTS (SELECT 1 FROM placements WHERE course_id = (SELECT course_id FROM courses WHERE course_name='Computer Engineering') AND year = 2025);

INSERT INTO placements (course_id, year, avg_package_lpa, highest_package_lpa, placement_percent, top_recruiters)
SELECT course_id, 2025, 5.0, 14.0, 85.0, 'TCS, Cognizant, Infosys'
FROM courses WHERE course_name = 'Information Technology'
AND NOT EXISTS (SELECT 1 FROM placements WHERE course_id = (SELECT course_id FROM courses WHERE course_name='Information Technology') AND year = 2025);

INSERT INTO placements (course_id, year, avg_package_lpa, highest_package_lpa, placement_percent, top_recruiters)
SELECT course_id, 2025, 4.2, 9.0, 78.0, 'Tata Motors, Bajaj Auto, L&T'
FROM courses WHERE course_name = 'Mechanical Engineering'
AND NOT EXISTS (SELECT 1 FROM placements WHERE course_id = (SELECT course_id FROM courses WHERE course_name='Mechanical Engineering') AND year = 2025);

INSERT INTO placements (course_id, year, avg_package_lpa, highest_package_lpa, placement_percent, top_recruiters)
SELECT course_id, 2025, 4.0, 8.0, 75.0, 'L&T Construction, Shapoorji Pallonji'
FROM courses WHERE course_name = 'Civil Engineering'
AND NOT EXISTS (SELECT 1 FROM placements WHERE course_id = (SELECT course_id FROM courses WHERE course_name='Civil Engineering') AND year = 2025);
"""

if __name__ == "__main__":
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.executescript(SEED_COURSES)
    conn.executescript(SEED_PLACEMENTS)
    conn.commit()
    conn.close()
    print("Database initialized and seeded at:", os.path.join(os.path.dirname(os.path.abspath(__file__)), "college_chatbot.db"))
