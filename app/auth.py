# CircleTable -- Christopher Liu, Yusuf Elsharawy, Deven Maheshwari, Naomi Naranjo
# SoftDev
# P00: CircleStories

"""Authentication

Handles all of the login/registration functionality for CircleStories
including input validation.
"""

import hashlib
import sqlite3

DB_FILE = "circlestories.db"


def hash_password(password: str) -> str:
    """Hashes the provided password using SHA512."""

    return hashlib.sha512(password.encode()).hexdigest()


def validate_registration(username: str, password: str, password_check: str) -> list:
    """Validates input for new user creation."""

    with sqlite3.connect(DB_FILE) as db:

        c = db.cursor()

        errors = []
        if len(username) == 0:
            errors.append("Username is required")
        if (
            c.execute(
                "SELECT * FROM users WHERE username=:username", {"username": username}
            ).fetchone()
            is not None
        ):
            errors.append("Username already in use")

        if len(password) == 0:
            errors.append("Password is required")
        if len(password_check) == 0:
            errors.append("Repeat password is required")

        if password != password_check:
            errors.append("Passwords must match")

        return errors


def create_user(username: str, password: str, password_check: str) -> list:
    """Validates inputs and creates a new user if all inputs are valid."""

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                user_id     TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                username    TEXT,
                password    TEXT
            )
        """
        )

        errors = validate_registration(username, password, password_check)
        if not errors:
            password_hash = hash_password(password)
            c.execute(
                "INSERT INTO users(username, password) VALUES (?, ?)",
                (username, password_hash),
            )

        return errors


def authenticate_user(username: str, password: str) -> bool:
    """Authenticates a user using the given credentials."""

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()

        if not c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users';"
        ).fetchone():
            return False

        user_pw = c.execute(
            "SELECT password FROM users WHERE username=:username",
            {"username": username},
        ).fetchone()
        if user_pw is not None and user_pw[0] == hash_password(password):
            return True

        return False


def get_user_id(username: str) -> str:
    """Returns the user ID associated with the given username, None if user
    doesn't exist."""

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()

        user_id = c.execute(
            "SELECT user_id FROM users WHERE username=:username", {"username": username}
        ).fetchone()

        if user_id is not None:
            return user_id[0]
        return None


def get_username(user_id: str) -> str:
    """Returns the username associated with the given user_id, None if user
    doesn't exist."""

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()

        username = c.execute(
            "SELECT username FROM users WHERE user_id=:user_id", {"user_id": user_id}
        ).fetchone()

        if username is not None:
            return username[0]
        return None
