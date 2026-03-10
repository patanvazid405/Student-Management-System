import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("students.db")


class StudentDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._initialize_database()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _initialize_database(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    course TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                )
                """
            )

    def fetch_students(self):
        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT id, name, age, course, email FROM students ORDER BY id DESC"
            )
            return cursor.fetchall()

    def add_student(self, name, age, course, email):
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO students (name, age, course, email)
                VALUES (?, ?, ?, ?)
                """,
                (name, age, course, email),
            )
            return cursor.lastrowid

    def update_student(self, student_id, name, age, course, email):
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE students
                SET name = ?, age = ?, course = ?, email = ?
                WHERE id = ?
                """,
                (name, age, course, email, student_id),
            )

    def delete_student(self, student_id):
        with self._connect() as connection:
            connection.execute("DELETE FROM students WHERE id = ?", (student_id,))
