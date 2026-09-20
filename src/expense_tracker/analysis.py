"""
Data analysis module using pandas for expense analytics.
"""

import pandas as pd
from typing import List, Dict, Optional
import logging
from datetime import datetime

from .models import Expense

logger = logging.getLogger("expense_tracker")


class ExpenseAnalyzer:
    """Analyzes expense data using pandas."""

    def __init__(self, expenses: List[Expense]):
        """
        Initialize analyzer with expense data.

        Args:
            expenses: List of Expense objects
        """
        self.expenses = expenses
        self.df = self._create_dataframe()

    def _create_dataframe(self) -> pd.DataFrame:
        """Convert expense list to pandas DataFrame."""
        if not self.expenses:
            return pd.DataFrame(columns=['id', 'date', 'category', 'description', 'amount'])

        data = [expense.to_dict() for expense in self.expenses]
        df = pd.DataFrame(data)

        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Add derived columns
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['year_month'] = df['date'].dt.to_period('M')
        df['day_of_week'] = df['date'].dt.day_name()

        logger.debug(f"Created DataFrame with {len(df)} expenses")
        return df

    def get_total_spending(self) -> float:
        """Calculate total spending."""
        if self.df.empty:
            return 0.0
        return float(self.df['amount'].sum())

    def get_spending_by_category(self) -> pd.Series:
        """
        Get total spending grouped by category.

        Returns:
            Series with category as index and total amount as values
        """
        if self.df.empty:
            return pd.Series(dtype=float)

        return self.df.groupby('category')['amount'].sum().sort_values(ascending=False)

    def get_spending_by_month(self) -> pd.Series:
        """
        Get total spending grouped by month.

        Returns:
            Series with year-month as index and total amount as values
        """
        if self.df.empty:
            return pd.Series(dtype=float)

        monthly = self.df.groupby('year_month')['amount'].sum().sort_index()
        # Convert period index to string for better display
        monthly.index = monthly.index.astype(str)
        return monthly

    def get_average_expense(self) -> float:
        """Calculate average expense amount."""
        if self.df.empty:
            return 0.0
        return float(self.df['amount'].mean())

    def get_category_statistics(self) -> pd.DataFrame:
        """
        Get detailed statistics for each category.

        Returns:
            DataFrame with statistics (count, total, mean, min, max) by category
        """
        if self.df.empty:
            return pd.DataFrame()

        stats = self.df.groupby('category')['amount'].agg([
            ('count', 'count'),
            ('total', 'sum'),
            ('average', 'mean'),
            ('min', 'min'),
            ('max', 'max')
        ]).round(2)

        return stats.sort_values('total', ascending=False)

    def get_monthly_trend(self) -> pd.DataFrame:
        """
        Get monthly spending trend with statistics.

        Returns:
            DataFrame with monthly totals, counts, and averages
        """
        if self.df.empty:
            return pd.DataFrame()

        monthly = self.df.groupby('year_month').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)

        monthly.columns = ['total_spending', 'num_expenses', 'avg_expense']
        monthly.index = monthly.index.astype(str)

        return monthly

    def get_top_expenses(self, n: int = 10) -> pd.DataFrame:
        """
        Get top N expenses by amount.

        Args:
            n: Number of top expenses to return

        Returns:
            DataFrame with top expenses
        """
        if self.df.empty:
            return pd.DataFrame()

        return self.df.nlargest(n, 'amount')[['date', 'category', 'description', 'amount']]

    def get_spending_by_day_of_week(self) -> pd.Series:
        """
        Get average spending by day of week.

        Returns:
            Series with day of week and average amount
        """
        if self.df.empty:
            return pd.Series(dtype=float)

        # Define day order
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        spending = self.df.groupby('day_of_week')['amount'].mean()
        # Reindex to ensure proper day ordering
        spending = spending.reindex(day_order, fill_value=0)

        return spending

    def filter_by_date_range(self, start_date: str, end_date: str) -> 'ExpenseAnalyzer':
        """
        Filter expenses by date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            New ExpenseAnalyzer instance with filtered data
        """
        if self.df.empty:
            return ExpenseAnalyzer([])

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        filtered_df = self.df[(self.df['date'] >= start) & (self.df['date'] <= end)]

        # Convert back to Expense objects
        filtered_expenses = []
        for _, row in filtered_df.iterrows():
            expense = Expense(
                id=int(row['id']) if pd.notna(row['id']) else None,
                date=row['date'].strftime('%Y-%m-%d'),
                category=row['category'],
                description=row['description'],
                amount=float(row['amount'])
            )
            filtered_expenses.append(expense)

        return ExpenseAnalyzer(filtered_expenses)

    def get_summary_statistics(self) -> Dict[str, float]:
        """
        Get overall summary statistics.

        Returns:
            Dictionary with key statistics
        """
        if self.df.empty:
            return {
                'total_expenses': 0,
                'total_spending': 0.0,
                'average_expense': 0.0,
                'median_expense': 0.0,
                'min_expense': 0.0,
                'max_expense': 0.0
            }

        return {
            'total_expenses': len(self.df),
            'total_spending': float(self.df['amount'].sum()),
            'average_expense': float(self.df['amount'].mean()),
            'median_expense': float(self.df['amount'].median()),
            'min_expense': float(self.df['amount'].min()),
            'max_expense': float(self.df['amount'].max())
        }

    def export_to_csv(self, filepath: str):
        """
        Export expenses to CSV file.

        Args:
            filepath: Path to output CSV file
        """
        if self.df.empty:
            logger.warning("No data to export")
            return

        export_df = self.df[['id', 'date', 'category', 'description', 'amount']].copy()
        export_df['date'] = export_df['date'].dt.strftime('%Y-%m-%d')
        export_df.to_csv(filepath, index=False)
        logger.info(f"Exported {len(export_df)} expenses to {filepath}")
