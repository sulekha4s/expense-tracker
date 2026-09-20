#!/usr/bin/env python3
"""
Expense Tracker - CLI expense management tool

Usage:
    python main.py
"""

from src.expense_tracker.main import ExpenseTrackerCLI

if __name__ == '__main__':
    cli = ExpenseTrackerCLI()
    cli.run()
