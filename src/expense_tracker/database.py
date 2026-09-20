"""
Database operations for expense tracking using SQLite.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional
import logging

from .models import Expense

logger = logging.getLogger("expense_tracker")


class ExpenseDatabase:
    """Handles all database operations for expense tracking."""

    def __init__(self, db_path: str = "expenses.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def init_db(self):
        """Initialize database connection and create tables if they don't exist."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            self._create_tables()
            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def _create_tables(self):
        """Create expenses table if it doesn't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_date ON expenses(date);
        CREATE INDEX IF NOT EXISTS idx_category ON expenses(category);
        """

        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_sql)
            cursor.executescript(create_index_sql)
            self.conn.commit()
            logger.debug("Tables and indexes created successfully")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def add_expense(self, expense: Expense) -> int:
        """
        Add a new expense to the database.

        Args:
            expense: Expense object to add

        Returns:
            ID of the newly created expense
        """
        insert_sql = """
        INSERT INTO expenses (date, category, description, amount)
        VALUES (?, ?, ?, ?)
        """

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                insert_sql,
                (expense.date, expense.category, expense.description, expense.amount)
            )
            self.conn.commit()
            expense_id = cursor.lastrowid
            logger.info(f"Added expense: {expense.description} (ID: {expense_id})")
            return expense_id
        except sqlite3.Error as e:
            logger.error(f"Error adding expense: {e}")
            raise

    def get_all_expenses(self) -> List[Expense]:
        """
        Retrieve all expenses from the database.

        Returns:
            List of Expense objects
        """
        select_sql = "SELECT id, date, category, description, amount FROM expenses ORDER BY date DESC, id DESC"

        try:
            cursor = self.conn.cursor()
            cursor.execute(select_sql)
            rows = cursor.fetchall()

            expenses = []
            for row in rows:
                expense = Expense(
                    id=row['id'],
                    date=row['date'],
                    category=row['category'],
                    description=row['description'],
                    amount=row['amount']
                )
                expenses.append(expense)

            logger.debug(f"Retrieved {len(expenses)} expenses")
            return expenses
        except sqlite3.Error as e:
            logger.error(f"Error retrieving expenses: {e}")
            raise

    def get_expense_by_id(self, expense_id: int) -> Optional[Expense]:
        """
        Get a specific expense by ID.

        Args:
            expense_id: ID of the expense

        Returns:
            Expense object or None if not found
        """
        select_sql = "SELECT id, date, category, description, amount FROM expenses WHERE id = ?"

        try:
            cursor = self.conn.cursor()
            cursor.execute(select_sql, (expense_id,))
            row = cursor.fetchone()

            if row:
                return Expense(
                    id=row['id'],
                    date=row['date'],
                    category=row['category'],
                    description=row['description'],
                    amount=row['amount']
                )
            return None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving expense {expense_id}: {e}")
            raise

    def get_expenses_by_category(self, category: str) -> List[Expense]:
        """
        Get all expenses for a specific category.

        Args:
            category: Category to filter by

        Returns:
            List of Expense objects
        """
        select_sql = """
        SELECT id, date, category, description, amount
        FROM expenses
        WHERE category = ?
        ORDER BY date DESC
        """

        try:
            cursor = self.conn.cursor()
            cursor.execute(select_sql, (category,))
            rows = cursor.fetchall()

            expenses = []
            for row in rows:
                expense = Expense(
                    id=row['id'],
                    date=row['date'],
                    category=row['category'],
                    description=row['description'],
                    amount=row['amount']
                )
                expenses.append(expense)

            return expenses
        except sqlite3.Error as e:
            logger.error(f"Error retrieving expenses for category {category}: {e}")
            raise

    def delete_expense(self, expense_id: int) -> bool:
        """
        Delete an expense by ID.

        Args:
            expense_id: ID of expense to delete

        Returns:
            True if deleted, False if not found
        """
        delete_sql = "DELETE FROM expenses WHERE id = ?"

        try:
            cursor = self.conn.cursor()
            cursor.execute(delete_sql, (expense_id,))
            self.conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"Deleted expense ID: {expense_id}")
                return True
            else:
                logger.warning(f"Expense ID {expense_id} not found")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            raise

    def get_total_spending(self) -> float:
        """
        Calculate total spending across all expenses.

        Returns:
            Total amount spent
        """
        sql = "SELECT SUM(amount) as total FROM expenses"

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            return result['total'] if result['total'] is not None else 0.0
        except sqlite3.Error as e:
            logger.error(f"Error calculating total spending: {e}")
            raise

    def get_spending_by_category(self) -> dict:
        """
        Calculate total spending grouped by category.

        Returns:
            Dictionary mapping category to total amount
        """
        sql = """
        SELECT category, SUM(amount) as total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
        """

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return {row['category']: row['total'] for row in rows}
        except sqlite3.Error as e:
            logger.error(f"Error calculating spending by category: {e}")
            raise

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
