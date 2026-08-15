import json

from datetime import datetime

from db import get_connection


def save_bookstore_results(
    application_id,
    lookup_id,
    materials
):
    conn = get_connection()
    cursor = conn.cursor()

    saved_materials = []

    try:

        for material in materials:

            cursor.execute(
                """
                INSERT INTO bookstore_materials (
                    application_id,
                    lookup_id,
                    course,
                    section,
                    title,
                    author,
                    edition,
                    isbn,
                    material_type,
                    requirement_type,
                    requirement_label,
                    publisher,
                    copyright_year,
                    is_package,
                    included_material,
                    options_json,
                    created_date
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    application_id,
                    lookup_id,

                    material.get("course"),
                    material.get("section"),

                    material.get("title"),
                    material.get("author"),
                    material.get("edition"),

                    material.get("isbn"),

                    material.get("material_type"),

                    material.get(
                        "requirement_type"
                    ),

                    material.get(
                        "requirement_label"
                    ),

                    material.get("publisher"),

                    material.get(
                        "copyright_year"
                    ),

                    int(
                        material.get(
                            "is_package",
                            False
                        )
                    ),

                    int(
                        material.get(
                            "included_material",
                            False
                        )
                    ),

                    json.dumps(
                        material.get(
                            "options",
                            []
                        )
                    ),

                    datetime.now().isoformat()
                )
            )

            material_id = cursor.lastrowid

            material["id"] = material_id

            saved_materials.append(
                material_id
            )

    except Exception:

        conn.rollback()
        raise

    else:

        conn.commit()

    finally:

        conn.close()

    return saved_materials

def clear_bookstore_selections_for_lookup(lookup_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM bookstore_selections
            WHERE material_id IN (
                SELECT id
                FROM bookstore_materials
                WHERE lookup_id = ?
            )
            """,
            (lookup_id,)
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def delete_bookstore_selection(
    selection_id
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM bookstore_selections
            WHERE id = ?
            """,
            (selection_id,)
        )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

def get_all_bookstore_selections_for_backup():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                material_id,
                option_type,
                option_label,
                price,
                price_display,
                availability,
                binding,
                sku,
                breakage_charge,
                restocking_fee,
                non_rental_charges,
                selected_date
            FROM bookstore_selections
            ORDER BY id
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:

        conn.close()

def delete_bookstore_selection(material_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM bookstore_selections
            WHERE material_id = ?
            """,
            (
                material_id,
            )
        )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

def save_bookstore_selection(
    material_id,
    option
):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM bookstore_selections
            WHERE material_id = ?
            """,
            (material_id,)
        )

        cursor.execute(
            """
            INSERT INTO bookstore_selections (
                material_id,
                option_type,
                option_label,
                price,
                price_display,
                availability,
                binding,
                sku,
                breakage_charge,
                restocking_fee,
                non_rental_charges,
                selected_date
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                material_id,

                option.get("type"),
                option.get("label"),

                option.get("price"),

                option.get(
                    "price_display"
                ),

                option.get(
                    "availability"
                ),

                option.get(
                    "binding"
                ),

                option.get(
                    "sku"
                ),

                option.get(
                    "breakage_charge"
                ),

                option.get(
                    "restocking_fee"
                ),

                option.get(
                    "non_rental_charges"
                ),

                datetime.now().isoformat()
            )
        )

        conn.commit()

        return cursor.lastrowid

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

def save_bookstore_lookup(
    application_id,
    total_current_price
):

    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE applications
            SET
                bookstore_total_current_price = ?,
                bookstore_last_lookup = ?
            WHERE application_id = ?
            """,
            (
                total_current_price,
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

def get_bookstore_lookup_summary(
    application_id
):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                bl.id AS lookup_id,
                bl.lookup_date,
                COUNT(bm.id) AS material_count
            FROM bookstore_lookups bl
            LEFT JOIN bookstore_materials bm
                ON bm.lookup_id = bl.id
            WHERE bl.application_id = ?
            GROUP BY
                bl.id,
                bl.lookup_date
            ORDER BY bl.id DESC
            LIMIT 1
            """,
            (application_id,)
        )

        row = cursor.fetchone()

        if row is None:

            return {
                "lookup_id": None,
                "lookup_date": None,
                "material_count": 0
            }

        return dict(row)

    finally:

        conn.close()

def create_bookstore_lookup(
    application_id,
    student_id,
    program_id,
    term_id
):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO bookstore_lookups (
                application_id,
                student_id,
                program_id,
                term_id,
                lookup_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                application_id,
                student_id,
                program_id,
                term_id,
                datetime.now().isoformat()
            )
        )

        conn.commit()

        return cursor.lastrowid

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

def get_latest_bookstore_lookup(
    application_id
):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM bookstore_lookups
            WHERE application_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (application_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:

        conn.close()

def get_bookstore_materials(
    application_id
):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                bm.*
            FROM bookstore_materials bm
            JOIN bookstore_lookups bl
                ON bm.lookup_id = bl.id
            WHERE
                bl.application_id = ?
                AND bl.id = (
                    SELECT id
                    FROM bookstore_lookups
                    WHERE application_id = ?
                    ORDER BY id DESC
                    LIMIT 1
                )
            ORDER BY
                bm.course,
                bm.section,
                bm.title
            """,
            (
                application_id,
                application_id
            )
        )

        rows = cursor.fetchall()

        materials = []

        for row in rows:

            material = dict(row)

            options_json = material.get(
                "options_json"
            )

            if options_json:

                try:

                    material["options"] = json.loads(
                        options_json
                    )

                except (
                    json.JSONDecodeError,
                    TypeError
                ):

                    material["options"] = []

            else:

                material["options"] = []

            materials.append(
                material
            )

        return materials

    finally:

        conn.close()

def get_bookstore_total_current_price(
    application_id
):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                bookstore_total_current_price
            FROM applications
            WHERE application_id = ?
            """,
            (application_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return 0.0

        return float(
            row["bookstore_total_current_price"]
            or 0
        )

    finally:

        conn.close()

def get_master_book_list():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                bs.id AS selection_id,

                a.student_id,

                bm.id AS material_id,

                bm.isbn,
                bm.title,
                bm.author,
                bm.edition,

                bs.option_type,
                bs.option_label,
                bs.price,
                bs.price_display,

                bs.availability,
                bs.binding,

                bl.id AS lookup_id

            FROM bookstore_selections bs

            JOIN bookstore_materials bm
                ON bs.material_id = bm.id

            JOIN bookstore_lookups bl
                ON bm.lookup_id = bl.id

            JOIN applications a
                ON bl.application_id = a.application_id

            ORDER BY
                a.student_id,
                bm.title
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:

        conn.close()

def clear_all_bookstore_selections():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM bookstore_selections
            """
        )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

def restore_bookstore_selections(
    selections
):

    if not selections:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        for selection in selections:

            cursor.execute(
                """
                INSERT INTO bookstore_selections (
                    material_id,
                    option_type,
                    option_label,
                    price,
                    price_display,
                    availability,
                    binding,
                    sku,
                    breakage_charge,
                    restocking_fee,
                    non_rental_charges,
                    selected_date
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    selection.get(
                        "material_id"
                    ),

                    selection.get(
                        "option_type"
                    ),

                    selection.get(
                        "option_label"
                    ),

                    selection.get(
                        "price"
                    ),

                    selection.get(
                        "price_display"
                    ),

                    selection.get(
                        "availability"
                    ),

                    selection.get(
                        "binding"
                    ),

                    selection.get(
                        "sku"
                    ),

                    selection.get(
                        "breakage_charge"
                    ),

                    selection.get(
                        "restocking_fee"
                    ),

                    selection.get(
                        "non_rental_charges"
                    ),

                    selection.get(
                        "selected_date"
                    )
                )
            )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

def get_bookstore_selections_total():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                COALESCE(
                    SUM(price),
                    0
                ) AS total
            FROM bookstore_selections
            """
        )

        row = cursor.fetchone()

        return float(
            row["total"]
            or 0
        )

    finally:

        conn.close()

def delete_bookstore_selection(selection_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM bookstore_selections
            WHERE id = ?
            """,
            (selection_id,)
        )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()

def get_all_bookstore_selections():

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                bs.id AS selection_id,
                bm.id AS material_id,
                bm.isbn,
                bl.student_id,

                TRIM(
                    COALESCE(
                        a.first_name,
                        ''
                    )
                    || ' '
                    ||
                    COALESCE(
                        a.last_name,
                        ''
                    )
                ) AS student_name,

                bs.price,
                bs.price_display,

                bs.option_label,

                bm.title,

                bm.course

            FROM bookstore_selections bs

            JOIN bookstore_materials bm
                ON bs.material_id = bm.id

            JOIN bookstore_lookups bl
                ON bm.lookup_id = bl.id

            JOIN applications a
                ON bl.application_id = a.application_id

            ORDER BY
                bm.course,
                bm.title
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:

        conn.close()

def delete_bookstore_selection(selection_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM bookstore_selections
            WHERE id = ?
            """,
            (selection_id,)
        )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

def get_bookstore_selected_total(application_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                COALESCE(
                    SUM(bs.price),
                    0
                ) AS total

            FROM bookstore_selections bs

            JOIN bookstore_materials bm
                ON bs.material_id = bm.id

            JOIN bookstore_lookups bl
                ON bm.lookup_id = bl.id

            WHERE bl.application_id = ?
            """,
            (application_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return 0.0

        return float(
            row["total"] or 0
        )

    finally:

        conn.close()

def get_bookstore_selections_for_application(
    application_id
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                bs.material_id,
                bs.option_type,
                bs.sku

            FROM bookstore_selections bs

            JOIN bookstore_materials bm
                ON bs.material_id = bm.id

            JOIN bookstore_lookups bl
                ON bm.lookup_id = bl.id

            WHERE bl.application_id = ?

            AND bl.id = (
                SELECT id
                FROM bookstore_lookups
                WHERE application_id = ?
                ORDER BY id DESC
                LIMIT 1
            )
            """,
            (
                application_id,
                application_id
            )
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:

        conn.close()

def get_bookstore_selections_for_application(
    application_id
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                bs.material_id,
                bs.option_type,
                bs.option_label,
                bs.price,
                bs.price_display,
                bs.sku

            FROM bookstore_selections bs

            JOIN bookstore_materials bm
                ON bs.material_id = bm.id

            JOIN bookstore_lookups bl
                ON bm.lookup_id = bl.id

            WHERE bl.application_id = ?

            AND bl.id = (
                SELECT id
                FROM bookstore_lookups
                WHERE application_id = ?
                ORDER BY id DESC
                LIMIT 1
            )
            """,
            (
                application_id,
                application_id
            )
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:

        conn.close()