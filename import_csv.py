import json
from datetime import datetime

import pandas as pd

from db import get_connection

APPLICATION_ID_COLUMN = "ApplicationID"
STUDENT_ID_COLUMN = "StudentID"


def import_csv(filename):
    df = pd.read_csv(filename)

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

        application_id = str(row[APPLICATION_ID_COLUMN])
        student_id = str(row[STUDENT_ID_COLUMN])

        row_json = json.dumps(row.to_dict(), default=str)

        cursor.execute("""
            INSERT INTO applications (
                application_id,
                student_id,
                current_data,
                last_seen_import
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(application_id)
            DO UPDATE SET
                student_id = excluded.student_id,
                current_data = excluded.current_data,
                last_seen_import = excluded.last_seen_import
        """, (
            application_id,
            student_id,
            row_json,
            import_id
        ))

    conn.commit()
    conn.close()

    print("Import Complete")