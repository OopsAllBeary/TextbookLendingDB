import sqlite3
from pathlib import Path
import os
import shutil
from datetime import datetime


APP_NAME = "TextbookLendingTracker"
CURRENT_SCHEMA_VERSION = 1
MAX_BACKUPS = 10


# ---------------------------------------------------------
# Application data directory
# ---------------------------------------------------------

APP_DATA_DIR = (
    Path(os.environ["LOCALAPPDATA"])
    / APP_NAME
)

APP_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Database locations
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = (
    APP_DATA_DIR / "tlTracking.db"
)

LEGACY_DB_PATH = (
    BASE_DIR / "data" / "tlTracking.db"
)


# ---------------------------------------------------------
# Backups
# ---------------------------------------------------------

BACKUP_DIR = (
    APP_DATA_DIR / "backups"
)

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def backup_database():

    if not DB_PATH.exists():
        return None

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_path = (
        BACKUP_DIR
        / f"tlTracking_{timestamp}.db"
    )

    shutil.copy2(
        DB_PATH,
        backup_path
    )

    print(
        f"Database backup created: {backup_path}"
    )

    cleanup_old_backups()

    return backup_path

def cleanup_old_backups():

    backups = sorted(
        BACKUP_DIR.glob("tlTracking_*.db"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    for old_backup in backups[MAX_BACKUPS:]:

        try:

            old_backup.unlink()

            print(
                f"Removed old backup:"
                f"\n{old_backup}"
            )

        except OSError as e:

            print(
                f"Could not remove old backup "
                f"{old_backup}: {e}"
            )

# ---------------------------------------------------------
# Legacy database migration
# ---------------------------------------------------------

def migrate_legacy_database():

    if DB_PATH.exists():
        return

    if not LEGACY_DB_PATH.exists():
        return

    print(
        "Existing database found."
    )

    print(
        f"Copying database from:\n"
        f"{LEGACY_DB_PATH}\n"
        f"to:\n"
        f"{DB_PATH}"
    )

    shutil.copy2(
        LEGACY_DB_PATH,
        DB_PATH
    )

    print(
        "Existing database copied successfully."
    )


# ---------------------------------------------------------
# Database connection
# ---------------------------------------------------------

def get_connection():

    conn = sqlite3.connect(
        DB_PATH
    )

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ---------------------------------------------------------
# Schema version
# ---------------------------------------------------------

def get_schema_version():

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            "PRAGMA user_version"
        )

        return cursor.fetchone()[0]

    finally:

        conn.close()


# ---------------------------------------------------------
# Database migrations
# ---------------------------------------------------------

def migrate_database():

    version = get_schema_version()

    print(
        f"Database schema version: {version}"
    )

    if version == 0:

        # The database already has our current schema.
        # We're simply establishing that schema as
        # version 1.

        conn = get_connection()

        try:

            conn.execute(
                "PRAGMA user_version = 1"
            )

            conn.commit()

            print(
                "Existing database marked as "
                "schema version 1."
            )

        finally:

            conn.close()

        version = 1


    if version < 4:

        print(
            "Migrating database to schema version 4..."
        )

        backup_database()

        conn = get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookstore_lookups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    application_id TEXT NOT NULL,

                    student_id TEXT,
                    program_id TEXT,
                    term_id TEXT,

                    lookup_date TEXT NOT NULL,

                    FOREIGN KEY(application_id)
                        REFERENCES applications(application_id)
                )
            """)

            if not column_exists(
                cursor,
                "applications",
                "bookstore_total_current_price"
            ):

                cursor.execute("""
                    ALTER TABLE applications
                    ADD COLUMN bookstore_total_current_price REAL
                """)


            if not column_exists(
                cursor,
                "applications",
                "bookstore_last_lookup"
            ):

                cursor.execute("""
                    ALTER TABLE applications
                    ADD COLUMN bookstore_last_lookup TEXT
                """)


            if not column_exists(
                cursor,
                "bookstore_materials",
                "lookup_id"
            ):

                cursor.execute("""
                    ALTER TABLE bookstore_materials
                    ADD COLUMN lookup_id INTEGER
                """)

            cursor.execute(
                "PRAGMA user_version = 4"
            )

            conn.commit()

            print(
                "Database successfully migrated "
                "to schema version 4."
            )

        except Exception:

            conn.rollback()

            print(
                "Database migration failed. "
                "Changes were rolled back."
            )

            raise

        finally:

            conn.close()

        version = 4

    if version < 5:
    
        print(
            "Migrating database to schema version 5..."
        )

        backup_database()

        conn = get_connection()

        try:

            cursor = conn.cursor()

            

            if not column_exists(
                cursor,
                "applications",
                "emailed"
            ):

                cursor.execute("""
                    ALTER TABLE annotations
                    ADD COLUMN emailed INTEGER NOT NULL DEFAULT 0
                """)

            cursor.execute(
                "PRAGMA user_version = 5"
            )

            conn.commit()

            print(
                "Database successfully migrated "
                "to schema version 5."
            )

        except Exception:

            conn.rollback()

            print(
                "Database migration failed. "
                "Changes were rolled back."
            )

            raise

        finally:

            conn.close()

        version = 5



def column_exists(
    cursor,
    table_name,
    column_name
):
    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    columns = cursor.fetchall()

    return any(
        row["name"] == column_name
        for row in columns
    )

# ---------------------------------------------------------
# Initialize database
# ---------------------------------------------------------

def init_database():

    migrate_legacy_database()

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # -----------------------------------------------------
        # Imports
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                import_date TEXT NOT NULL
            )
        """)

        # -----------------------------------------------------
        # Applications
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                application_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,

                first_name TEXT,
                last_name TEXT,

                email TEXT,

                pop_type TEXT,

                semester TEXT,
                campus TEXT,
                program TEXT,

                requested_device TEXT,
                requested_books_devices TEXT,

                course_names TEXT,

                submitted_date TEXT,

                current_data TEXT NOT NULL,

                last_seen_import INTEGER,

                is_deleted INTEGER NOT NULL DEFAULT 0,
                deleted_date TEXT,

                FOREIGN KEY(last_seen_import)
                    REFERENCES imports(id)
            )
        """)

        # -----------------------------------------------------
        # Annotations
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS annotations (
                application_id TEXT PRIMARY KEY,

                status TEXT DEFAULT 'New',
                notes TEXT,

                rsvp TEXT,

                created_date TEXT,
                updated_date TEXT,

                FOREIGN KEY(application_id)
                    REFERENCES applications(application_id)
            )
        """)

        # -----------------------------------------------------
        # Bookstore Materials
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookstore_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                application_id TEXT NOT NULL,
                lookup_id INTEGER,

                course TEXT,
                section TEXT,

                title TEXT,
                author TEXT,
                edition TEXT,

                isbn TEXT,

                material_type TEXT,
                requirement_type TEXT,
                requirement_label TEXT,

                publisher TEXT,
                copyright_year TEXT,

                is_package INTEGER DEFAULT 0,
                included_material INTEGER DEFAULT 0,

                created_date TEXT NOT NULL,

                FOREIGN KEY(application_id)
                    REFERENCES applications(application_id)
            )
            """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookstore_selections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                material_id INTEGER NOT NULL,

                option_type TEXT,
                option_label TEXT,

                price REAL,
                price_display TEXT,

                availability TEXT,
                binding TEXT,

                sku TEXT,

                breakage_charge REAL,
                restocking_fee REAL,
                non_rental_charges REAL,

                selected_date TEXT NOT NULL,

                FOREIGN KEY(material_id)
                    REFERENCES bookstore_materials(id)
            )
            """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookstore_lookups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                application_id TEXT NOT NULL,

                student_id TEXT,
                program_id TEXT,
                term_id TEXT,

                lookup_date TEXT NOT NULL,

                FOREIGN KEY(application_id)
                    REFERENCES applications(application_id)
            )
        """)

        conn.commit()

    finally:
        cursor.close()

    migrate_database()


def clear_database():

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            "PRAGMA foreign_keys = OFF"
        )

        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            """
        )

        tables = [
            row["name"]
            for row in cursor.fetchall()
        ]

        for table in tables:

            cursor.execute(
                f'DELETE FROM "{table}"'
            )

        # Reset AUTOINCREMENT counters.
        try:

            cursor.execute(
                "DELETE FROM sqlite_sequence"
            )

        except Exception:

            pass

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

# ---------------------------------------------------------
# Standalone initialization
# ---------------------------------------------------------

if __name__ == "__main__":
    init_database()

    print("Database initialized")
    print(f"Database location: {DB_PATH}")
    print(f"Schema version: {get_schema_version()}")