import sqlite3
from pathlib import Path

Path("data").mkdir(exist_ok=True)

DB_PATH = "data/tlTracking.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS imports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        import_date TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        application_id TEXT PRIMARY KEY,
        student_id TEXT NOT NULL,

        first_name TEXT,
        last_name TEXT,

        semester TEXT,
        campus TEXT,
        program TEXT,

        requested_device TEXT,
        requested_books_devices TEXT,

        course_names TEXT,

        submitted_date TEXT,

        current_data TEXT NOT NULL,

        last_seen_import INTEGER,

        FOREIGN KEY(last_seen_import) REFERENCES imports(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS annotations (
        application_id TEXT PRIMARY KEY,
        notes TEXT,
        status TEXT DEFAULT 'New',
        rsvp TEXT,
        created_at TEXT,
        last_updated TEXT,
        FOREIGN KEY(application_id) REFERENCES applications(application_id)
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized")

