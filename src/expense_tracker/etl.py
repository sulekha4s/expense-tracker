"""
ETL (Extract, Transform, Load) module for importing bank statements.
"""

import csv
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from .models import Expense
from .database import ExpenseDatabase

logger = logging.getLogger("expense_tracker")


class BankStatementETL:
    """ETL pipeline for importing bank statement CSV files."""

    def __init__(self, db: ExpenseDatabase):
        """
        Initialize ETL pipeline.

        Args:
            db: ExpenseDatabase instance
        """
        self.db = db
        self.stats = {
            "total_rows": 0,
            "imported": 0,
            "skipped": 0,
            "errors": 0
        }

    def extract(self, filepath: str) -> List[Dict]:
        """
        Extract data from CSV file.

        Args:
            filepath: Path to CSV file

        Returns:
            List of dictionaries representing rows
        """
        logger.info(f"Extracting data from {filepath}")

        rows = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
                self.stats["total_rows"] += 1

        logger.info(f"Extracted {len(rows)} rows")
        return rows

    def transform(self, rows: List[Dict]) -> List[Expense]:
        """
        Transform bank statement rows into Expense objects.

        Expected CSV format:
        - Transaction Date: Date of transaction (DD/MM/YYYY or YYYY-MM-DD)
        - Description: Transaction description
        - Category: Expense category
        - Debit: Amount debited (expenses)
        - Credit: Amount credited (skip these)

        Args:
            rows: List of dictionaries from CSV

        Returns:
            List of valid Expense objects
        """
        logger.info("Transforming data...")

        expenses = []

        for row in rows:
            try:
                # Skip if it's a credit (income, not expense)
                debit = row.get('Debit', '').strip()
                credit = row.get('Credit', '').strip()

                if not debit or debit == '':
                    logger.debug(f"Skipping credit transaction: {row.get('Description')}")
                    self.stats["skipped"] += 1
                    continue

                # Parse amount
                amount = float(debit.replace(',', ''))

                # Parse date - support multiple formats
                date_str = row.get('Transaction Date', '').strip()
                date = self._parse_date(date_str)

                category = row.get('Category', '').strip()
                description = row.get('Description', '').strip()

                expense = Expense(
                    date=date,
                    category=category,
                    description=description,
                    amount=amount
                )

                expenses.append(expense)
                logger.debug(f"Transformed: {description} - ₹{amount}")

            except ValueError as e:
                logger.warning(f"Validation error for row {row}: {e}")
                self.stats["errors"] += 1
            except Exception as e:
                logger.error(f"Error transforming row {row}: {e}")
                self.stats["errors"] += 1

        logger.info(f"Transformed {len(expenses)} valid expenses")
        return expenses

    def load(self, expenses: List[Expense]) -> int:
        """
        Load expenses into database.

        Args:
            expenses: List of Expense objects

        Returns:
            Number of expenses loaded
        """
        logger.info(f"Loading {len(expenses)} expenses into database...")

        loaded = 0
        for expense in expenses:
            try:
                self.db.add_expense(expense)
                loaded += 1
                self.stats["imported"] += 1
            except Exception as e:
                logger.error(f"Error loading expense {expense}: {e}")
                self.stats["errors"] += 1

        logger.info(f"Loaded {loaded} expenses")
        return loaded

    def run_pipeline(self, filepath: str) -> Dict:
        """
        Run the full ETL pipeline.

        Args:
            filepath: Path to CSV file

        Returns:
            Dictionary with statistics
        """
        logger.info(f"Starting ETL pipeline for {filepath}")

        # Reset stats
        self.stats = {
            "total_rows": 0,
            "imported": 0,
            "skipped": 0,
            "errors": 0
        }

        try:
            # Extract
            rows = self.extract(filepath)

            # Transform
            expenses = self.transform(rows)

            # Load
            loaded = self.load(expenses)

            logger.info(
                f"ETL pipeline completed. "
                f"Total: {self.stats['total_rows']}, "
                f"Imported: {self.stats['imported']}, "
                f"Skipped: {self.stats['skipped']}, "
                f"Errors: {self.stats['errors']}"
            )

            return self.stats

        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            raise

    def _parse_date(self, date_str: str) -> str:
        """
        Parse date from various formats to YYYY-MM-DD.

        Args:
            date_str: Date string in various formats

        Returns:
            Date in YYYY-MM-DD format
        """
        formats = [
            "%Y-%m-%d",      # YYYY-MM-DD
            "%d/%m/%Y",      # DD/MM/YYYY
            "%d-%m-%Y",      # DD-MM-YYYY
            "%m/%d/%Y",      # MM/DD/YYYY
            "%Y/%m/%d",      # YYYY/MM/DD
        ]

        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue

        raise ValueError(f"Unable to parse date: {date_str}")


def import_bank_statement(csv_file: str, db_path: str = "expenses.db") -> Dict:
    """
    Convenience function to import a bank statement CSV.

    Args:
        csv_file: Path to CSV file
        db_path: Path to database

    Returns:
        Dictionary with import statistics
    """
    db = ExpenseDatabase(db_path)
    etl = BankStatementETL(db)

    try:
        stats = etl.run_pipeline(csv_file)
        return stats
    finally:
        db.close()
