"""
File System Interface

Defines the contract for file system operations.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Tuple, List, Optional
from datetime import datetime


class FileSystem(ABC):
    """
    Abstract interface for file system operations.
    
    This interface defines the contract that infrastructure implementations
    must follow for file system access.
    """
    
    @abstractmethod
    def walk_directory(self, path: str) -> Iterator[Tuple[str, List[str], List[str]]]:
        """
        Walk through directory tree.
        
        Args:
            path: Root directory path to walk
            
        Yields:
            Tuples of (dirpath, dirnames, filenames)
        """
        pass
    
    @abstractmethod
    def get_file_info(self, path: str) -> Tuple[int, datetime]:
        """
        Get file information.
        
        Args:
            path: File path
            
        Returns:
            Tuple of (size_bytes, modified_date)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If no access permission
        """
        pass
    
    @abstractmethod
    def get_folder_info(self, path: str) -> datetime:
        """
        Get folder information.
        
        Args:
            path: Folder path
            
        Returns:
            Modified date
            
        Raises:
            FileNotFoundError: If folder doesn't exist
            PermissionError: If no access permission
        """
        pass
    
    @abstractmethod
    def path_exists(self, path: str) -> bool:
        """
        Check if path exists.
        
        Args:
            path: Path to check
            
        Returns:
            True if path exists
        """
        pass
    
    @abstractmethod
    def is_file(self, path: str) -> bool:
        """
        Check if path is a file.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a file
        """
        pass
    
    @abstractmethod
    def is_directory(self, path: str) -> bool:
        """
        Check if path is a directory.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a directory
        """
        pass
    
    @abstractmethod
    def has_read_permission(self, path: str) -> bool:
        """
        Check if we have read permission for path.
        
        Args:
            path: Path to check
            
        Returns:
            True if we can read the path
        """
        pass
    
    @abstractmethod
    def get_absolute_path(self, path: str) -> str:
        """
        Get absolute path.
        
        Args:
            path: Path to resolve
            
        Returns:
            Absolute path
        """
        pass
    
    @abstractmethod
    def normalize_path(self, path: str) -> str:
        """
        Normalize path (resolve . and .. components).
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized path
        """
        pass
    
    @abstractmethod
    def get_parent_path(self, path: str) -> str:
        """
        Get parent directory path.
        
        Args:
            path: Path to get parent of
            
        Returns:
            Parent directory path
        """
        pass
    
    @abstractmethod
    def get_filename(self, path: str) -> str:
        """
        Get filename from path.
        
        Args:
            path: File path
            
        Returns:
            Filename
        """
        pass
    
    @abstractmethod
    def get_file_extension(self, path: str) -> str:
        """
        Get file extension from path.
        
        Args:
            path: File path
            
        Returns:
            File extension (including dot)
        """
        pass
    
    @abstractmethod
    def join_paths(self, *paths: str) -> str:
        """
        Join multiple path components.
        
        Args:
            *paths: Path components to join
            
        Returns:
            Joined path
        """
        pass
    
    @abstractmethod
    def list_directory(self, path: str) -> Tuple[List[str], List[str]]:
        """
        List directory contents.
        
        Args:
            path: Directory path
            
        Returns:
            Tuple of (subdirectories, files)
            
        Raises:
            FileNotFoundError: If directory doesn't exist
            PermissionError: If no access permission
        """
        pass
    
    @abstractmethod
    def get_directory_size(self, path: str) -> int:
        """
        Get total size of directory (recursive).
        
        Args:
            path: Directory path
            
        Returns:
            Total size in bytes
        """
        pass
    
    @abstractmethod
    def count_items_in_directory(self, path: str) -> Tuple[int, int]:
        """
        Count files and folders in directory (recursive).
        
        Args:
            path: Directory path
            
        Returns:
            Tuple of (file_count, folder_count)
        """
        pass