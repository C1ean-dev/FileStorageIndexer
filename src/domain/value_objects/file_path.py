"""
File Path Value Object

Represents a file or directory path with validation and normalization.
"""

import os
from pathlib import Path
from typing import Optional

from ..exceptions.validation_errors import InvalidPathError, EmptyValueError


class FilePath:
    """
    Value object representing a file or directory path.
    
    Provides validation, normalization, and path manipulation methods.
    """
    
    def __init__(self, path: str):
        """
        Initialize a FilePath.
        
        Args:
            path: The file or directory path
            
        Raises:
            EmptyValueError: If path is empty
            InvalidPathError: If path is invalid
        """
        if not path or not path.strip():
            raise EmptyValueError("path")
        
        self._original_path = path.strip()
        self._normalized_path = self._normalize_path(self._original_path)
        self._validate_path()
    
    def _normalize_path(self, path: str) -> str:
        """Normalize the path using pathlib."""
        try:
            return str(Path(path).resolve())
        except (OSError, ValueError) as e:
            raise InvalidPathError(path, f"Erro ao normalizar caminho: {e}")
    
    def _validate_path(self) -> None:
        """Validate the path format."""
        # Check for invalid characters (basic validation)
        invalid_chars = ['<', '>', '|', '*', '?']
        for char in invalid_chars:
            if char in self._original_path:
                raise InvalidPathError(
                    self._original_path, 
                    f"Caractere inválido encontrado: '{char}'"
                )
        
        # Check path length (Windows limitation)
        if len(self._normalized_path) > 260:
            raise InvalidPathError(
                self._original_path,
                f"Caminho muito longo: {len(self._normalized_path)} caracteres"
            )
    
    @property
    def value(self) -> str:
        """Get the normalized path value."""
        return self._normalized_path
    
    @property
    def original(self) -> str:
        """Get the original path value."""
        return self._original_path
    
    @property
    def parent(self) -> 'FilePath':
        """Get the parent directory path."""
        parent_path = str(Path(self._normalized_path).parent)
        return FilePath(parent_path)
    
    @property
    def name(self) -> str:
        """Get the file or directory name."""
        return Path(self._normalized_path).name
    
    @property
    def stem(self) -> str:
        """Get the file name without extension."""
        return Path(self._normalized_path).stem
    
    @property
    def suffix(self) -> str:
        """Get the file extension."""
        return Path(self._normalized_path).suffix
    
    @property
    def is_absolute(self) -> bool:
        """Check if path is absolute."""
        return Path(self._normalized_path).is_absolute()
    
    def exists(self) -> bool:
        """Check if the path exists."""
        return Path(self._normalized_path).exists()
    
    def is_file(self) -> bool:
        """Check if path points to a file."""
        return Path(self._normalized_path).is_file()
    
    def is_dir(self) -> bool:
        """Check if path points to a directory."""
        return Path(self._normalized_path).is_dir()
    
    def join(self, *parts: str) -> 'FilePath':
        """Join path with additional parts."""
        new_path = str(Path(self._normalized_path).joinpath(*parts))
        return FilePath(new_path)
    
    def relative_to(self, other: 'FilePath') -> str:
        """Get path relative to another path."""
        try:
            return str(Path(self._normalized_path).relative_to(other.value))
        except ValueError as e:
            raise InvalidPathError(
                self._original_path,
                f"Não é possível calcular caminho relativo: {e}"
            )
    
    def __str__(self) -> str:
        return self._normalized_path
    
    def __repr__(self) -> str:
        return f"FilePath('{self._normalized_path}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, FilePath):
            return False
        return self._normalized_path == other._normalized_path
    
    def __hash__(self) -> int:
        return hash(self._normalized_path)