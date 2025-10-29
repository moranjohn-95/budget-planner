"""
models.py
---------
Typed models used across the app:
- User
- Budget
- Transaction
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Represents a user stored in the Google Sheet."""
    user_id: int
    email: str
    password_hash: str
    created_at: datetime


@dataclass
class Budget:
    """Represents a budget record."""
    budget_id: int
    user_id: int
    category: str
    amount: float
    created_at: datetime


@dataclass
class Transaction:
    """Represents an expense or income transaction."""
    transaction_id: int
    budget_id: int
    description: str
    amount: float
    date: datetime
