import sqlite3
import os
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

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

# Create a default admin user
admin_email = "admin@gmail.com"
admin_password = "admin#143"
admin_full_name = "System Administrator"

# Check if admin already exists
cursor.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
existing_admin = cursor.fetchone()

if existing_admin:
    print(f"Admin user with email {admin_email} already exists!")
    print("Do you want to reset the password? (y/n): ", end="")
    response = input().lower()
    if response == 'y':
        # Update password
        password_hash = generate_password_hash(admin_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", 
                      (password_hash, admin_email))
        conn.commit()
        print(f"Password reset for admin user {admin_email}")
    else:
        print("Password not changed.")
else:
    # Create new admin user
    user_id = str(uuid.uuid4())
    password_hash = generate_password_hash(admin_password)
    created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    
    cursor.execute("""
        INSERT INTO users (id, full_name, email, password_hash, role, created_at, is_active)
        VALUES (?, ?, ?, ?, 'admin', ?, 1)
    """, (user_id, admin_full_name, admin_email, password_hash, created_at))
    
    conn.commit()
    print(f"Created new admin user:")
    print(f"  Email: {admin_email}")
    print(f"  Password: {admin_password}")
    print(f"  Full Name: {admin_full_name}")

conn.close()
print("Done!")