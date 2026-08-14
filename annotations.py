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

    status_map = {
        "new": "New",
        "approved": "Approved",
        "denied": "Denied",
        "waitlist": "WaitList",
        "wait_list": "WaitList",
        "wait list": "WaitList"
    }

    normalized_status = status_map.get(
        str(status).strip().lower(),
        "New"
    )

    _update_annotation_field(
        application_id,
        "status",
        normalized_status
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

def set_emailed(application_id, emailed):
    _update_annotation_field(
        application_id,
        "emailed",
        int(bool(emailed))
    )

def save_imported_annotations(
    cursor,
    application_id,
    notes=None,
    rsvp=None,
    status=None
):

    # Make sure an annotation row exists
    cursor.execute(
        """
        INSERT OR IGNORE INTO annotations (
            application_id,
            created_date
        )
        VALUES (?, ?)
        """,
        (
            application_id,
            datetime.now().isoformat()
        )
    )

    updates = []
    values = []

    if notes is not None:

        updates.append(
            "notes = ?"
        )

        values.append(
            notes
        )

    if rsvp is not None:

        updates.append(
            "rsvp = ?"
        )

        values.append(
            rsvp
        )

    if status is not None:

        updates.append(
            "status = ?"
        )

        values.append(
            status
        )

    if not updates:
        return

    updates.append(
        "updated_date = ?"
    )

    values.append(
        datetime.now().isoformat()
    )

    values.append(
        application_id
    )

    cursor.execute(
        f"""
        UPDATE annotations
        SET
            {", ".join(updates)}
        WHERE application_id = ?
        """,
        values
    )

