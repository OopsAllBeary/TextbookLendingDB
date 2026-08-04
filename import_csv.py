import json
from datetime import datetime

import pandas as pd

from db import get_connection

import hashlib


COLUMN_MAP = {
    "First Name": "first_name",
    "Last Name": "last_name",
    "Email": "email",
    "Student ID": "student_id",
    "Student Population Type": "pop_type",
    "Semester Applied For": "semester",
    "Campus": "campus",
    "Program": "program",
    "Electronic Device": "requested_device",
    "Requesting Book and/or Device": "requested_books_devices",
    "Course Name and Number": "course_names",
    "Date Submitted": "submitted_date"
}

DATABASE_COLUMNS = [
    "application_id",
    "student_id",
    "first_name",
    "last_name",
    "email",
    "pop_type",
    "semester",
    "campus",
    "program",
    "requested_device",
    "requested_books_devices",
    "course_names",
    "submitted_date",
    "current_data",
    "last_seen_import"
]

def clean_csv_row(row):
    clean_row = {}

    for csv_name, db_name in COLUMN_MAP.items():
        clean_row[db_name] = str(row.get(csv_name, "")).strip()

    return clean_row

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

def build_upsert_query():
    insert_columns = ", ".join(DATABASE_COLUMNS)

    placeholders = ", ".join(
        ["?"] * len(DATABASE_COLUMNS)
    )

    update_columns = [
        col for col in DATABASE_COLUMNS
        if col != "application_id"
    ]

    updates = ", ".join(
        [
            f"{col} = excluded.{col}"
            for col in update_columns
        ]
    )

    return f"""
    INSERT INTO applications (
        {insert_columns}
    )
    VALUES ({placeholders})

    ON CONFLICT(application_id)
    DO UPDATE SET
        {updates}
    """

def import_applications(filename):
    stats = {
        "processed": 0,
        "new": 0,
        "updated": 0
    }
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

    query = build_upsert_query()


    for _, row in df.iterrows():

        stats["processed"] += 1

        clean_row = clean_csv_row(row)

        application_id = make_application_id(clean_row)

        cursor.execute("""
            SELECT 1
            FROM applications
            WHERE application_id = ?
        """, (application_id,))

        exists = cursor.fetchone() is not None

        values = [
            application_id,
            clean_row["student_id"],
            clean_row["first_name"],
            clean_row["last_name"],
            clean_row["email"],
            clean_row["pop_type"],
            clean_row["semester"],
            clean_row["campus"],
            clean_row["program"],
            clean_row["requested_device"],
            clean_row["requested_books_devices"],
            clean_row["course_names"],
            clean_row["submitted_date"],
            json.dumps(clean_row),
            import_id
        ]

        cursor.execute(query, values)

        if exists:
            stats["updated"] += 1
        else:
            stats["new"] += 1

    conn.commit()
    conn.close()

    print(stats)
    return stats