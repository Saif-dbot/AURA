import hashlib
import os
import sqlite3
from typing import Optional, Tuple

from src.database.connection import get_connection, initialize_database


class AuthManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize()
        self._ensure_default_user()

    def _initialize(self) -> None:
        initialize_database()

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
        return digest.hex()

    def create_user(self, username: str, password: str, role: str = "Admin") -> bool:
        username = username.strip()
        if not username or len(password) < 6:
            return False
        salt = os.urandom(16).hex()
        password_hash = self._hash_password(password, salt)
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, salt, password_hash, role, is_active) VALUES (?, ?, ?, ?, 1)",
                    (username, salt, password_hash, role),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate(self, username: str, password: str) -> Optional[Tuple[str, str]]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT username, salt, password_hash, role, is_active FROM users WHERE username = ?",
                (username.strip(),),
            ).fetchone()
        if not row:
            return None
        if int(row[4]) != 1:
            return None
        hashed = self._hash_password(password, row[1])
        if hashed != row[2]:
            return None
        return row[0], row[3]

    def _ensure_default_user(self) -> None:
        with get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        if row and int(row[0]) == 0:
            self.create_user("admin", "admin123", role="Admin")
