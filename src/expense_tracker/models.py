"""
Data models for the expense tracker application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

VALID_CATEGORIES = {"Food", "Travel", "Books", "Shopping", "Entertainment", "Utilities", "Healthcare", "Other"}


@dataclass
class Expense:
    """Represents a single expense entry."""

    date: str
    category: str
    description: str
    amount: float
    id: Optional[int] = None

    def __post_init__(self):
        """Validate expense data after initialization."""
        self.validate()

    def validate(self):
        """Validate expense fields."""
        # Validate date format
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {self.date}. Expected YYYY-MM-DD")

        # Validate category
        if self.category not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category: {self.category}. "
                f"Must be one of {', '.join(sorted(VALID_CATEGORIES))}"
            )

        # Validate amount
        if self.amount <= 0:
            raise ValueError(f"Amount must be positive, got: {self.amount}")

        # Validate description
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")

    def to_dict(self):
        """Convert expense to dictionary."""
        return {
            "id": self.id,
            "date": self.date,
            "category": self.category,
            "description": self.description,
            "amount": self.amount
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        """Create Expense from dictionary."""
        return cls(
            id=data.get("id"),
            date=data["date"],
            category=data["category"],
            description=data["description"],
            amount=data["amount"]
        )
