

from ..enums.search_type import SearchType
from ..exceptions.validation_errors import EmptyValueError, ValidationError


class SearchCriteria:

    def __init__(
        self, 
        term: str, 
        search_type: SearchType, 
        exact_match: bool = False,
        case_sensitive: bool = False
    ):
        """
        Initialize SearchCriteria.
        
        Args:
            term: The search term
            search_type: Type of search to perform
            exact_match: Whether to perform exact matching
            case_sensitive: Whether search is case sensitive
            
        Raises:
            EmptyValueError: If term is empty
            ValidationError: If search_type is invalid
        """
        if not term or not term.strip():
            raise EmptyValueError("search_term")
        
        if not isinstance(search_type, SearchType):
            raise ValidationError(f"search_type deve ser uma instância de SearchType, recebido: {type(search_type)}")
        
        self._original_term = term
        self._search_type = search_type
        self._exact_match = exact_match
        self._case_sensitive = case_sensitive
        self._normalized_term = self._normalize_term(term, case_sensitive)
    
    def _normalize_term(self, term: str, case_sensitive: bool) -> str:
        """Normalize the search term."""
        normalized = term.strip()
        
        if not case_sensitive:
            normalized = normalized.lower()
        
        if self._search_type == SearchType.EXTENSION and not normalized.startswith('.'):
            normalized = f".{normalized}"
        
        return normalized
    
    @property
    def term(self) -> str:
        """Get the normalized search term."""
        return self._normalized_term
    
    @property
    def original_term(self) -> str:
        """Get the original search term."""
        return self._original_term
    
    @property
    def search_type(self) -> SearchType:
        """Get the search type."""
        return self._search_type
    
    @property
    def exact_match(self) -> bool:
        """Check if exact matching is enabled."""
        return self._exact_match
    
    @property
    def case_sensitive(self) -> bool:
        """Check if search is case sensitive."""
        return self._case_sensitive
    
    def matches(self, target: str) -> bool:
        """
        Check if the target matches this search criteria.
        
        Args:
            target: The target string to match against
            
        Returns:
            True if target matches the criteria
        """
        if not target:
            return False
        
        # Normalize target for comparison
        normalized_target = target if self._case_sensitive else target.lower()
        
        if self._exact_match:
            return normalized_target == self._normalized_term
        else:
            return self._normalized_term in normalized_target
    
    def get_sql_pattern(self) -> str:
        """
        Get SQL LIKE pattern for database queries.
        
        Returns:
            SQL pattern string for LIKE queries
        """
        if self._exact_match:
            return self._normalized_term
        else:
            return f"%{self._normalized_term}%"
    
    @classmethod
    def for_filename(
        cls, 
        filename: str, 
        exact_match: bool = False, 
        case_sensitive: bool = False
    ) -> 'SearchCriteria':
        """Create search criteria for filename search."""
        return cls(filename, SearchType.FILE_NAME, exact_match, case_sensitive)
    
    @classmethod
    def for_extension(cls, extension: str, case_sensitive: bool = False) -> 'SearchCriteria':
        """Create search criteria for extension search."""
        return cls(extension, SearchType.EXTENSION, True, case_sensitive)
    
    @classmethod
    def for_folder(
        cls, 
        folder_name: str, 
        exact_match: bool = False, 
        case_sensitive: bool = False
    ) -> 'SearchCriteria':
        """Create search criteria for folder search."""
        return cls(folder_name, SearchType.FOLDER_NAME, exact_match, case_sensitive)
    
    def __str__(self) -> str:
        match_type = "exata" if self._exact_match else "parcial"
        case_type = "sensível" if self._case_sensitive else "insensível"
        return f"SearchCriteria('{self._normalized_term}', {self._search_type.value}, {match_type}, {case_type})"
    
    def __repr__(self) -> str:
        return (f"SearchCriteria(term='{self._original_term}', "
                f"search_type={self._search_type}, "
                f"exact_match={self._exact_match}, "
                f"case_sensitive={self._case_sensitive})")
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, SearchCriteria):
            return False
        return (
            self._normalized_term == other._normalized_term and
            self._search_type == other._search_type and
            self._exact_match == other._exact_match and
            self._case_sensitive == other._case_sensitive
        )
    
    def __hash__(self) -> int:
        return hash((
            self._normalized_term,
            self._search_type,
            self._exact_match,
            self._case_sensitive
        ))