"""
Statistics Calculator Domain Service

Contains business logic for calculating statistics about indexed files and folders.
"""

from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from datetime import datetime

from ..entities.file_item import FileItem
from ..entities.folder_item import FolderItem
from ..entities.index_stats import IndexStats
from ..value_objects.file_size import FileSize


class StatisticsCalculator:
    """
    Domain service for calculating statistics about the file index.
    
    Contains business logic for aggregating and analyzing file/folder data.
    """
    
    def __init__(self):
        """Initialize the StatisticsCalculator."""
        pass
    
    def calculate_index_stats(
        self, 
        files: List[FileItem], 
        folders: List[FolderItem]
    ) -> IndexStats:
        """
        Calculate comprehensive statistics for the index.
        
        Args:
            files: List of all indexed files
            folders: List of all indexed folders
            
        Returns:
            IndexStats entity with calculated statistics
        """
        # Basic counts
        total_files = len(files)
        total_folders = len(folders)
        
        # Calculate total size
        total_size_bytes = sum(file.size.bytes for file in files)
        
        # Calculate extension statistics
        extension_stats = self._calculate_extension_stats(files)
        
        # Calculate category statistics
        category_stats = self._calculate_category_stats(files)
        
        return IndexStats(
            total_files=total_files,
            total_folders=total_folders,
            total_size_bytes=total_size_bytes,
            extension_stats=extension_stats,
            category_stats=category_stats,
            last_updated=datetime.now()
        )
    
    def calculate_extension_distribution(self, files: List[FileItem]) -> Dict[str, float]:
        """
        Calculate the percentage distribution of file extensions.
        
        Args:
            files: List of FileItem objects
            
        Returns:
            Dictionary mapping extension to percentage
        """
        if not files:
            return {}
        
        extension_counts = Counter(file.extension for file in files)
        total_files = len(files)
        
        return {
            ext: (count / total_files) * 100.0
            for ext, count in extension_counts.items()
        }
    
    def calculate_category_distribution(self, files: List[FileItem]) -> Dict[str, float]:
        """
        Calculate the percentage distribution of file categories.
        
        Args:
            files: List of FileItem objects
            
        Returns:
            Dictionary mapping category to percentage
        """
        if not files:
            return {}
        
        category_counts = Counter(file.get_category() for file in files)
        total_files = len(files)
        
        return {
            category: (count / total_files) * 100.0
            for category, count in category_counts.items()
        }
    
    def calculate_size_distribution(self, files: List[FileItem]) -> Dict[str, int]:
        """
        Calculate distribution of files by size ranges.
        
        Args:
            files: List of FileItem objects
            
        Returns:
            Dictionary mapping size range to file count
        """
        size_ranges = {
            'Muito pequeno (< 1KB)': 0,
            'Pequeno (1KB - 1MB)': 0,
            'Médio (1MB - 10MB)': 0,
            'Grande (10MB - 100MB)': 0,
            'Muito grande (> 100MB)': 0
        }
        
        for file in files:
            size_bytes = file.size.bytes
            
            if size_bytes < 1024:
                size_ranges['Muito pequeno (< 1KB)'] += 1
            elif size_bytes < 1024 * 1024:
                size_ranges['Pequeno (1KB - 1MB)'] += 1
            elif size_bytes < 10 * 1024 * 1024:
                size_ranges['Médio (1MB - 10MB)'] += 1
            elif size_bytes < 100 * 1024 * 1024:
                size_ranges['Grande (10MB - 100MB)'] += 1
            else:
                size_ranges['Muito grande (> 100MB)'] += 1
        
        return size_ranges
    
    def calculate_folder_depth_distribution(self, folders: List[FolderItem]) -> Dict[int, int]:
        """
        Calculate distribution of folders by depth level.
        
        Args:
            folders: List of FolderItem objects
            
        Returns:
            Dictionary mapping depth level to folder count
        """
        depth_counts = Counter(folder.get_depth_level() for folder in folders)
        return dict(depth_counts)
    
    def find_largest_files(self, files: List[FileItem], limit: int = 10) -> List[FileItem]:
        """
        Find the largest files in the index.
        
        Args:
            files: List of FileItem objects
            limit: Maximum number of files to return
            
        Returns:
            List of largest files, sorted by size descending
        """
        return sorted(files, key=lambda f: f.size.bytes, reverse=True)[:limit]
    
    def find_duplicate_names(self, files: List[FileItem]) -> Dict[str, List[FileItem]]:
        """
        Find files with duplicate names (but different paths).
        
        Args:
            files: List of FileItem objects
            
        Returns:
            Dictionary mapping filename to list of files with that name
        """
        name_groups = defaultdict(list)
        
        for file in files:
            name_groups[file.filename].append(file)
        
        # Only return groups with more than one file
        return {name: file_list for name, file_list in name_groups.items() if len(file_list) > 1}
    
    def calculate_storage_waste(self, files: List[FileItem]) -> Dict[str, any]:
        """
        Calculate potential storage waste (empty files, duplicates, etc.).
        
        Args:
            files: List of FileItem objects
            
        Returns:
            Dictionary with waste analysis
        """
        empty_files = [f for f in files if f.is_empty()]
        hidden_files = [f for f in files if f.is_hidden()]
        system_files = [f for f in files if f.is_system_file()]
        
        # Calculate wasted space from empty files
        empty_count = len(empty_files)
        
        # Calculate space used by hidden/system files
        hidden_size = sum(f.size.bytes for f in hidden_files)
        system_size = sum(f.size.bytes for f in system_files)
        
        return {
            'empty_files_count': empty_count,
            'hidden_files_count': len(hidden_files),
            'hidden_files_size': FileSize(hidden_size),
            'system_files_count': len(system_files),
            'system_files_size': FileSize(system_size),
            'total_waste_potential': FileSize(hidden_size + system_size)
        }
    
    def calculate_indexing_health(self, files: List[FileItem], folders: List[FolderItem]) -> Dict[str, any]:
        """
        Calculate health metrics for the index.
        
        Args:
            files: List of FileItem objects
            folders: List of FolderItem objects
            
        Returns:
            Dictionary with health metrics
        """
        total_items = len(files) + len(folders)
        
        if total_items == 0:
            return {
                'health_score': 0.0,
                'status': 'empty',
                'recommendations': ['Indexe alguns arquivos para começar']
            }
        
        # Calculate various health factors
        indexable_files = [f for f in files if f.should_be_indexed()]
        indexable_folders = [f for f in folders if f.should_be_indexed()]
        
        indexable_ratio = (len(indexable_files) + len(indexable_folders)) / total_items
        
        # Check for reasonable file/folder ratio
        if len(folders) > 0:
            file_folder_ratio = len(files) / len(folders)
        else:
            file_folder_ratio = len(files)  # All files, no folders
        
        # Ideal ratio is between 5-50 files per folder
        ratio_score = 1.0
        if file_folder_ratio < 5:
            ratio_score = 0.7  # Too few files per folder
        elif file_folder_ratio > 50:
            ratio_score = 0.8  # Too many files per folder
        
        # Calculate overall health score
        health_score = (indexable_ratio * 0.6 + ratio_score * 0.4) * 100
        
        # Determine status
        if health_score >= 80:
            status = 'excellent'
        elif health_score >= 60:
            status = 'good'
        elif health_score >= 40:
            status = 'fair'
        else:
            status = 'poor'
        
        # Generate recommendations
        recommendations = []
        if indexable_ratio < 0.8:
            recommendations.append('Considere limpar arquivos desnecessários')
        if file_folder_ratio > 50:
            recommendations.append('Muitos arquivos por pasta - considere reorganizar')
        if file_folder_ratio < 5:
            recommendations.append('Poucas pastas indexadas - considere indexar mais diretórios')
        
        if not recommendations:
            recommendations.append('Índice está em bom estado')
        
        return {
            'health_score': round(health_score, 1),
            'status': status,
            'indexable_ratio': round(indexable_ratio * 100, 1),
            'file_folder_ratio': round(file_folder_ratio, 1),
            'recommendations': recommendations
        }
    
    def _calculate_extension_stats(self, files: List[FileItem]) -> List[Tuple[str, int]]:
        """Calculate extension statistics."""
        extension_counts = Counter(file.extension for file in files)
        return extension_counts.most_common()
    
    def _calculate_category_stats(self, files: List[FileItem]) -> Dict[str, int]:
        """Calculate category statistics."""
        category_counts = Counter(file.get_category() for file in files)
        return dict(category_counts)