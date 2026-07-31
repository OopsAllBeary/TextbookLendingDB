import json
from datetime import datetime

import pandas as pd

from db import get_connection

import hashlib


COLUMN_MAP = {
    "First Name": "first_name",
    "Last Name": "last_name",
    "Student ID": "student_id",
    "Semester Applied For": "semester",
    "Campus": "campus",
    "Program": "program",
    "Electronic Device": "requested_device",
    "Requesting Book and/or Device": "requested_books_devices",
    "Course Name and Number": "course_names",
    "Date Submitted": "submitted_date"
}

def safe_string(value):
    if value is None:
        return ""
    return str(value).strip()

def make_application_id(clean_row):
    unique_string = "|".join([
        safe_string(clean_row["student_id"]),
        safe_string(clean_row["submitted_date"]),
        safe_string(clean_row["course_names"])
    ])

    return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()

def import_csv(filename):
    df = pd.read_csv(filename, dtype=str).fillna("")

    print(f"Loaded Row Count: {len(df)}")
    print(f"Columns:")
    for column in df.columns:
        print(f" - {column}")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO imports (filename, import_date)
        VALUES (?, ?)
    """, (
        filename,
        datetime.now().isoformat()
    ))

    import_id = cursor.lastrowid


    for _, row in df.iterrows():

        clean_row = {}

        for csv_name, db_name in COLUMN_MAP.items():
            clean_row[db_name] = row[csv_name]

        application_id = make_application_id(clean_row)

        cursor.execute("""
        INSERT INTO applications (
            application_id,
            student_id,
            first_name,
            last_name,
            semester,
            campus,
            program,
            requested_device,
            requested_books_devices,
            course_names,
            submitted_date,
            current_data,
            last_seen_import
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        
        ON CONFLICT(application_id)
        DO UPDATE SET
            student_id = excluded.student_id,
            first_name = excluded.first_name,
            last_name = excluded.last_name,
            semester = excluded.semester,
            campus = excluded.campus,
            program = excluded.program,
            requested_device = excluded.requested_device,
            requested_books_devices = excluded.requested_books_devices,
            course_names = excluded.course_names,
            submitted_date = excluded.submitted_date,
            current_data = excluded.current_data,
            last_seen_import = excluded.last_seen_import
        """, (
            application_id,
            clean_row["student_id"],
            clean_row["first_name"],
            clean_row["last_name"],
            clean_row["semester"],
            clean_row["campus"],
            clean_row["program"],
            clean_row["requested_device"],
            clean_row["requested_books_devices"],
            clean_row["course_names"],
            clean_row["submitted_date"],
            json.dumps(clean_row),
            import_id
        ))

    conn.commit()
    conn.close()

    print("Import Complete")