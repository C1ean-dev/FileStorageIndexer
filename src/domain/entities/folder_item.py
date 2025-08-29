"""
Folder Item Entity

Represents a folder in the indexing system with business logic and validation.
"""

from datetime import datetime
from typing import Optional

from ..value_objects.file_path import FilePath
from ..exceptions.validation_errors import InvalidFilenameError, EmptyValueError
from ..exceptions.domain_exceptions import FileValidationError


class FolderItem:
    """
    Entity representing a folder in the system.
    
    Contains folder metadata and business logic for folder operations.
    """
    
    # Business rules constants
    MAX_FOLDER_NAME_LENGTH = 255
    HIDDEN_FOLDER_PREFIX = '.'
    SYSTEM_FOLDER_NAMES = {'System Volume Information', '$Recycle.Bin', 'pagefile.sys', 'hiberfil.sys'}
    
    def __init__(
        self,
        folder_name: str,
        full_path: FilePath,
        modified_date: datetime,
        id: Optional[int] = None
    ):
        """
        Initialize a FolderItem.
        
        Args:
            folder_name: The folder name
            full_path: The complete folder path
            modified_date: When the folder was last modified
            id: Optional database ID
            
        Raises:
            InvalidFilenameError: If folder name is invalid
            FileValidationError: If folder validation fails
        """
        self._id = id
        self._folder_name = self._validate_folder_name(folder_name)
        self._full_path = full_path
        self._modified_date = modified_date
        
        # Validate consistency
        self._validate_consistency()
    
    def _validate_folder_name(self, folder_name: str) -> str:
        """Validate the folder name according to business rules."""
        if not folder_name or not folder_name.strip():
            raise EmptyValueError("folder_name")
        
        folder_name = folder_name.strip()
        
        if len(folder_name) > self.MAX_FOLDER_NAME_LENGTH:
            raise InvalidFilenameError(
                folder_name, 
                f"Nome muito longo: {len(folder_name)} > {self.MAX_FOLDER_NAME_LENGTH}"
            )
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in invalid_chars:
            if char in folder_name:
                raise InvalidFilenameError(
                    folder_name,
                    f"Caractere inválido: '{char}'"
                )
        
        return folder_name
    
    def _validate_consistency(self) -> None:
        """Validate consistency between folder name and path."""
        if self._full_path.name != self._folder_name:
            raise FileValidationError(
                self._folder_name,
                f"Nome da pasta não coincide com o caminho: '{self._full_path.name}' != '{self._folder_name}'"
            )
    
    @property
    def id(self) -> Optional[int]:
        """Get the database ID."""
        return self._id
    
    @property
    def folder_name(self) -> str:
        """Get the folder name."""
        return self._folder_name
    
    @property
    def full_path(self) -> FilePath:
        """Get the full path."""
        return self._full_path
    
    @property
    def parent_path(self) -> FilePath:
        """Get the parent directory path."""
        return self._full_path.parent
    
    @property
    def modified_date(self) -> datetime:
        """Get the modification date."""
        return self._modified_date
    
    def is_hidden(self) -> bool:
        """Check if the folder is hidden (starts with dot)."""
        return self._folder_name.startswith(self.HIDDEN_FOLDER_PREFIX)
    
    def is_system_folder(self) -> bool:
        """Check if the folder is a system folder."""
        return self._folder_name in self.SYSTEM_FOLDER_NAMES
    
    def is_root_folder(self) -> bool:
        """Check if this is a root folder (drive root)."""
        return len(str(self._full_path).strip('\\').strip('/')) <= 3  # e.g., "C:\" or "/"
    
    def should_be_indexed(self) -> bool:
        """
        Business rule: Determine if this folder should be indexed.
        
        Returns:
            True if folder should be indexed
        """
        # Don't index hidden folders (configurable business rule)
        if self.is_hidden():
            return False
        
        # Don't index system folders
        if self.is_system_folder():
            return False
        
        return True
    
    def should_be_scanned(self) -> bool:
        """
        Business rule: Determine if this folder should be scanned for files.
        
        Returns:
            True if folder should be scanned
        """
        # Even if we don't index the folder itself, we might want to scan its contents
        # This is a separate business rule from indexing
        
        # Don't scan system folders
        if self.is_system_folder():
            return False
        
        # Don't scan certain hidden folders that are known to be problematic
        problematic_folders = {'.git', '.svn', '.hg', 'node_modules', '__pycache__'}
        if self._folder_name in problematic_folders:
            return False
        
        return True
    
    def get_depth_level(self) -> int:
        """
        Calculate the depth level of this folder.
        
        Returns:
            Depth level (0 for root, 1 for first level, etc.)
        """
        path_parts = str(self._full_path).replace('\\', '/').strip('/').split('/')
        # Filter out empty parts and drive letters
        meaningful_parts = [part for part in path_parts if part and ':' not in part]
        return len(meaningful_parts)
    
    def update_metadata(self, modified_date: datetime) -> None:
        """
        Update folder metadata (for re-indexing scenarios).
        
        Args:
            modified_date: New modification date
        """
        self._modified_date = modified_date
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': self._id,
            'folder_name': self._folder_name,
            'full_path': str(self._full_path),
            'parent_path': str(self.parent_path),
            'modified_date': self._modified_date.isoformat(),
            'is_hidden': self.is_hidden(),
            'is_system_folder': self.is_system_folder(),
            'is_root_folder': self.is_root_folder(),
            'depth_level': self.get_depth_level(),
            'should_be_indexed': self.should_be_indexed(),
            'should_be_scanned': self.should_be_scanned()
        }
    
    def __str__(self) -> str:
        return f"FolderItem('{self._folder_name}')"
    
    def __repr__(self) -> str:
        return (f"FolderItem(id={self._id}, folder_name='{self._folder_name}', "
                f"path='{self._full_path}')")
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, FolderItem):
            return False
        # Folders are equal if they have the same full path
        return self._full_path == other._full_path
    
    def __hash__(self) -> int:
        return hash(self._full_path)