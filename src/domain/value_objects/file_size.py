"""
File Size Value Object

Represents a file size with validation and formatting capabilities.
"""

from typing import Union

from ..exceptions.validation_errors import ValidationError
from ..exceptions.domain_exceptions import InvalidFileSizeError


class FileSize:
    """
    Value object representing a file size in bytes.
    
    Provides validation, formatting, and comparison methods.
    """
    
    def __init__(self, size_bytes: Union[int, float]):
        """
        Initialize a FileSize.
        
        Args:
            size_bytes: The size in bytes
            
        Raises:
            InvalidFileSizeError: If size is negative
            ValidationError: If size is not a number
        """
        if not isinstance(size_bytes, (int, float)):
            raise ValidationError(f"Tamanho deve ser um número, recebido: {type(size_bytes)}")
        
        if size_bytes < 0:
            raise InvalidFileSizeError(size_bytes, "Tamanho não pode ser negativo")
        
        self._bytes = int(size_bytes)
    
    @property
    def bytes(self) -> int:
        """Get the size in bytes."""
        return self._bytes
    
    @property
    def kilobytes(self) -> float:
        """Get the size in kilobytes."""
        return self._bytes / 1024
    
    @property
    def megabytes(self) -> float:
        """Get the size in megabytes."""
        return self._bytes / (1024 ** 2)
    
    @property
    def gigabytes(self) -> float:
        """Get the size in gigabytes."""
        return self._bytes / (1024 ** 3)
    
    @property
    def terabytes(self) -> float:
        """Get the size in terabytes."""
        return self._bytes / (1024 ** 4)
    
    def format_human_readable(self) -> str:
        """
        Format the size in human-readable format.
        
        Returns:
            Formatted size string (e.g., "1.5 MB", "2.3 GB")
        """
        if self._bytes < 1024:
            return f"{self._bytes} B"
        elif self._bytes < 1024 ** 2:
            return f"{self.kilobytes:.1f} KB"
        elif self._bytes < 1024 ** 3:
            return f"{self.megabytes:.1f} MB"
        elif self._bytes < 1024 ** 4:
            return f"{self.gigabytes:.1f} GB"
        else:
            return f"{self.terabytes:.1f} TB"
    
    def is_empty(self) -> bool:
        """Check if the file is empty (0 bytes)."""
        return self._bytes == 0
    
    def is_large(self, threshold_mb: int = 100) -> bool:
        """
        Check if the file is considered large.
        
        Args:
            threshold_mb: Threshold in megabytes (default: 100MB)
            
        Returns:
            True if file is larger than threshold
        """
        return self.megabytes > threshold_mb
    
    @classmethod
    def from_kilobytes(cls, kb: Union[int, float]) -> 'FileSize':
        """Create FileSize from kilobytes."""
        return cls(kb * 1024)
    
    @classmethod
    def from_megabytes(cls, mb: Union[int, float]) -> 'FileSize':
        """Create FileSize from megabytes."""
        return cls(mb * 1024 ** 2)
    
    @classmethod
    def from_gigabytes(cls, gb: Union[int, float]) -> 'FileSize':
        """Create FileSize from gigabytes."""
        return cls(gb * 1024 ** 3)
    
    @classmethod
    def zero(cls) -> 'FileSize':
        """Create a zero-sized FileSize."""
        return cls(0)
    
    def __str__(self) -> str:
        return self.format_human_readable()
    
    def __repr__(self) -> str:
        return f"FileSize({self._bytes})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, FileSize):
            return False
        return self._bytes == other._bytes
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, FileSize):
            return NotImplemented
        return self._bytes < other._bytes
    
    def __le__(self, other) -> bool:
        if not isinstance(other, FileSize):
            return NotImplemented
        return self._bytes <= other._bytes
    
    def __gt__(self, other) -> bool:
        if not isinstance(other, FileSize):
            return NotImplemented
        return self._bytes > other._bytes
    
    def __ge__(self, other) -> bool:
        if not isinstance(other, FileSize):
            return NotImplemented
        return self._bytes >= other._bytes
    
    def __add__(self, other) -> 'FileSize':
        if not isinstance(other, FileSize):
            return NotImplemented
        return FileSize(self._bytes + other._bytes)
    
    def __sub__(self, other) -> 'FileSize':
        if not isinstance(other, FileSize):
            return NotImplemented
        result = self._bytes - other._bytes
        if result < 0:
            raise InvalidFileSizeError(result, "Resultado da subtração não pode ser negativo")
        return FileSize(result)
    
    def __hash__(self) -> int:
        return hash(self._bytes)