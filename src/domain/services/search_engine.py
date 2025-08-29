"""
Search Engine Domain Service

Contains business logic for searching files and folders.
"""

from typing import List, Callable
import re

from ..entities.file_item import FileItem
from ..entities.folder_item import FolderItem
from ..value_objects.search_criteria import SearchCriteria
from ..enums.search_type import SearchType
from ..exceptions.domain_exceptions import BusinessRuleViolationError


class SearchEngine:
    """
    Domain service for searching files and folders.
    
    Contains business logic for different types of searches and filtering.
    """
    
    def __init__(self):
        """Initialize the SearchEngine."""
        pass
    
    def matches_criteria(self, item: FileItem, criteria: SearchCriteria) -> bool:
        """
        Check if a file item matches the search criteria.
        
        Args:
            item: FileItem to check
            criteria: Search criteria to match against
            
        Returns:
            True if item matches criteria
        """
        if criteria.search_type == SearchType.FILE_NAME:
            return self._matches_filename(item, criteria)
        elif criteria.search_type == SearchType.EXTENSION:
            return self._matches_extension(item, criteria)
        else:
            return False
    
    def matches_folder_criteria(self, folder: FolderItem, criteria: SearchCriteria) -> bool:
        """
        Check if a folder item matches the search criteria.
        
        Args:
            folder: FolderItem to check
            criteria: Search criteria to match against
            
        Returns:
            True if folder matches criteria
        """
        if criteria.search_type == SearchType.FOLDER_NAME:
            return self._matches_folder_name(folder, criteria)
        else:
            return False
    
    def filter_files(self, files: List[FileItem], criteria: SearchCriteria) -> List[FileItem]:
        """
        Filter a list of files based on search criteria.
        
        Args:
            files: List of FileItem objects to filter
            criteria: Search criteria to apply
            
        Returns:
            Filtered list of FileItem objects
        """
        return [file for file in files if self.matches_criteria(file, criteria)]
    
    def filter_folders(self, folders: List[FolderItem], criteria: SearchCriteria) -> List[FolderItem]:
        """
        Filter a list of folders based on search criteria.
        
        Args:
            folders: List of FolderItem objects to filter
            criteria: Search criteria to apply
            
        Returns:
            Filtered list of FolderItem objects
        """
        return [folder for folder in folders if self.matches_folder_criteria(folder, criteria)]
    
    def sort_files_by_relevance(self, files: List[FileItem], criteria: SearchCriteria) -> List[FileItem]:
        """
        Sort files by relevance to search criteria.
        
        Args:
            files: List of FileItem objects to sort
            criteria: Search criteria used for relevance scoring
            
        Returns:
            Sorted list with most relevant files first
        """
        def relevance_score(file: FileItem) -> float:
            return self._calculate_file_relevance(file, criteria)
        
        return sorted(files, key=relevance_score, reverse=True)
    
    def sort_folders_by_relevance(self, folders: List[FolderItem], criteria: SearchCriteria) -> List[FolderItem]:
        """
        Sort folders by relevance to search criteria.
        
        Args:
            folders: List of FolderItem objects to sort
            criteria: Search criteria used for relevance scoring
            
        Returns:
            Sorted list with most relevant folders first
        """
        def relevance_score(folder: FolderItem) -> float:
            return self._calculate_folder_relevance(folder, criteria)
        
        return sorted(folders, key=relevance_score, reverse=True)
    
    def create_search_filter(self, criteria: SearchCriteria) -> Callable[[FileItem], bool]:
        """
        Create a filter function for the given search criteria.
        
        Args:
            criteria: Search criteria to create filter for
            
        Returns:
            Filter function that takes FileItem and returns bool
        """
        def filter_func(item: FileItem) -> bool:
            return self.matches_criteria(item, criteria)
        
        return filter_func
    
    def validate_search_criteria(self, criteria: SearchCriteria) -> None:
        """
        Validate search criteria according to business rules.
        
        Args:
            criteria: Search criteria to validate
            
        Raises:
            BusinessRuleViolationError: If criteria violates business rules
        """
        # Check minimum search term length
        if len(criteria.term.strip()) < 1:
            raise BusinessRuleViolationError(
                "Termo de busca muito curto",
                "O termo de busca deve ter pelo menos 1 caractere"
            )
        
        # Check maximum search term length
        if len(criteria.term) > 100:
            raise BusinessRuleViolationError(
                "Termo de busca muito longo",
                "O termo de busca não pode ter mais de 100 caracteres"
            )
        
        # Validate extension format
        if criteria.search_type == SearchType.EXTENSION:
            if not criteria.term.startswith('.'):
                raise BusinessRuleViolationError(
                    "Formato de extensão inválido",
                    "Extensões devem começar com ponto (ex: .pdf)"
                )
            
            if len(criteria.term) > 10:
                raise BusinessRuleViolationError(
                    "Extensão muito longa",
                    "Extensões não podem ter mais de 10 caracteres"
                )
    
    def get_search_suggestions(self, partial_term: str, search_type: SearchType) -> List[str]:
        """
        Get search suggestions based on partial input.
        
        This is a business rule for improving user experience.
        
        Args:
            partial_term: Partial search term
            search_type: Type of search
            
        Returns:
            List of suggested search terms
        """
        suggestions = []
        
        if search_type == SearchType.EXTENSION:
            # Common file extensions
            common_extensions = [
                '.pdf', '.doc', '.docx', '.txt', '.xlsx', '.ppt',
                '.jpg', '.png', '.gif', '.mp4', '.mp3', '.zip'
            ]
            
            partial_lower = partial_term.lower()
            if not partial_lower.startswith('.'):
                partial_lower = '.' + partial_lower
            
            suggestions = [ext for ext in common_extensions if ext.startswith(partial_lower)]
        
        elif search_type == SearchType.FILE_NAME:
            # Common file name patterns
            if partial_term.lower() in ['doc', 'document']:
                suggestions = ['documento', 'documentos', 'doc', 'docs']
            elif partial_term.lower() in ['img', 'image']:
                suggestions = ['imagem', 'imagens', 'foto', 'fotos']
            elif partial_term.lower() in ['vid', 'video']:
                suggestions = ['video', 'videos', 'filme', 'filmes']
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _matches_filename(self, item: FileItem, criteria: SearchCriteria) -> bool:
        """Check if file matches filename criteria."""
        target = item.filename
        if not criteria.case_sensitive:
            target = target.lower()
        
        return criteria.matches(target)
    
    def _matches_extension(self, item: FileItem, criteria: SearchCriteria) -> bool:
        """Check if file matches extension criteria."""
        target = item.extension
        if not criteria.case_sensitive:
            target = target.lower()
        
        return criteria.matches(target)
    
    def _matches_folder_name(self, folder: FolderItem, criteria: SearchCriteria) -> bool:
        """Check if folder matches folder name criteria."""
        target = folder.folder_name
        if not criteria.case_sensitive:
            target = target.lower()
        
        return criteria.matches(target)
    
    def _calculate_file_relevance(self, file: FileItem, criteria: SearchCriteria) -> float:
        """
        Calculate relevance score for a file.
        
        Higher scores indicate better matches.
        """
        score = 0.0
        
        if criteria.search_type == SearchType.FILE_NAME:
            # Exact match gets highest score
            if criteria.exact_match and criteria.matches(file.filename):
                score += 100.0
            elif criteria.matches(file.filename):
                # Partial match - score based on how much of the filename matches
                term_length = len(criteria.term)
                filename_length = len(file.filename)
                score += (term_length / filename_length) * 50.0
                
                # Bonus for match at beginning of filename
                if file.filename.lower().startswith(criteria.term.lower()):
                    score += 25.0
        
        elif criteria.search_type == SearchType.EXTENSION:
            # Extension matches are binary - either match or don't
            if criteria.matches(file.extension):
                score += 100.0
        
        # Bonus for common file types
        if file.get_category() in ['document', 'image']:
            score += 5.0
        
        # Penalty for very large files (might be less relevant)
        if file.is_large(500):  # > 500MB
            score -= 10.0
        
        return score
    
    def _calculate_folder_relevance(self, folder: FolderItem, criteria: SearchCriteria) -> float:
        """
        Calculate relevance score for a folder.
        
        Higher scores indicate better matches.
        """
        score = 0.0
        
        if criteria.search_type == SearchType.FOLDER_NAME:
            # Exact match gets highest score
            if criteria.exact_match and criteria.matches(folder.folder_name):
                score += 100.0
            elif criteria.matches(folder.folder_name):
                # Partial match - score based on how much of the folder name matches
                term_length = len(criteria.term)
                folder_length = len(folder.folder_name)
                score += (term_length / folder_length) * 50.0
                
                # Bonus for match at beginning of folder name
                if folder.folder_name.lower().startswith(criteria.term.lower()):
                    score += 25.0
        
        # Bonus for folders at reasonable depth (not too deep)
        depth = folder.get_depth_level()
        if 1 <= depth <= 3:
            score += 10.0
        elif depth > 5:
            score -= 5.0
        
        return score