import sqlite3
import bcrypt

def check_users():
    """List all existing users and their hashed passwords."""
    conn = sqlite3.connect('chats.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users")
    users = cursor.fetchall()
    conn.close()

    print("Existing Users:")
    for user in users:
        print(f"Username: {user[0]}, Hashed Password: {user[1]}")

def verify_password(username, password):
    """Verify if the provided username and password are correct."""
    conn = sqlite3.connect('chats.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
        print("Password is correct!")
    else:
        print("Invalid username or password.")

if __name__ == "__main__":
    # List all users
    check_users()

    # Example: Verify a specific username and password
    username_to_check = input("Enter username to verify: ")
    password_to_check = input("Enter password to verify: ")
    verify_password(username_to_check, password_to_check)