"""
File Item Entity

Represents a file in the indexing system with business logic and validation.
"""

import os
from datetime import datetime
from typing import Optional

from ..value_objects.file_path import FilePath
from ..value_objects.file_size import FileSize
from ..exceptions.validation_errors import InvalidFilenameError, EmptyValueError
from ..exceptions.domain_exceptions import FileValidationError


class FileItem:
    """
    Entity representing a file in the system.
    
    Contains file metadata and business logic for file operations.
    """
    
    # Business rules constants
    MAX_FILENAME_LENGTH = 255
    HIDDEN_FILE_PREFIX = '.'
    SYSTEM_FILE_PREFIXES = ('~', '$')
    
    def __init__(
        self,
        filename: str,
        full_path: FilePath,
        size: FileSize,
        modified_date: datetime,
        id: Optional[int] = None
    ):
        """
        Initialize a FileItem.
        
        Args:
            filename: The file name
            full_path: The complete file path
            size: The file size
            modified_date: When the file was last modified
            id: Optional database ID
            
        Raises:
            InvalidFilenameError: If filename is invalid
            FileValidationError: If file validation fails
        """
        self._id = id
        self._filename = self._validate_filename(filename)
        self._full_path = full_path
        self._size = size
        self._modified_date = modified_date
        
        # Validate consistency
        self._validate_consistency()
    
    def _validate_filename(self, filename: str) -> str:
        """Validate the filename according to business rules."""
        if not filename or not filename.strip():
            raise EmptyValueError("filename")
        
        filename = filename.strip()
        
        if len(filename) > self.MAX_FILENAME_LENGTH:
            raise InvalidFilenameError(
                filename, 
                f"Nome muito longo: {len(filename)} > {self.MAX_FILENAME_LENGTH}"
            )
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in invalid_chars:
            if char in filename:
                raise InvalidFilenameError(
                    filename,
                    f"Caractere inválido: '{char}'"
                )
        
        return filename
    
    def _validate_consistency(self) -> None:
        """Validate consistency between filename and path."""
        if self._full_path.name != self._filename:
            raise FileValidationError(
                self._filename,
                f"Nome do arquivo não coincide com o caminho: '{self._full_path.name}' != '{self._filename}'"
            )
    
    @property
    def id(self) -> Optional[int]:
        """Get the database ID."""
        return self._id
    
    @property
    def filename(self) -> str:
        """Get the filename."""
        return self._filename
    
    @property
    def full_path(self) -> FilePath:
        """Get the full path."""
        return self._full_path
    
    @property
    def parent_path(self) -> FilePath:
        """Get the parent directory path."""
        return self._full_path.parent
    
    @property
    def size(self) -> FileSize:
        """Get the file size."""
        return self._size
    
    @property
    def modified_date(self) -> datetime:
        """Get the modification date."""
        return self._modified_date
    
    @property
    def extension(self) -> str:
        """Get the file extension."""
        return self._full_path.suffix.lower()
    
    @property
    def stem(self) -> str:
        """Get the filename without extension."""
        return self._full_path.stem
    
    def is_hidden(self) -> bool:
        """Check if the file is hidden (starts with dot)."""
        return self._filename.startswith(self.HIDDEN_FILE_PREFIX)
    
    def is_system_file(self) -> bool:
        """Check if the file is a system file."""
        return any(self._filename.startswith(prefix) for prefix in self.SYSTEM_FILE_PREFIXES)
    
    def is_empty(self) -> bool:
        """Check if the file is empty."""
        return self._size.is_empty()
    
    def is_large(self, threshold_mb: int = 100) -> bool:
        """Check if the file is considered large."""
        return self._size.is_large(threshold_mb)
    
    def should_be_indexed(self) -> bool:
        """
        Business rule: Determine if this file should be indexed.
        
        Returns:
            True if file should be indexed
        """
        # Don't index hidden files (configurable business rule)
        if self.is_hidden():
            return False
        
        # Don't index system files
        if self.is_system_file():
            return False
        
        # Don't index empty files
        if self.is_empty():
            return False
        
        return True
    
    def get_category(self) -> str:
        """
        Get file category based on extension.
        
        Returns:
            Category name (e.g., 'document', 'image', 'video')
        """
        extension = self.extension
        
        # Document extensions
        document_exts = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'}
        if extension in document_exts:
            return 'document'
        
        # Image extensions
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'}
        if extension in image_exts:
            return 'image'
        
        # Video extensions
        video_exts = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        if extension in video_exts:
            return 'video'
        
        # Audio extensions
        audio_exts = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'}
        if extension in audio_exts:
            return 'audio'
        
        # Archive extensions
        archive_exts = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}
        if extension in archive_exts:
            return 'archive'
        
        # Code extensions
        code_exts = {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go'}
        if extension in code_exts:
            return 'code'
        
        return 'other'
    
    def update_metadata(self, size: FileSize, modified_date: datetime) -> None:
        """
        Update file metadata (for re-indexing scenarios).
        
        Args:
            size: New file size
            modified_date: New modification date
        """
        self._size = size
        self._modified_date = modified_date
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': self._id,
            'filename': self._filename,
            'full_path': str(self._full_path),
            'parent_path': str(self.parent_path),
            'size_bytes': self._size.bytes,
            'size_formatted': str(self._size),
            'modified_date': self._modified_date.isoformat(),
            'extension': self.extension,
            'category': self.get_category(),
            'is_hidden': self.is_hidden(),
            'is_system_file': self.is_system_file(),
            'should_be_indexed': self.should_be_indexed()
        }
    
    def __str__(self) -> str:
        return f"FileItem('{self._filename}', {self._size})"
    
    def __repr__(self) -> str:
        return (f"FileItem(id={self._id}, filename='{self._filename}', "
                f"size={self._size.bytes}, path='{self._full_path}')")
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, FileItem):
            return False
        # Files are equal if they have the same full path
        return self._full_path == other._full_path
    
    def __hash__(self) -> int:
        return hash(self._full_path)