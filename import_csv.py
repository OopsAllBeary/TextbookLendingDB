import json
from datetime import datetime

import pandas as pd

from db import get_connection

from annotations import (
    save_imported_annotations
)

import hashlib


COLUMN_MAP = {
    "first name": "first_name",
    "last name": "last_name",
    "email": "email",
    "student id": "student_id",
    "student population type": "pop_type",
    "semester applied for": "semester",
    "campus": "campus",
    "program": "program",
    "electronic device": "requested_device",
    "requesting book and/or device": "requested_books_devices",
    "course name and number": "course_names",
    "date submitted": "submitted_date"
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

        clean_row[db_name] = safe_string(
            row.get(csv_name, "")
        )

    return clean_row

def safe_string(value):
    if value is None:
        return ""
    return str(value).strip()

def get_imported_status(row):
    approved = safe_string(
        row.get("approved", "")
    ).lower()

    denied = safe_string(
        row.get("denied", "")
    ).lower()

    waitlist = safe_string(
        row.get("waitlist", "")
    ).lower()

    true_values = {
        "1",
        "true",
        "yes",
        "y",
        "x",
        "approved"
    }

    if denied in true_values:
        return "Denied"

    if approved in true_values:
        return "Approved"

    if waitlist in true_values:
        return "Waitlist"

    return None

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


def normalize_csv_columns(df):

    df.columns = [
        str(column).strip().lower()
        for column in df.columns
    ]

    return df


def import_applications(filename):
    stats = {
        "processed": 0,
        "new": 0,
        "updated": 0
    }

    df = pd.read_csv(
        filename,
        dtype=str
    ).fillna("")

    df = normalize_csv_columns(
        df
    )


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

        application_id = make_application_id(
            clean_row
        )

        # -----------------------------------------
        # Read annotation columns from CSV
        # -----------------------------------------

        imported_notes = safe_string(
            row.get("notes", "")
        )

        imported_rsvp = safe_string(
            row.get("rsvp", "")
        )

        imported_status = get_imported_status(
            row
        )

        # -----------------------------------------
        # Check whether application already exists
        # -----------------------------------------

        cursor.execute(
            """
            SELECT 1
            FROM applications
            WHERE application_id = ?
            """,
            (application_id,)
        )

        exists = (
            cursor.fetchone()
            is not None
        )

        # -----------------------------------------
        # Save application
        # -----------------------------------------

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

        cursor.execute(
            query,
            values
        )

        # -----------------------------------------
        # Import annotations
        # -----------------------------------------

        save_imported_annotations(
            cursor,
            application_id,
            notes=(
                imported_notes
                if "notes" in df.columns
                and imported_notes
                else None
            ),
            rsvp=(
                imported_rsvp
                if "rsvp" in df.columns
                and imported_rsvp
                else None
            ),
            status=imported_status
        )

        # -----------------------------------------
        # Statistics
        # -----------------------------------------

        if exists:

            stats["updated"] += 1

        else:

            stats["new"] += 1


    conn.commit()
    conn.close()

    print(stats)
    return stats