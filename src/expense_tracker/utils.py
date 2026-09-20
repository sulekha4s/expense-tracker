"""
Utility functions for the expense tracker application.
"""

import logging
from datetime import datetime
from typing import Optional


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return application logger."""
    logger = logging.getLogger("expense_tracker")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_user_input(
    prompt: str,
    input_type: type = str,
    error_message: str = "Invalid input. Please try again."
) -> any:
    """
    Get user input with type conversion.

    Args:
        prompt: The input prompt to display
        input_type: Type to convert input to (str, int, float)
        error_message: Message to display on error

    Returns:
        Type-converted user input
    """
    while True:
        try:
            user_input = input(prompt)
            converted = input_type(user_input)
            return converted
        except ValueError as e:
            print(f"{error_message}: {str(e)}")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


def format_currency(amount: float, currency: str = "₹") -> str:
    """Format amount as currency string."""
    return f"{currency}{amount:,.2f}"


def parse_date_input(date_str: str) -> str:
    """
    Parse and validate date input, converting to YYYY-MM-DD format.

    Accepts:
    - YYYY-MM-DD (ISO format)
    - DD/MM/YYYY
    - DD-MM-YYYY
    - 'today' or 'now'

    Returns:
        Date in YYYY-MM-DD format
    """
    date_str = date_str.strip().lower()

    # Handle special keywords
    if date_str in ('today', 'now'):
        return datetime.now().strftime("%Y-%m-%d")

    # Try ISO format first
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
    ]

    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError(
        f"Invalid date format: {date_str}. "
        "Expected YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, or 'today'"
    )
