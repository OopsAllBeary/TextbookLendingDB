from datetime import datetime
from db import get_connection




def get_annotation(application_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM annotations
        WHERE application_id = ?
    """, (application_id,))

    annotation = cursor.fetchone()

    conn.close()

    if annotation is None:
        return None

    return annotation

def _update_annotation_field(application_id, field_name, value):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO annotations (
            application_id,
            created_date
        )
        VALUES (?, ?)
    """, (
        application_id,
        datetime.now().isoformat()
    ))

    cursor.execute(f"""
        UPDATE annotations
        SET
            {field_name} = ?,
            updated_date = ?
        WHERE application_id = ?
    """, (
        value,
        datetime.now().isoformat(),
        application_id
    ))

    conn.commit()
    conn.close()


def set_status(application_id, status):
    _update_annotation_field(
        application_id,
        "status",
        status
    )


def set_notes(application_id, notes):
    _update_annotation_field(
        application_id,
        "notes",
        notes
    )


def set_rsvp(application_id, rsvp):
    _update_annotation_field(
        application_id,
        "rsvp",
        rsvp
    )

# def update_annotation(application_id, status=None, notes=None, rsvp=None):

#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#     INSERT INTO annotations (
#         application_id,
#         status,
#         notes,
#         rsvp,
#         created_date,
#         updated_date
#     )
#     VALUES (?, ?, ?, ?, ?, ?)

#     ON CONFLICT(application_id)
#     DO UPDATE SET
#         status = COALESCE(excluded.status, annotations.status), 
#         notes = COALESCE(excluded.notes, annotations.notes), 
#         rsvp = COALESCE(excluded.rsvp, annotations.rsvp), 
#         updated_date = excluded.updated_date

#     """, (
#         application_id,
#         status,
#         notes,
#         rsvp,
#         datetime.now().isoformat(),
#         datetime.now().isoformat()
#     ))

#     conn.commit()
#     conn.close()
