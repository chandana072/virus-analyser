import psycopg2

# Paste your actual Render PostgreSQL connection string here
DATABASE_URL = "postgresql://virususer:K9evWmVorkld10vaI6uhasKzjkb8u0zN@dpg-d1nu3kc9c44c73eps510-a/virusdb"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

conn.commit()
cur.close()
conn.close()

print(" users table created successfully.")
