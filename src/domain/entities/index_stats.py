"""
Index Statistics Entity

Represents statistics about the indexed files and folders.
"""

from typing import List, Tuple, Dict
from datetime import datetime

from ..value_objects.file_size import FileSize


class IndexStats:
    """
    Entity representing statistics about the file index.
    
    Contains aggregated information about indexed files and folders.
    """
    
    def __init__(
        self,
        total_files: int = 0,
        total_folders: int = 0,
        total_size_bytes: int = 0,
        extension_stats: List[Tuple[str, int]] = None,
        category_stats: Dict[str, int] = None,
        last_updated: datetime = None
    ):
        """
        Initialize IndexStats.
        
        Args:
            total_files: Total number of indexed files
            total_folders: Total number of indexed folders
            total_size_bytes: Total size of all files in bytes
            extension_stats: List of (extension, count) tuples
            category_stats: Dictionary of category -> count
            last_updated: When stats were last calculated
        """
        self._total_files = max(0, total_files)
        self._total_folders = max(0, total_folders)
        self._total_size = FileSize(max(0, total_size_bytes))
        self._extension_stats = extension_stats or []
        self._category_stats = category_stats or {}
        self._last_updated = last_updated or datetime.now()
    
    @property
    def total_files(self) -> int:
        """Get total number of files."""
        return self._total_files
    
    @property
    def total_folders(self) -> int:
        """Get total number of folders."""
        return self._total_folders
    
    @property
    def total_items(self) -> int:
        """Get total number of items (files + folders)."""
        return self._total_files + self._total_folders
    
    @property
    def total_size(self) -> FileSize:
        """Get total size of all files."""
        return self._total_size
    
    @property
    def extension_stats(self) -> List[Tuple[str, int]]:
        """Get extension statistics as list of (extension, count) tuples."""
        return self._extension_stats.copy()
    
    @property
    def category_stats(self) -> Dict[str, int]:
        """Get category statistics."""
        return self._category_stats.copy()
    
    @property
    def last_updated(self) -> datetime:
        """Get when stats were last updated."""
        return self._last_updated
    
    def is_empty(self) -> bool:
        """Check if the index is empty."""
        return self._total_files == 0 and self._total_folders == 0
    
    def get_most_common_extensions(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get the most common file extensions.
        
        Args:
            limit: Maximum number of extensions to return
            
        Returns:
            List of (extension, count) tuples sorted by count descending
        """
        sorted_extensions = sorted(self._extension_stats, key=lambda x: x[1], reverse=True)
        return sorted_extensions[:limit]
    
    def get_extension_percentage(self, extension: str) -> float:
        """
        Get the percentage of files with a specific extension.
        
        Args:
            extension: The file extension to check
            
        Returns:
            Percentage (0.0 to 100.0)
        """
        if self._total_files == 0:
            return 0.0
        
        extension_count = next((count for ext, count in self._extension_stats if ext == extension), 0)
        return (extension_count / self._total_files) * 100.0
    
    def get_average_file_size(self) -> FileSize:
        """
        Get the average file size.
        
        Returns:
            Average file size, or zero if no files
        """
        if self._total_files == 0:
            return FileSize.zero()
        
        average_bytes = self._total_size.bytes // self._total_files
        return FileSize(average_bytes)
    
    def get_largest_category(self) -> Tuple[str, int]:
        """
        Get the category with the most files.
        
        Returns:
            Tuple of (category_name, file_count)
        """
        if not self._category_stats:
            return ("unknown", 0)
        
        return max(self._category_stats.items(), key=lambda x: x[1])
    
    def get_category_percentage(self, category: str) -> float:
        """
        Get the percentage of files in a specific category.
        
        Args:
            category: The category to check
            
        Returns:
            Percentage (0.0 to 100.0)
        """
        if self._total_files == 0:
            return 0.0
        
        category_count = self._category_stats.get(category, 0)
        return (category_count / self._total_files) * 100.0
    
    def has_large_files(self, threshold_mb: int = 100) -> bool:
        """
        Check if there are files larger than the threshold.
        
        This is a business rule check that could be used for warnings.
        
        Args:
            threshold_mb: Size threshold in megabytes
            
        Returns:
            True if average file size suggests large files exist
        """
        avg_size = self.get_average_file_size()
        return avg_size.megabytes > (threshold_mb / 2)  # Heuristic
    
    def get_storage_efficiency_score(self) -> float:
        """
        Calculate a storage efficiency score (0.0 to 1.0).
        
        This is a business metric that considers file count vs total size.
        Higher scores indicate more efficient storage (many small files).
        
        Returns:
            Efficiency score between 0.0 and 1.0
        """
        if self._total_files == 0 or self._total_size.bytes == 0:
            return 0.0
        
        # Calculate files per GB
        files_per_gb = self._total_files / max(1, self._total_size.gigabytes)
        
        # Normalize to 0-1 scale (assuming 1000 files per GB is "efficient")
        efficiency = min(1.0, files_per_gb / 1000.0)
        return efficiency
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'total_files': self._total_files,
            'total_folders': self._total_folders,
            'total_items': self.total_items,
            'total_size_bytes': self._total_size.bytes,
            'total_size_formatted': str(self._total_size),
            'average_file_size': str(self.get_average_file_size()),
            'extension_stats': self._extension_stats,
            'most_common_extensions': self.get_most_common_extensions(5),
            'category_stats': self._category_stats,
            'largest_category': self.get_largest_category(),
            'storage_efficiency_score': self.get_storage_efficiency_score(),
            'has_large_files': self.has_large_files(),
            'last_updated': self._last_updated.isoformat(),
            'is_empty': self.is_empty()
        }
    
    def get_summary_text(self) -> str:
        """
        Get a human-readable summary of the statistics.
        
        Returns:
            Formatted summary string
        """
        if self.is_empty():
            return "Índice vazio - nenhum arquivo ou pasta indexado."
        
        lines = [
            f"Total de arquivos: {self._total_files:,}",
            f"Total de pastas: {self._total_folders:,}",
            f"Tamanho total: {self._total_size}",
            f"Tamanho médio por arquivo: {self.get_average_file_size()}",
        ]
        
        if self._extension_stats:
            most_common = self.get_most_common_extensions(3)
            ext_text = ", ".join([f"{ext} ({count})" for ext, count in most_common])
            lines.append(f"Extensões mais comuns: {ext_text}")
        
        if self._category_stats:
            largest_cat, cat_count = self.get_largest_category()
            lines.append(f"Categoria predominante: {largest_cat} ({cat_count} arquivos)")
        
        lines.append(f"Última atualização: {self._last_updated.strftime('%d/%m/%Y %H:%M:%S')}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return f"IndexStats({self._total_files} files, {self._total_folders} folders, {self._total_size})"
    
    def __repr__(self) -> str:
        return (f"IndexStats(total_files={self._total_files}, "
                f"total_folders={self._total_folders}, "
                f"total_size={self._total_size.bytes})")