from db import get_connection
from annotations import get_annotation


DISPLAY_COLUMNS = [
    "student_id",
    "first_name",
    "last_name",
    "pop_type",
    "course_names",
    "requested_device",
    "requested_books_devices",
    "program",
    "campus",
    "status",
    "rsvp",
    "notes"
]

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
        ORDER BY a.submitted_date DESC,
            a.last_name,
            a.first_name
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]