import sqlite3
from contextlib import closing
import os
import sys
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.financial import Financial


class FinancialDatabase:
    """Separate SQLite database for financial/thanksgiving offerings records.
    
    This database is independent from the main Records.db and stores all
    financial transaction data with member references.
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
            self.db_path = os.path.join(data_dir, "Financial.db")

        self.create_tables()

    # -----------------
    # Financial operations
    # -----------------

    def add_financial_record(self, financial: Financial) -> int:
        """Add a new financial record. Returns the ID of the inserted record."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO financial_records (member_id, member_name, value, date, notes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        financial.member_id,
                        financial.member_name,
                        financial.value,
                        financial.date,
                        financial.notes,
                    ),
                )
                return cur.lastrowid

    def get_financial_record(self, record_id: int) -> Optional[Financial]:
        """Retrieve a financial record by ID."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM financial_records WHERE id = ?", (record_id,))
                row = cur.fetchone()
                if not row:
                    return None

                f = Financial()
                f.id = row[0]
                f.member_id = row[1]
                f.member_name = row[2]
                f.value = row[3]
                f.date = row[4]
                f.notes = row[5]
                return f

    def get_all_financial_records(self) -> List[Financial]:
        """Retrieve all financial records."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM financial_records ORDER BY date DESC")
                rows = cur.fetchall()
                records = []
                for row in rows:
                    f = Financial()
                    f.id = row[0]
                    f.member_id = row[1]
                    f.member_name = row[2]
                    f.value = row[3]
                    f.date = row[4]
                    f.notes = row[5]
                    records.append(f)
                return records

    def get_financial_records_for_member(self, member_id: str) -> List[Financial]:
        """Get all financial records for a specific member."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT * FROM financial_records WHERE member_id = ? ORDER BY date DESC",
                    (str(member_id),)
                )
                rows = cur.fetchall()
                records = []
                for row in rows:
                    f = Financial()
                    f.id = row[0]
                    f.member_id = row[1]
                    f.member_name = row[2]
                    f.value = row[3]
                    f.date = row[4]
                    f.notes = row[5]
                    records.append(f)
                return records

    def get_financial_records_by_date_range(self, start_date: str, end_date: str) -> List[Financial]:
        """Get financial records within a date range (YYYY-MM-DD format)."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT * FROM financial_records WHERE date >= ? AND date <= ? ORDER BY date DESC",
                    (start_date, end_date)
                )
                rows = cur.fetchall()
                records = []
                for row in rows:
                    f = Financial()
                    f.id = row[0]
                    f.member_id = row[1]
                    f.member_name = row[2]
                    f.value = row[3]
                    f.date = row[4]
                    f.notes = row[5]
                    records.append(f)
                return records

    def get_financial_records_last_year(self) -> List[Financial]:
        """Get financial records from the last year."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        return self.get_financial_records_by_date_range(start_date, end_date)

    def update_financial_record(self, financial: Financial) -> None:
        """Update an existing financial record."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE financial_records
                    SET member_id = ?, member_name = ?, value = ?, date = ?, notes = ?
                    WHERE id = ?
                    """,
                    (
                        financial.member_id,
                        financial.member_name,
                        financial.value,
                        financial.date,
                        financial.notes,
                        financial.id,
                    ),
                )

    def delete_financial_record(self, record_id: int) -> None:
        """Delete a financial record."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM financial_records WHERE id = ?", (record_id,))

    def get_total_by_member(self, member_id: str) -> float:
        """Get total offerings for a specific member."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT SUM(value) FROM financial_records WHERE member_id = ?",
                    (str(member_id),)
                )
                result = cur.fetchone()
                return result[0] if result[0] is not None else 0.0

    def get_total_all(self) -> float:
        """Get total offerings across all members."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT SUM(value) FROM financial_records")
                result = cur.fetchone()
                return result[0] if result[0] is not None else 0.0

    def create_tables(self) -> None:
        """Create financial tables if they don't exist."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS financial_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        member_id TEXT,
                        member_name TEXT NOT NULL,
                        value REAL NOT NULL,
                        date TEXT NOT NULL,
                        notes TEXT
                    )
                    """
                )

    @staticmethod
    def get_instance() -> 'FinancialDatabase':
        """Get a singleton instance of the database."""
        return FinancialDatabase()


__all__ = ["FinancialDatabase"]
