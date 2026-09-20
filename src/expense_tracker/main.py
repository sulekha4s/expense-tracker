"""
Main CLI application for the Expense Tracker.
"""

import sys
from typing import Optional
import logging

from .models import Expense, VALID_CATEGORIES
from .database import ExpenseDatabase
from .analysis import ExpenseAnalyzer
from .visualization import ExpenseVisualizer
from .etl import BankStatementETL
from .utils import setup_logging, get_user_input, format_currency, parse_date_input

# Setup logging
logger = setup_logging(level=logging.INFO)


class ExpenseTrackerCLI:
    """Command-line interface for the expense tracker."""

    def __init__(self, db_path: str = "expenses.db"):
        """
        Initialize the CLI application.

        Args:
            db_path: Path to SQLite database
        """
        self.db = ExpenseDatabase(db_path)
        logger.info("Expense Tracker initialized")

    def display_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("            EXPENSE TRACKER MENU")
        print("=" * 50)
        print("1.  Add Expense")
        print("2.  View All Expenses")
        print("3.  View Total Spending")
        print("4.  View Expenses by Category")
        print("5.  Delete an Expense")
        print("6.  View Analytics Dashboard")
        print("7.  View Spending by Category (Detailed)")
        print("8.  View Monthly Trend")
        print("9.  Generate Charts")
        print("10. Export to CSV")
        print("11. Load Sample Data (ETL Demo)")
        print("12. Exit")
        print("=" * 50)

    def add_expense(self):
        """Add a new expense with validation."""
        print("\n" + "-" * 50)
        print("ADD NEW EXPENSE")
        print("-" * 50)

        try:
            date_input = input("Enter date (YYYY-MM-DD or DD/MM/YYYY or 'today'): ").strip()
            date = parse_date_input(date_input)

            print(f"\nAvailable categories: {', '.join(sorted(VALID_CATEGORIES))}")
            category = input("Enter category: ").strip()

            description = input("Enter description: ").strip()

            while True:
                try:
                    amount_input = input("Enter amount (₹): ")
                    amount = float(amount_input)
                    if amount <= 0:
                        print("Amount must be positive. Please try again.")
                        continue
                    break
                except ValueError:
                    print("Invalid amount. Please enter a number.")

            expense = Expense(
                date=date,
                category=category,
                description=description,
                amount=amount
            )

            expense_id = self.db.add_expense(expense)
            print(f"\n✓ Expense added successfully! (ID: {expense_id})")

        except ValueError as e:
            print(f"\n✗ Error: {e}")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
        except Exception as e:
            logger.error(f"Unexpected error adding expense: {e}")
            print(f"\n✗ An unexpected error occurred: {e}")

    def view_all_expenses(self):
        """Display all expenses in a formatted table."""
        print("\n" + "-" * 50)
        print("ALL EXPENSES")
        print("-" * 50)

        try:
            expenses = self.db.get_all_expenses()

            if not expenses:
                print("\nNo expenses recorded yet.")
                return

            print(f"\n{'ID':<6} {'Date':<12} {'Category':<15} {'Description':<25} {'Amount':>12}")
            print("-" * 80)

            for expense in expenses:
                desc_truncated = expense.description[:22] + "..." if len(expense.description) > 25 else expense.description
                print(f"{expense.id:<6} {expense.date:<12} {expense.category:<15} "
                      f"{desc_truncated:<25} {format_currency(expense.amount):>12}")

            print("-" * 80)
            print(f"Total expenses: {len(expenses)}")

        except Exception as e:
            logger.error(f"Error viewing expenses: {e}")
            print(f"\n✗ Error retrieving expenses: {e}")

    def view_total_spending(self):
        """Display total spending with summary."""
        print("\n" + "-" * 50)
        print("SPENDING SUMMARY")
        print("-" * 50)

        try:
            expenses = self.db.get_all_expenses()

            if not expenses:
                print("\nNo expenses to analyze.")
                return

            analyzer = ExpenseAnalyzer(expenses)
            stats = analyzer.get_summary_statistics()

            print(f"\nTotal Expenses: {stats['total_expenses']}")
            print(f"Total Spending: {format_currency(stats['total_spending'])}")
            print(f"\nAverage Expense: {format_currency(stats['average_expense'])}")
            print(f"Median Expense: {format_currency(stats['median_expense'])}")
            print(f"\nSmallest Expense: {format_currency(stats['min_expense'])}")
            print(f"Largest Expense: {format_currency(stats['max_expense'])}")

        except Exception as e:
            logger.error(f"Error calculating total spending: {e}")
            print(f"\n✗ Error: {e}")

    def view_expenses_by_category(self):
        """View expenses filtered by category."""
        print("\n" + "-" * 50)
        print("VIEW EXPENSES BY CATEGORY")
        print("-" * 50)

        try:
            print(f"\nAvailable categories: {', '.join(sorted(VALID_CATEGORIES))}")
            category = input("Enter category to view: ").strip()

            expenses = self.db.get_expenses_by_category(category)

            if not expenses:
                print(f"\nNo expenses found in category '{category}'.")
                return

            print(f"\n{category.upper()} EXPENSES")
            print("-" * 70)
            print(f"{'Date':<12} {'Description':<35} {'Amount':>12}")
            print("-" * 70)

            total = 0
            for expense in expenses:
                desc_truncated = expense.description[:32] + "..." if len(expense.description) > 35 else expense.description
                print(f"{expense.date:<12} {desc_truncated:<35} {format_currency(expense.amount):>12}")
                total += expense.amount

            print("-" * 70)
            print(f"{'Total:':>47} {format_currency(total):>12}")
            print(f"Number of expenses: {len(expenses)}")

        except Exception as e:
            logger.error(f"Error viewing category expenses: {e}")
            print(f"\n✗ Error: {e}")

    def delete_expense(self):
        """Delete an expense by ID."""
        print("\n" + "-" * 50)
        print("DELETE EXPENSE")
        print("-" * 50)

        try:
            expenses = self.db.get_all_expenses()

            if not expenses:
                print("\nNo expenses available to delete.")
                return

            print(f"\n{'ID':<6} {'Date':<12} {'Category':<15} {'Description':<30} {'Amount':>10}")
            print("-" * 80)
            for expense in expenses:
                desc_truncated = expense.description[:27] + "..." if len(expense.description) > 30 else expense.description
                print(f"{expense.id:<6} {expense.date:<12} {expense.category:<15} "
                      f"{desc_truncated:<30} {format_currency(expense.amount):>10}")

            expense_id = get_user_input(
                "\nEnter expense ID to delete (0 to cancel): ",
                input_type=int,
                error_message="Invalid ID"
            )

            if expense_id == 0:
                print("Deletion cancelled.")
                return

            expense = self.db.get_expense_by_id(expense_id)
            if not expense:
                print(f"\n✗ Expense with ID {expense_id} not found.")
                return

            confirm = input(f"\nAre you sure you want to delete '{expense.description}'? (yes/no): ").strip().lower()

            if confirm in ['yes', 'y']:
                if self.db.delete_expense(expense_id):
                    print(f"\n✓ Expense '{expense.description}' deleted successfully!")
                else:
                    print(f"\n✗ Failed to delete expense.")
            else:
                print("Deletion cancelled.")

        except Exception as e:
            logger.error(f"Error deleting expense: {e}")
            print(f"\n✗ Error: {e}")

    def view_analytics_dashboard(self):
        """Display analytics dashboard in text format."""
        print("\n" + "=" * 50)
        print("ANALYTICS DASHBOARD")
        print("=" * 50)

        try:
            expenses = self.db.get_all_expenses()

            if not expenses:
                print("\nNo expenses to analyze.")
                return

            analyzer = ExpenseAnalyzer(expenses)

            # Overall statistics
            stats = analyzer.get_summary_statistics()
            print("\n📊 OVERALL STATISTICS")
            print("-" * 50)
            print(f"Total Expenses: {stats['total_expenses']}")
            print(f"Total Spending: {format_currency(stats['total_spending'])}")
            print(f"Average Expense: {format_currency(stats['average_expense'])}")

            # Spending by category
            print("\n💰 SPENDING BY CATEGORY")
            print("-" * 50)
            category_spending = analyzer.get_spending_by_category()
            for category, amount in category_spending.items():
                percentage = (amount / stats['total_spending']) * 100
                print(f"{category:<15} {format_currency(amount):>12} ({percentage:>5.1f}%)")

            # Monthly trend
            print("\n📈 MONTHLY TREND")
            print("-" * 50)
            monthly = analyzer.get_monthly_trend()
            for month, row in monthly.iterrows():
                print(f"{month:<10} {format_currency(row['total_spending']):>12} "
                      f"({int(row['num_expenses'])} expenses)")

            # Top expenses
            print("\n🔝 TOP 5 EXPENSES")
            print("-" * 50)
            top_expenses = analyzer.get_top_expenses(n=5)
            for _, expense in top_expenses.iterrows():
                print(f"{expense['date']} | {expense['category']:<12} | "
                      f"{expense['description'][:30]:<30} | {format_currency(expense['amount']):>12}")

        except Exception as e:
            logger.error(f"Error displaying analytics: {e}")
            print(f"\n✗ Error: {e}")

    def view_category_analysis(self):
        """Display detailed category analysis."""
        print("\n" + "-" * 50)
        print("CATEGORY ANALYSIS")
        print("-" * 50)

        try:
            expenses = self.db.get_all_expenses()

            if not expenses:
                print("\nNo expenses to analyze.")
                return

            analyzer = ExpenseAnalyzer(expenses)
            category_stats = analyzer.get_category_statistics()

            print(f"\n{'Category':<15} {'Count':>8} {'Total':>12} {'Average':>12} {'Min':>10} {'Max':>10}")
            print("-" * 80)

            for category, row in category_stats.iterrows():
                print(f"{category:<15} {int(row['count']):>8} "
                      f"{format_currency(row['total']):>12} "
                      f"{format_currency(row['average']):>12} "
                      f"{format_currency(row['min']):>10} "
                      f"{format_currency(row['max']):>10}")

        except Exception as e:
            logger.error(f"Error displaying category analysis: {e}")
            print(f"\n✗ Error: {e}")

    def view_monthly_trend(self):
        """Display monthly spending trend."""
        print("\n" + "-" * 50)
        print("MONTHLY SPENDING TREND")
        print("-" * 50)

        try:
            expenses = self.db.get_all_expenses()

            if not expenses:
                print("\nNo expenses to analyze.")
                return

            analyzer = ExpenseAnalyzer(expenses)
            monthly = analyzer.get_monthly_trend()

            print(f"\n{'Month':<12} {'Total Spending':>15} {'# Expenses':>12} {'Avg Expense':>15}")
            print("-" * 60)

            for month, row in monthly.iterrows():
                print(f"{month:<12} {format_currency(row['total_spending']):>15} "
                      f"{int(row['num_expenses']):>12} {format_currency(row['avg_expense']):>15}")

        except Exception as e:
            logger.error(f"Error displaying monthly trend: {e}")
            print(f"\n✗ Error: {e}")

    def generate_charts(self):
        """Generate all visualization charts."""
        print("\n" + "-" * 50)
        print("GENERATE CHARTS")
        print("-" * 50)

        try:
            expenses = self.db.get_all_expenses()

            if not expenses:
                print("\nNo expenses to visualize. Add some expenses first!")
                return

            analyzer = ExpenseAnalyzer(expenses)
            visualizer = ExpenseVisualizer(analyzer)

            print("\nGenerating charts...")
            visualizer.generate_all_charts()

            print("\n✓ All charts generated successfully!")
            print(f"  Charts saved to: {visualizer.output_dir}/")
            print("\nGenerated files:")
            print("  - spending_by_category.png")
            print("  - monthly_trend.png")
            print("  - category_bar_chart.png")
            print("  - expense_distribution.png")
            print("  - dashboard.png")

        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            print(f"\n✗ Error generating charts: {e}")

    def export_to_csv(self):
        """Export expenses to CSV file."""
        print("\n" + "-" * 50)
        print("EXPORT TO CSV")
        print("-" * 50)

        try:
            expenses = self.db.get_all_expenses()

            if not expenses:
                print("\nNo expenses to export.")
                return

            filename = input("\nEnter filename (default: expenses_export.csv): ").strip()
            if not filename:
                filename = "expenses_export.csv"

            if not filename.endswith('.csv'):
                filename += '.csv'

            analyzer = ExpenseAnalyzer(expenses)
            analyzer.export_to_csv(filename)

            print(f"\n✓ Expenses exported successfully to {filename}")
            print(f"  Total records: {len(expenses)}")

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            print(f"\n✗ Error: {e}")

    def load_sample_data(self):
        """Load sample bank statement data using ETL pipeline."""
        print("\n" + "-" * 50)
        print("LOAD SAMPLE DATA (ETL DEMO)")
        print("-" * 50)

        sample_file = "data/sample_bank_statement.csv"

        print("\nThis will import 20 sample bank transactions from:")
        print(f"  {sample_file}")
        print("\nSample data includes:")
        print("  • 20 expenses from Jan-Feb 2024")
        print("  • 7 categories: Food, Travel, Books, Shopping,")
        print("    Entertainment, Healthcare, Utilities")
        print("  • Demonstrates ETL pipeline (Extract-Transform-Load)")

        confirm = input("\nDo you want to proceed? (yes/no): ").strip().lower()

        if confirm not in ['yes', 'y']:
            print("\n✗ Import cancelled.")
            return

        try:
            print("\n⏳ Running ETL pipeline...")
            print("  [1/3] Extracting data from CSV...")

            etl = BankStatementETL(self.db)

            print("  [2/3] Transforming and validating...")
            print("  [3/3] Loading into database...")

            stats = etl.run_pipeline(sample_file)

            print("\n" + "=" * 50)
            print("✓ ETL PIPELINE COMPLETED")
            print("=" * 50)
            print(f"\nImport Statistics:")
            print(f"  Total rows processed: {stats['total_rows']}")
            print(f"  Successfully imported: {stats['imported']}")
            print(f"  Skipped (credits):    {stats['skipped']}")
            print(f"  Errors:               {stats['errors']}")

            if stats['imported'] > 0:
                print(f"\n✓ {stats['imported']} expenses added to database!")
                print("\nYou can now:")
                print("  • View them in option 2 (View All Expenses)")
                print("  • Analyze them in option 6 (Analytics Dashboard)")
                print("  • Generate charts in option 9 (Generate Charts)")

        except FileNotFoundError:
            print(f"\n✗ Error: Sample file not found at {sample_file}")
            print("  Make sure you're running from the project root directory.")
        except Exception as e:
            logger.error(f"Error loading sample data: {e}")
            print(f"\n✗ Error loading sample data: {e}")

    def run(self):
        """Main application loop."""
        print("\n" + "=" * 50)
        print("     WELCOME TO EXPENSE TRACKER")
        print("=" * 50)

        while True:
            try:
                self.display_menu()

                choice = get_user_input(
                    "\nEnter your choice (1-12): ",
                    input_type=int,
                    error_message="Invalid choice. Please enter a number between 1 and 12"
                )

                if choice == 1:
                    self.add_expense()
                elif choice == 2:
                    self.view_all_expenses()
                elif choice == 3:
                    self.view_total_spending()
                elif choice == 4:
                    self.view_expenses_by_category()
                elif choice == 5:
                    self.delete_expense()
                elif choice == 6:
                    self.view_analytics_dashboard()
                elif choice == 7:
                    self.view_category_analysis()
                elif choice == 8:
                    self.view_monthly_trend()
                elif choice == 9:
                    self.generate_charts()
                elif choice == 10:
                    self.export_to_csv()
                elif choice == 11:
                    self.load_sample_data()
                elif choice == 12:
                    print("\n" + "=" * 50)
                    print("Thank you for using Expense Tracker!")
                    print("=" * 50)
                    break
                else:
                    print("\n✗ Invalid choice. Please select 1-12.")

            except KeyboardInterrupt:
                print("\n\n" + "=" * 50)
                print("Application terminated by user.")
                print("=" * 50)
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                print(f"\n✗ An unexpected error occurred: {e}")

        # Cleanup
        self.db.close()
        logger.info("Application closed")


def main():
    """Entry point for the application."""
    try:
        app = ExpenseTrackerCLI()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
