"""
Statistics Repository Interface

Defines the contract for statistics persistence and retrieval operations.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict

from src.domain.entities.index_stats import IndexStats


class StatsRepository(ABC):
    """
    Abstract interface for statistics repository operations.
    
    This interface defines the contract that infrastructure implementations
    must follow for statistics persistence and retrieval.
    """
    
    @abstractmethod
    def get_file_count(self) -> int:
        """
        Get the total number of files in the index.
        
        Returns:
            Total file count
        """
        pass
    
    @abstractmethod
    def get_folder_count(self) -> int:
        """
        Get the total number of folders in the index.
        
        Returns:
            Total folder count
        """
        pass
    
    @abstractmethod
    def get_total_size(self) -> int:
        """
        Get the total size of all files in bytes.
        
        Returns:
            Total size in bytes
        """
        pass
    
    @abstractmethod
    def get_extension_stats(self) -> List[Tuple[str, int]]:
        """
        Get statistics about file extensions.
        
        Returns:
            List of (extension, count) tuples sorted by count descending
        """
        pass
    
    @abstractmethod
    def get_category_stats(self) -> Dict[str, int]:
        """
        Get statistics about file categories.
        
        Returns:
            Dictionary mapping category to file count
        """
        pass
    
    @abstractmethod
    def get_size_distribution(self) -> Dict[str, int]:
        """
        Get distribution of files by size ranges.
        
        Returns:
            Dictionary mapping size range to file count
        """
        pass
    
    @abstractmethod
    def get_folder_depth_stats(self) -> Dict[int, int]:
        """
        Get statistics about folder depth distribution.
        
        Returns:
            Dictionary mapping depth level to folder count
        """
        pass
    
    @abstractmethod
    def get_largest_files(self, limit: int = 10) -> List[Tuple[str, str, int]]:
        """
        Get the largest files in the index.
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of (filename, path, size_bytes) tuples
        """
        pass
    
    @abstractmethod
    def get_most_common_extensions(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get the most common file extensions.
        
        Args:
            limit: Maximum number of extensions to return
            
        Returns:
            List of (extension, count) tuples
        """
        pass
    
    @abstractmethod
    def get_files_by_category(self, category: str) -> int:
        """
        Get the number of files in a specific category.
        
        Args:
            category: Category name to count
            
        Returns:
            Number of files in the category
        """
        pass
    
    @abstractmethod
    def get_files_by_extension(self, extension: str) -> int:
        """
        Get the number of files with a specific extension.
        
        Args:
            extension: Extension to count (e.g., '.pdf')
            
        Returns:
            Number of files with the extension
        """
        pass
    
    @abstractmethod
    def get_empty_files_count(self) -> int:
        """
        Get the number of empty files (0 bytes).
        
        Returns:
            Number of empty files
        """
        pass
    
    @abstractmethod
    def get_hidden_files_count(self) -> int:
        """
        Get the number of hidden files.
        
        Returns:
            Number of hidden files
        """
        pass
    
    @abstractmethod
    def get_system_files_count(self) -> int:
        """
        Get the number of system files.
        
        Returns:
            Number of system files
        """
        pass
    
    @abstractmethod
    def get_average_file_size(self) -> float:
        """
        Get the average file size in bytes.
        
        Returns:
            Average file size, or 0.0 if no files
        """
        pass
    
    @abstractmethod
    def get_files_modified_since(self, days: int) -> int:
        """
        Get the number of files modified within the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Number of recently modified files
        """
        pass
    
    @abstractmethod
    def get_duplicate_filenames(self) -> List[Tuple[str, int]]:
        """
        Get filenames that appear multiple times (different paths).
        
        Returns:
            List of (filename, count) tuples for duplicates
        """
        pass
    
    @abstractmethod
    def calculate_comprehensive_stats(self) -> IndexStats:
        """
        Calculate comprehensive statistics for the entire index.
        
        This method should aggregate all available statistics into
        a single IndexStats entity.
        
        Returns:
            IndexStats entity with all calculated statistics
        """
        pass
    
    @abstractmethod
    def refresh_stats_cache(self) -> bool:
        """
        Refresh any cached statistics.
        
        This method should be called after significant changes
        to the index to ensure statistics are up-to-date.
        
        Returns:
            True if refresh was successful
        """
        pass