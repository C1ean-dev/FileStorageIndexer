"""
Search Request DTO

Data Transfer Object for search operation requests.
"""

from dataclasses import dataclass
from typing import Optional

from src.domain.enums.search_type import SearchType


@dataclass
class SearchRequest:
    """
    DTO for search operation requests.
    
    Contains all parameters needed to perform a search operation.
    """
    
    term: str
    search_type: SearchType
    exact_match: bool = False
    case_sensitive: bool = False
    limit: Optional[int] = None
    offset: int = 0
    sort_by_relevance: bool = True
    
    def __post_init__(self):
        """Validate the request after initialization."""
        if not self.term or not self.term.strip():
            raise ValueError("Search term cannot be empty")
        
        if self.limit is not None and self.limit < 1:
            raise ValueError("Limit must be at least 1")
        
        if self.offset < 0:
            raise ValueError("Offset cannot be negative")
    
    @property
    def normalized_term(self) -> str:
        """Get the normalized search term."""
        return self.term.strip()
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'term': self.term,
            'search_type': self.search_type.value,
            'exact_match': self.exact_match,
            'case_sensitive': self.case_sensitive,
            'limit': self.limit,
            'offset': self.offset,
            'sort_by_relevance': self.sort_by_relevance
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SearchRequest':
        """Create from dictionary representation."""
        search_type = SearchType(data['search_type'])
        
        return cls(
            term=data['term'],
            search_type=search_type,
            exact_match=data.get('exact_match', False),
            case_sensitive=data.get('case_sensitive', False),
            limit=data.get('limit'),
            offset=data.get('offset', 0),
            sort_by_relevance=data.get('sort_by_relevance', True)
        )
    
    @classmethod
    def for_filename(cls, filename: str, exact_match: bool = False) -> 'SearchRequest':
        """Create a search request for filename search."""
        return cls(
            term=filename,
            search_type=SearchType.FILE_NAME,
            exact_match=exact_match
        )
    
    @classmethod
    def for_extension(cls, extension: str) -> 'SearchRequest':
        """Create a search request for extension search."""
        return cls(
            term=extension,
            search_type=SearchType.EXTENSION,
            exact_match=True
        )
    
    @classmethod
    def for_folder(cls, folder_name: str, exact_match: bool = False) -> 'SearchRequest':
        """Create a search request for folder search."""
        return cls(
            term=folder_name,
            search_type=SearchType.FOLDER_NAME,
            exact_match=exact_match
        )