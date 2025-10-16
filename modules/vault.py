"""
Interact with sqlite3 databases.
"""

import os
import sqlite3
from modules import crypt

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    k TEXT PRIMARY KEY,
    v BLOB
);

CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title BLOB NOT NULL,
    username BLOB NOT NULL,
    password BLOB NOT NULL
);
"""

class Vault:
    def __init__(self, path: os.PathLike) -> None:
        self.path = path
        self.conn = None
        self.aes = None
    
    def open(self):
        first_time = not os.path.exists(self.path)
        
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        cur.executescript(DB_SCHEMA)
        conn.commit()
        
        self.conn = conn
        self.first_time = first_time

    def unlock(self, password: bytes):
        assert self.conn is not None

        cur = self.conn.cursor()
        cur.execute("SELECT v FROM meta WHERE k='salt'")

        salt = cur.fetchone()[0]
        key = crypt.argon2_derive(password, salt, 32)

        cur.execute("SELECT v FROM meta WHERE k='keycheck'")
        stored_check = cur.fetchone()[0]

        if not crypt.compare(crypt.digest(key), stored_check):
            return 1

        aes = crypt.AESGCM(key)
        del key

        self.aes = aes

    def initialize(self, password: bytes):
        assert self.conn is not None

        salt = crypt.generate(128)
        key = crypt.argon2_derive(password, salt, 32)

        aes = crypt.AESGCM(key)
        keycheck = crypt.digest(key)
        del key

        cur = self.conn.cursor()
        cur.execute("INSERT INTO meta (k, v) VALUES (?, ?)", ("salt", salt))
        cur.execute("INSERT INTO meta (k, v) VALUES (?, ?)", ("keycheck", keycheck))
        self.commit()

        self.aes = aes

    def get_rows(self):
        assert self.conn is not None

        cur = self.conn.cursor()
        cur.execute("SELECT id, title, username, password FROM entries")
        rows = cur.fetchall()

        return rows

    def add_entry(self, title: str, username: str, password: str):
        assert self.conn is not None
        assert self.aes is not None

        enc_title = self.aes.encrypt(title.encode())
        enc_username = self.aes.encrypt(username.encode())
        enc_password = self.aes.encrypt(password.encode())

        values = (enc_title, enc_username, enc_password)

        cur = self.conn.cursor()

        cur.execute("INSERT INTO entries (title, username, password) VALUES (?, ?, ?)", values)

        self.commit()

    def edit_entry(self, entry_id: int, title: str, username: str, password: str):
        assert self.conn is not None
        assert self.aes is not None

        enc_title = self.aes.encrypt(title.encode())
        enc_username = self.aes.encrypt(username.encode())
        enc_password = self.aes.encrypt(password.encode())

        values = (enc_title, enc_username, enc_password, entry_id)

        cur = self.conn.cursor()

        cur.execute("UPDATE entries SET title=?, username=?, password=? WHERE id=?", values)

        self.commit()

    def delete_entry(self, entry_id: int):
        assert self.conn is not None

        values = (entry_id, )

        cur = self.conn.cursor()

        cur.execute("DELETE FROM entries WHERE id=?", values)

        self.commit()

    def commit(self):
        assert self.conn is not None

        self.conn.commit()

    def close(self):
        assert self.conn is not None

        self.conn.close()
