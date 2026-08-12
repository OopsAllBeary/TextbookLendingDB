from db import get_connection
from annotations import get_annotation
from datetime import datetime


def get_application(application_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM applications
        WHERE application_id = ?
    """, (application_id,))

    application = cursor.fetchone()

    conn.close()

    if application is None:
        return None

    return dict(application)


def get_application_with_annotation(application_id):

    application = get_application(application_id)

    if application is None:
        return None

    annotation = get_annotation(application_id)

    if annotation:
        application.update(annotation)

    return application

def get_all_applications():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.*,
            an.status,
            an.notes,
            an.rsvp,
            an.created_date,
            an.updated_date
        FROM applications a
        LEFT JOIN annotations an
            ON a.application_id = an.application_id
        WHERE COALESCE(a.is_deleted, 0) = 0
        ORDER BY a.submitted_date DESC,
            a.last_name,
            a.first_name
""")

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]

def delete_application(application_id):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE applications
            SET
                is_deleted = 1,
                deleted_date = ?
            WHERE application_id = ?
            """,
            (
                datetime.now().isoformat(),
                application_id
            )
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def restore_application(application_id):

    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE applications
            SET
                is_deleted = 0,
                deleted_date = NULL
            WHERE application_id = ?
            """,
            (application_id,)
        )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()

def get_deleted_applications():

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.*,
                an.status,
                an.notes,
                an.rsvp,
                an.created_date,
                an.updated_date
            FROM applications a
            LEFT JOIN annotations an
                ON a.application_id = an.application_id
            WHERE a.is_deleted = 1
            ORDER BY
                a.deleted_date DESC,
                a.last_name,
                a.first_name
        """)

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        conn.close()