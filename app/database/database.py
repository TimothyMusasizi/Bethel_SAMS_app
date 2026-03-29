import sqlite3
from contextlib import closing
import os
import sys
from typing import List, Optional

from app.models.members import Member
from app.models.attendance import Attendance


class Database:
    """Simple SQLite-backed storage for members, attendance and option lists.

    This implementation is defensive (creates missing tables) and provides
    helpers used by the UI for class/duty/activity option management.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            if getattr(sys, "frozen", False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))

            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "Records.db")

        self.create_tables()

    # -----------------
    # Member operations
    # -----------------

    def addMember(self, member: Member) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO members (member_id, name, contact, email, dob, occupation, marital_status, duty, class, activity, photo_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        None,
                        member.name,
                        member.contact,
                        member.email,
                        member.dob,
                        member.occupation,
                        member.marital_status,
                        getattr(member, "duty", ""),
                        member.member_class,
                        member.activity_status,
                        member.photo_path,
                    ),
                )
                last = cur.lastrowid
                cur.execute("UPDATE members SET member_id = ? WHERE id = ?", (str(last), last))

    def getMember(self, member_id) -> Optional[Member]:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM members WHERE member_id = ?", (str(member_id),))
                row = cur.fetchone()
                if not row:
                    return None

                # Read column names so we can safely map values even if schema changed
                cur.execute("PRAGMA table_info('members')")
                cols = [c[1] for c in cur.fetchall()]

                def _val(name, default=""):
                    try:
                        idx = cols.index(name)
                    except ValueError:
                        return default
                    try:
                        return row[idx]
                    except Exception:
                        return default

                m = Member()
                m.id = _val('id', None)
                m.member_id = _val('member_id', None)
                m.name = _val('name', '')
                m.contact = _val('contact', '')
                m.email = _val('email', '')
                m.dob = _val('dob', '')
                m.occupation = _val('occupation', '')
                m.marital_status = _val('marital_status', '')
                m.duty = _val('duty', '')
                m.member_class = _val('class', '')
                m.activity_status = _val('activity', '')
                m.photo_path = _val('photo_path', '')
                return m

    def updateMember(self, member: Member) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE members
                    SET name = ?, contact = ?, email = ?, dob = ?, occupation = ?, marital_status = ?, duty = ?, class = ?, activity = ?, photo_path = ?
                    WHERE id = ?
                    """,
                    (
                        member.name,
                        member.contact,
                        member.email,
                        member.dob,
                        member.occupation,
                        member.marital_status,
                        getattr(member, "duty", ""),
                        member.member_class,
                        member.activity_status,
                        member.photo_path,
                        member.id,
                    ),
                )

    def getAllMembers(self) -> List[Member]:
        members: List[Member] = []
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("PRAGMA table_info('members')")
                cols = [c[1] for c in cur.fetchall()]

                def _val_from_row(row, name, default=""):
                    try:
                        idx = cols.index(name)
                    except ValueError:
                        return default
                    try:
                        return row[idx]
                    except Exception:
                        return default

                cur.execute("SELECT * FROM members ORDER BY name")
                for row in cur.fetchall():
                    m = Member()
                    m.id = _val_from_row(row, 'id', None)
                    m.member_id = _val_from_row(row, 'member_id', None)
                    m.name = _val_from_row(row, 'name', '')
                    m.contact = _val_from_row(row, 'contact', '')
                    m.email = _val_from_row(row, 'email', '')
                    m.dob = _val_from_row(row, 'dob', '')
                    m.occupation = _val_from_row(row, 'occupation', '')
                    m.marital_status = _val_from_row(row, 'marital_status', '')
                    m.duty = _val_from_row(row, 'duty', '')
                    m.member_class = _val_from_row(row, 'class', '')
                    m.activity_status = _val_from_row(row, 'activity', '')
                    m.photo_path = _val_from_row(row, 'photo_path', '')
                    members.append(m)
        return members

    def deleteMember(self, member_id: str) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM members WHERE member_id = ?", (member_id,))

    # -------------------
    # Attendance handling
    # -------------------

    @staticmethod
    def _quote_ident(name: str) -> str:
        return '"' + name.replace('"', '""') + '"'

    def addAttendance(self, attendance: Attendance) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS attendance (date TEXT PRIMARY KEY)")
                cur.execute("PRAGMA table_info('attendance')")
                existing = {r[1] for r in cur.fetchall()}

                member_cols = list(attendance.records.keys())
                for mid in member_cols:
                    if str(mid) not in existing:
                        cur.execute(f'ALTER TABLE attendance ADD COLUMN {self._quote_ident(str(mid))} INTEGER DEFAULT 0')

                quoted = [self._quote_ident(str(m)) for m in member_cols]
                cols_sql = ', '.join([self._quote_ident('date')] + quoted)
                placeholders = ', '.join(['?'] * (1 + len(member_cols)))
                values = [1 if bool(attendance.records[mid]) else 0 for mid in member_cols]
                try:
                    cur.execute(f'INSERT INTO attendance ({cols_sql}) VALUES ({placeholders})', [attendance.date] + values)
                except sqlite3.IntegrityError:
                    if member_cols:
                        set_sql = ', '.join(f'{q} = ?' for q in quoted)
                        cur.execute(f'UPDATE attendance SET {set_sql} WHERE date = ?', values + [attendance.date])

    def getAttendance(self, date: str) -> Optional[Attendance]:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM attendance WHERE date = ?", (date,))
                row = cur.fetchone()
                if not row:
                    return None
                cur.execute("PRAGMA table_info('attendance')")
                cols = [c[1] for c in cur.fetchall()]
                att = Attendance(date)
                for idx, col in enumerate(cols[1:], start=1):
                    try:
                        att.records[col] = bool(row[idx])
                    except IndexError:
                        att.records[col] = False
                return att

    def updateAttendance(self, attendance: Attendance) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("PRAGMA table_info('attendance')")
                existing = {r[1] for r in cur.fetchall()}
                member_cols = list(attendance.records.keys())
                for mid in member_cols:
                    if str(mid) not in existing:
                        cur.execute(f'ALTER TABLE attendance ADD COLUMN {self._quote_ident(str(mid))} INTEGER DEFAULT 0')

                quoted = [self._quote_ident(str(m)) for m in member_cols]
                values = [1 if bool(attendance.records[mid]) else 0 for mid in member_cols]
                if member_cols:
                    set_sql = ', '.join(f'{q} = ?' for q in quoted)
                    cur.execute(f'UPDATE attendance SET {set_sql} WHERE date = ?', values + [attendance.date])

    def getAllAttendanceDates(self) -> List[str]:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT date FROM attendance ORDER BY date")
                return [r[0] for r in cur.fetchall()]

    def get_attendance_for_member(self, member_id) -> dict:
        result = {}
        dates = self.getAllAttendanceDates() or []
        for d in dates:
            att = self.getAttendance(d)
            if not att:
                result[d] = False
                continue
            recs = att.records
            val = recs.get(str(member_id))
            if val is None and isinstance(member_id, str) and member_id.isdigit():
                val = recs.get(int(member_id))
            result[d] = bool(val)
        return result

    def deleteAttendance(self, date: str) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM attendance WHERE date = ?", (date,))

    # -------------------------
    # Option list management
    # -------------------------

    def create_tables(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS members (
                        id INTEGER PRIMARY KEY,
                        member_id TEXT,
                        name TEXT NOT NULL,
                        contact TEXT,
                        email TEXT,
                        dob TEXT,
                        occupation TEXT,
                        marital_status TEXT,
                        duty TEXT,
                        class TEXT,
                        activity TEXT,
                        photo_path TEXT
                    )
                    """
                )
                cur.execute("CREATE TABLE IF NOT EXISTS attendance (date TEXT PRIMARY KEY)")
                cur.execute("CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
                cur.execute("CREATE TABLE IF NOT EXISTS duties (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
                cur.execute("CREATE TABLE IF NOT EXISTS activity_options (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")

                # defaults
                cur.execute("SELECT COUNT(*) FROM classes")
                if cur.fetchone()[0] == 0:
                    cur.executemany("INSERT INTO classes (name) VALUES (?)", [(n,) for n in ("Davidus", "Naphtali", "Andrew", "John")])
                cur.execute("SELECT COUNT(*) FROM activity_options")
                if cur.fetchone()[0] == 0:
                    cur.executemany("INSERT INTO activity_options (name) VALUES (?)", [(n,) for n in ("Active", "Visitor", "Inactive")])

    def get_options(self, table_name: str) -> List[str]:
        if table_name not in ("classes", "duties", "activity_options"):
            raise ValueError("Invalid options table")
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(f"SELECT name FROM {table_name} ORDER BY name")
                return [r[0] for r in cur.fetchall()]

    def add_option(self, table_name: str, name: str) -> None:
        if table_name not in ("classes", "duties", "activity_options"):
            raise ValueError("Invalid options table")
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(f"INSERT OR IGNORE INTO {table_name} (name) VALUES (?)", (name,))

    def remove_option(self, table_name: str, name: str) -> None:
        if table_name not in ("classes", "duties", "activity_options"):
            raise ValueError("Invalid options table")
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(f"DELETE FROM {table_name} WHERE name = ?", (name,))
                cur.execute(f"SELECT name FROM {table_name} ORDER BY name LIMIT 1")
                row = cur.fetchone()
                fallback = row[0] if row else ""
                if table_name == 'classes':
                    cur.execute("UPDATE members SET class = ? WHERE class = ?", (fallback, name))
                elif table_name == 'duties':
                    cur.execute("UPDATE members SET duty = ? WHERE duty = ?", (fallback, name))
                elif table_name == 'activity_options':
                    cur.execute("UPDATE members SET activity = ? WHERE activity = ?", (fallback, name))

    # convenience factory
    @staticmethod
    def get_instance() -> 'Database':
        return Database()


__all__ = ["Database"]
