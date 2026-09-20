"""
Data visualization module using matplotlib for expense charts.
"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from typing import Optional
import logging

from .analysis import ExpenseAnalyzer

logger = logging.getLogger("expense_tracker")


def format_currency_axis(value, position):
    """
    Format axis values as currency.

    Args:
        value: The numeric value to format
        position: The tick position (required by matplotlib formatter)

    Returns:
        Formatted string with currency symbol
    """
    return f'₹{value:,.0f}'


class ExpenseVisualizer:
    """Creates visualizations for expense data."""

    def __init__(self, analyzer: ExpenseAnalyzer, output_dir: str = "charts"):
        """
        Initialize visualizer.

        Args:
            analyzer: ExpenseAnalyzer instance with loaded data
            output_dir: Directory to save chart images
        """
        self.analyzer = analyzer
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Set style for better-looking charts
        plt.style.use('seaborn-v0_8-darkgrid')

    def plot_spending_by_category(self, save: bool = True, show: bool = False) -> Optional[str]:
        """
        Create a pie chart of spending by category.

        Args:
            save: Whether to save the chart to file
            show: Whether to display the chart

        Returns:
            Path to saved file if save=True, else None
        """
        spending = self.analyzer.get_spending_by_category()

        if spending.empty:
            logger.warning("No data to visualize")
            return None

        fig, ax = plt.subplots(figsize=(10, 8))


        colors = plt.cm.Set3.colors
        wedges, texts, autotexts = ax.pie(
            spending.values,
            labels=spending.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )

        # Enhance text
        for text in texts:
            text.set_fontsize(12)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        ax.set_title('Spending by Category', fontsize=16, fontweight='bold', pad=20)

        # Add legend with amounts
        legend_labels = [f"{cat}: ₹{amt:,.2f}" for cat, amt in spending.items()]
        ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))

        plt.tight_layout()

        output_path = None
        if save:
            output_path = self.output_dir / "spending_by_category.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved category chart to {output_path}")

        if show:
            plt.show()
        else:
            plt.close()

        return str(output_path) if output_path else None

    def plot_monthly_trend(self, save: bool = True, show: bool = False) -> Optional[str]:
        """
        Create a line chart of monthly spending trend.

        Args:
            save: Whether to save the chart to file
            show: Whether to display the chart

        Returns:
            Path to saved file if save=True, else None
        """
        monthly = self.analyzer.get_spending_by_month()

        if monthly.empty:
            logger.warning("No data to visualize")
            return None

        fig, ax = plt.subplots(figsize=(12, 6))


        ax.plot(monthly.index, monthly.values, marker='o', linewidth=2, markersize=8, color='#2E86AB')

        # Fill area under the line
        ax.fill_between(monthly.index, monthly.values, alpha=0.3, color='#2E86AB')

        # Customize chart
        ax.set_title('Monthly Spending Trend', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount (₹)', fontsize=12, fontweight='bold')

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')

        # Add grid
        ax.grid(True, alpha=0.3)


        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_currency_axis))

        plt.tight_layout()

        output_path = None
        if save:
            output_path = self.output_dir / "monthly_trend.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved monthly trend chart to {output_path}")

        if show:
            plt.show()
        else:
            plt.close()

        return str(output_path) if output_path else None

    def plot_category_bar_chart(self, save: bool = True, show: bool = False) -> Optional[str]:
        """
        Create a horizontal bar chart of spending by category.

        Args:
            save: Whether to save the chart to file
            show: Whether to display the chart

        Returns:
            Path to saved file if save=True, else None
        """
        spending = self.analyzer.get_spending_by_category()

        if spending.empty:
            logger.warning("No data to visualize")
            return None

        fig, ax = plt.subplots(figsize=(10, 6))


        colors = plt.cm.Spectral(range(len(spending)))
        bars = ax.barh(spending.index, spending.values, color=colors)

        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'₹{width:,.2f}',
                   ha='left', va='center', fontweight='bold', fontsize=10)

        # Customize chart
        ax.set_title('Spending by Category', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Amount (₹)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Category', fontsize=12, fontweight='bold')


        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_currency_axis))

        plt.tight_layout()

        output_path = None
        if save:
            output_path = self.output_dir / "category_bar_chart.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved category bar chart to {output_path}")

        if show:
            plt.show()
        else:
            plt.close()

        return str(output_path) if output_path else None

    def plot_expense_distribution(self, save: bool = True, show: bool = False) -> Optional[str]:
        """
        Create a histogram showing distribution of expense amounts.

        Args:
            save: Whether to save the chart to file
            show: Whether to display the chart

        Returns:
            Path to saved file if save=True, else None
        """
        if self.analyzer.df.empty:
            logger.warning("No data to visualize")
            return None

        fig, ax = plt.subplots(figsize=(10, 6))


        ax.hist(self.analyzer.df['amount'], bins=20, color='#A23B72', edgecolor='black', alpha=0.7)

        # Add mean and median lines
        mean_val = self.analyzer.df['amount'].mean()
        median_val = self.analyzer.df['amount'].median()

        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: ₹{mean_val:,.2f}')
        ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: ₹{median_val:,.2f}')

        # Customize chart
        ax.set_title('Distribution of Expense Amounts', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Amount (₹)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')


        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_currency_axis))

        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        output_path = None
        if save:
            output_path = self.output_dir / "expense_distribution.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved distribution chart to {output_path}")

        if show:
            plt.show()
        else:
            plt.close()

        return str(output_path) if output_path else None

    def create_dashboard(self, save: bool = True, show: bool = False) -> Optional[str]:
        """
        Create a comprehensive dashboard with multiple visualizations.

        Args:
            save: Whether to save the dashboard to file
            show: Whether to display the dashboard

        Returns:
            Path to saved file if save=True, else None
        """
        if self.analyzer.df.empty:
            logger.warning("No data to visualize")
            return None

        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # 1. Spending by Category (Pie Chart)
        ax1 = fig.add_subplot(gs[0, 0])
        spending = self.analyzer.get_spending_by_category()
        colors = plt.cm.Set3.colors
        ax1.pie(spending.values, labels=spending.index, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.set_title('Spending by Category', fontsize=14, fontweight='bold')

        # 2. Monthly Trend (Line Chart)
        ax2 = fig.add_subplot(gs[0, 1])
        monthly = self.analyzer.get_spending_by_month()
        ax2.plot(monthly.index, monthly.values, marker='o', linewidth=2, markersize=6, color='#2E86AB')
        ax2.fill_between(monthly.index, monthly.values, alpha=0.3, color='#2E86AB')
        ax2.set_title('Monthly Spending Trend', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Month', fontsize=10)
        ax2.set_ylabel('Amount (₹)', fontsize=10)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_currency_axis))
        ax2.grid(True, alpha=0.3)

        # 3. Category Bar Chart
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.barh(spending.index, spending.values, color=plt.cm.Spectral(range(len(spending))))
        ax3.set_title('Spending by Category (Bar)', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Amount (₹)', fontsize=10)
        ax3.xaxis.set_major_formatter(plt.FuncFormatter(format_currency_axis))

        # 4. Summary Statistics (Text)
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')

        stats = self.analyzer.get_summary_statistics()
        summary_text = f"""
        Summary Statistics
        {'='*40}

        Total Expenses: {stats['total_expenses']}
        Total Spending: ₹{stats['total_spending']:,.2f}

        Average Expense: ₹{stats['average_expense']:,.2f}
        Median Expense: ₹{stats['median_expense']:,.2f}

        Min Expense: ₹{stats['min_expense']:,.2f}
        Max Expense: ₹{stats['max_expense']:,.2f}
        """

        ax4.text(0.1, 0.5, summary_text, fontsize=12, family='monospace',
                verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        fig.suptitle('Expense Tracker Dashboard', fontsize=18, fontweight='bold', y=0.98)

        output_path = None
        if save:
            output_path = self.output_dir / "dashboard.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved dashboard to {output_path}")

        if show:
            plt.show()
        else:
            plt.close()

        return str(output_path) if output_path else None

    def generate_all_charts(self):
        """Generate and save all available charts."""
        logger.info("Generating all charts...")
        self.plot_spending_by_category(save=True, show=False)
        self.plot_monthly_trend(save=True, show=False)
        self.plot_category_bar_chart(save=True, show=False)
        self.plot_expense_distribution(save=True, show=False)
        self.create_dashboard(save=True, show=False)
        logger.info("All charts generated successfully")
