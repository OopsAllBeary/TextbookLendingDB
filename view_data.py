from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT
    application_id,
    student_id
FROM applications
""")

for row in cursor.fetchall():
    print(dict(row))

conn.close()