import sqlite3
from contextlib import closing


class Database:
    def __init__(self, db_name='chat.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            self.conn.commit()

    def register_user(self, username, password):
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute('''
                    INSERT INTO users (username, password)
                    VALUES (?, ?)
                ''', (username, password))
                self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def validate_user(self, username, password):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('''
                SELECT * FROM users 
                WHERE username = ? AND password = ?
            ''', (username, password))
            return cursor.fetchone() is not None

    def close(self):
        self.conn.close()
