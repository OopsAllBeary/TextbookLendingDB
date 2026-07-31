from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT
    application_id,
    student_id,
    first_name,
    last_name,
    program,
    campus,
    requested_books_devices,
    submitted_date
FROM applications
ORDER BY last_name
""")

rows = cursor.fetchall()

for row in rows:
    print("-" * 50)
    for key in row.keys():
        print(f"{key}: {row[key]}")

conn.close()