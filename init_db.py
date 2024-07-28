import sqlite3

from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect("database.sqlite3")

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    face_id TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    face_image TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    foreign key (user_id) references users(id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance_logs (
    id SERIAL PRIMARY KEY,
    attendance_id INTEGER NOT NULL,
    attendance_note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    foreign key (attendance_id) references attendances(id)
);
""")

conn.commit()
conn.close()
