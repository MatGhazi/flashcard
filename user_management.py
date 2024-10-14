import sqlite3
import bcrypt
import os

def init_user_db():
    conn = sqlite3.connect('databases/users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def add_user(username: str, password: str):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('databases/users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        print(f"User {username} added successfully.")
        # Create a new database for the user
        init_user_flashcard_db(username)
    except sqlite3.IntegrityError:
        print(f"User {username} already exists.")
    finally:
        conn.close()

def init_user_flashcard_db(username: str):
    db_path = f"databases/{username}.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        review_date DATE NOT NULL,
        level INTEGER NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

import sqlite3

def get_all_flashcards(username: str):
    db_path = f"databases/{username}.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute a query to get all rows from the flashcards table
    cursor.execute("SELECT * FROM flashcards")
    flashcards = cursor.fetchall()

    # Close the connection
    conn.close()

    # Print the flashcards or return them
    for card in flashcards:
        print(f"ID: {card[0]}, Question: {card[1]}, Answer: {card[2]}, Review Date: {card[3]}, Level: {card[4]}")

    return flashcards


def list_users():
    conn = sqlite3.connect('databases/users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    conn.close()
    if users:
        print("Registered users:")
        for user in users:
            print(user[0])
    else:
        print("No users registered.")

def delete_user(username: str):
    conn = sqlite3.connect('databases/users.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    if cursor.rowcount > 0:
        print(f"User {username} deleted successfully.")
        # Delete the user's flashcard database
        db_path = f"databases/{username}.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Flashcard database for {username} deleted.")
    else:
        print(f"User {username} not found.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_user_db()
    while True:
        print("\n1. Add user")
        print("2. List users")
        print("3. Delete user")
        print("4. show all flashcards")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            add_user(username, password)
        elif choice == '2':
            list_users()
        elif choice == '3':
            username = input("Enter username to delete: ")
            delete_user(username)
        elif choice == '4':
            username = input("Enter username: ")
            get_all_flashcards(username)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

    print("Exiting user management.")