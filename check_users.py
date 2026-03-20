import sqlite3
import os

# Connect to the SQLite database
db_path = os.path.join('instance', 'stroke_prediction.db')
print(f"Database path: {db_path}")

if not os.path.exists(db_path):
    print("Database file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if users table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
table_exists = cursor.fetchone()

if not table_exists:
    print("Users table does not exist!")
    conn.close()
    exit(1)

# Query all users
cursor.execute("SELECT id, email, full_name, role, created_at, last_login FROM users;")
users = cursor.fetchall()

print("\nExisting users in database:")
print("-" * 80)
if users:
    for user in users:
        print(f"ID: {user[0]}")
        print(f"Email: {user[1]}")
        print(f"Full Name: {user[2]}")
        print(f"Role: {user[3]}")
        print(f"Created: {user[4]}")
        print(f"Last Login: {user[5]}")
        print("-" * 40)
else:
    print("No users found in database")

conn.close()