"""
Repository Interfaces

Defines contracts for data persistence operations.
"""

from .file_repository import FileRepository
from .stats_repository import StatsRepository

__all__ = ['FileRepository', 'StatsRepository']