"""
OS File System Implementation

Concrete implementation of FileSystem interface using os module.
"""

import os
from datetime import datetime
from typing import Iterator, Tuple, List
from pathlib import Path

from src.application.interfaces.external.file_system import FileSystem


class OsFileSystem(FileSystem):
    """
    File system implementation using Python's os module.
    
    This implementation provides access to the operating system's file system
    using standard Python libraries.
    """
    
    def __init__(self):
        """Initialize the OS file system implementation."""
        pass
    
    def walk_directory(self, path: str) -> Iterator[Tuple[str, List[str], List[str]]]:
        """
        Walk through directory tree using os.walk.
        
        Args:
            path: Root directory path to walk
            
        Yields:
            Tuples of (dirpath, dirnames, filenames)
        """
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                yield dirpath, dirnames, filenames
        except (OSError, PermissionError) as e:
            # Log error but don't stop the iteration
            # The caller should handle logging
            pass
    
    def get_file_info(self, path: str) -> Tuple[int, datetime]:
        """
        Get file information using os.stat.
        
        Args:
            path: File path
            
        Returns:
            Tuple of (size_bytes, modified_date)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If no access permission
        """
        try:
            stat_result = os.stat(path)
            size_bytes = stat_result.st_size
            modified_timestamp = stat_result.st_mtime
            modified_date = datetime.fromtimestamp(modified_timestamp)
            
            return size_bytes, modified_date
            
        except OSError as e:
            if e.errno == 2:  # File not found
                raise FileNotFoundError(f"File not found: {path}")
            elif e.errno == 13:  # Permission denied
                raise PermissionError(f"Permission denied: {path}")
            else:
                raise
    
    def get_folder_info(self, path: str) -> datetime:
        """
        Get folder information using os.stat.
        
        Args:
            path: Folder path
            
        Returns:
            Modified date
            
        Raises:
            FileNotFoundError: If folder doesn't exist
            PermissionError: If no access permission
        """
        try:
            stat_result = os.stat(path)
            modified_timestamp = stat_result.st_mtime
            return datetime.fromtimestamp(modified_timestamp)
            
        except OSError as e:
            if e.errno == 2:  # File not found
                raise FileNotFoundError(f"Folder not found: {path}")
            elif e.errno == 13:  # Permission denied
                raise PermissionError(f"Permission denied: {path}")
            else:
                raise
    
    def path_exists(self, path: str) -> bool:
        """
        Check if path exists using os.path.exists.
        
        Args:
            path: Path to check
            
        Returns:
            True if path exists
        """
        return os.path.exists(path)
    
    def is_file(self, path: str) -> bool:
        """
        Check if path is a file using os.path.isfile.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a file
        """
        return os.path.isfile(path)
    
    def is_directory(self, path: str) -> bool:
        """
        Check if path is a directory using os.path.isdir.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a directory
        """
        return os.path.isdir(path)
    
    def has_read_permission(self, path: str) -> bool:
        """
        Check if we have read permission using os.access.
        
        Args:
            path: Path to check
            
        Returns:
            True if we can read the path
        """
        return os.access(path, os.R_OK)
    
    def get_absolute_path(self, path: str) -> str:
        """
        Get absolute path using os.path.abspath.
        
        Args:
            path: Path to resolve
            
        Returns:
            Absolute path
        """
        return os.path.abspath(path)
    
    def normalize_path(self, path: str) -> str:
        """
        Normalize path using os.path.normpath.
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized path
        """
        return os.path.normpath(path)
    
    def get_parent_path(self, path: str) -> str:
        """
        Get parent directory path using os.path.dirname.
        
        Args:
            path: Path to get parent of
            
        Returns:
            Parent directory path
        """
        return os.path.dirname(path)
    
    def get_filename(self, path: str) -> str:
        """
        Get filename from path using os.path.basename.
        
        Args:
            path: File path
            
        Returns:
            Filename
        """
        return os.path.basename(path)
    
    def get_file_extension(self, path: str) -> str:
        """
        Get file extension using os.path.splitext.
        
        Args:
            path: File path
            
        Returns:
            File extension (including dot)
        """
        _, extension = os.path.splitext(path)
        return extension.lower()
    
    def join_paths(self, *paths: str) -> str:
        """
        Join multiple path components using os.path.join.
        
        Args:
            *paths: Path components to join
            
        Returns:
            Joined path
        """
        return os.path.join(*paths)
    
    def list_directory(self, path: str) -> Tuple[List[str], List[str]]:
        """
        List directory contents using os.listdir.
        
        Args:
            path: Directory path
            
        Returns:
            Tuple of (subdirectories, files)
            
        Raises:
            FileNotFoundError: If directory doesn't exist
            PermissionError: If no access permission
        """
        try:
            items = os.listdir(path)
            subdirectories = []
            files = []
            
            for item in items:
                item_path = self.join_paths(path, item)
                if self.is_directory(item_path):
                    subdirectories.append(item)
                elif self.is_file(item_path):
                    files.append(item)
            
            return subdirectories, files
            
        except OSError as e:
            if e.errno == 2:  # File not found
                raise FileNotFoundError(f"Directory not found: {path}")
            elif e.errno == 13:  # Permission denied
                raise PermissionError(f"Permission denied: {path}")
            else:
                raise
    
    def get_directory_size(self, path: str) -> int:
        """
        Get total size of directory (recursive).
        
        Args:
            path: Directory path
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in self.walk_directory(path):
                for filename in filenames:
                    file_path = self.join_paths(dirpath, filename)
                    try:
                        size, _ = self.get_file_info(file_path)
                        total_size += size
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
        except (OSError, PermissionError):
            # Return partial size if we can't access some parts
            pass
        
        return total_size
    
    def count_items_in_directory(self, path: str) -> Tuple[int, int]:
        """
        Count files and folders in directory (recursive).
        
        Args:
            path: Directory path
            
        Returns:
            Tuple of (file_count, folder_count)
        """
        file_count = 0
        folder_count = 0
        
        try:
            for dirpath, dirnames, filenames in self.walk_directory(path):
                file_count += len(filenames)
                folder_count += len(dirnames)
        except (OSError, PermissionError):
            # Return partial counts if we can't access some parts
            pass
        
        return file_count, folder_count