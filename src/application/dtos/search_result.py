"""
Search Result DTO

Data Transfer Object for search operation results.
"""

from dataclasses import dataclass
from typing import List, Union, Optional
from datetime import datetime

from src.domain.entities.file_item import FileItem
from src.domain.entities.folder_item import FolderItem


@dataclass
class SearchResult:
    """
    DTO for search operation results.
    
    Contains the results of a search operation with metadata.
    """
    
    items: List[Union[FileItem, FolderItem]]
    total_count: int
    execution_time: float
    search_term: str
    search_type: str
    has_more: bool = False
    offset: int = 0
    limit: Optional[int] = None
    
    def __post_init__(self):
        """Validate the result after initialization."""
        if self.total_count < 0:
            raise ValueError("Total count cannot be negative")
        
        if self.execution_time < 0:
            raise ValueError("Execution time cannot be negative")
        
        if len(self.items) > self.total_count:
            raise ValueError("Items count cannot exceed total count")
    
    @property
    def files(self) -> List[FileItem]:
        """Get only file items from results."""
        return [item for item in self.items if isinstance(item, FileItem)]
    
    @property
    def folders(self) -> List[FolderItem]:
        """Get only folder items from results."""
        return [item for item in self.items if isinstance(item, FolderItem)]
    
    @property
    def file_count(self) -> int:
        """Get count of file items."""
        return len(self.files)
    
    @property
    def folder_count(self) -> int:
        """Get count of folder items."""
        return len(self.folders)
    
    @property
    def is_empty(self) -> bool:
        """Check if result is empty."""
        return len(self.items) == 0
    
    @property
    def execution_time_ms(self) -> float:
        """Get execution time in milliseconds."""
        return self.execution_time * 1000
    
    def get_page_info(self) -> dict:
        """Get pagination information."""
        return {
            'offset': self.offset,
            'limit': self.limit,
            'current_count': len(self.items),
            'total_count': self.total_count,
            'has_more': self.has_more,
            'has_previous': self.offset > 0
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'items': [item.to_dict() for item in self.items],
            'total_count': self.total_count,
            'file_count': self.file_count,
            'folder_count': self.folder_count,
            'execution_time': self.execution_time,
            'execution_time_ms': self.execution_time_ms,
            'search_term': self.search_term,
            'search_type': self.search_type,
            'pagination': self.get_page_info(),
            'is_empty': self.is_empty
        }
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the results."""
        if self.is_empty:
            return f"Nenhum resultado encontrado para '{self.search_term}'"
        
        summary_parts = []
        
        if self.file_count > 0:
            summary_parts.append(f"{self.file_count} arquivo(s)")
        
        if self.folder_count > 0:
            summary_parts.append(f"{self.folder_count} pasta(s)")
        
        items_text = " e ".join(summary_parts)
        
        time_text = f"{self.execution_time_ms:.1f}ms"
        
        result = f"Encontrados {items_text} para '{self.search_term}' em {time_text}"
        
        if self.has_more:
            result += f" (mostrando {len(self.items)} de {self.total_count})"
        
        return result
    
    @classmethod
    def empty(cls, search_term: str, search_type: str, execution_time: float = 0.0) -> 'SearchResult':
        """Create an empty search result."""
        return cls(
            items=[],
            total_count=0,
            execution_time=execution_time,
            search_term=search_term,
            search_type=search_type
        )
    
    @classmethod
    def from_files(
        cls, 
        files: List[FileItem], 
        search_term: str, 
        execution_time: float,
        total_count: Optional[int] = None,
        offset: int = 0,
        limit: Optional[int] = None
    ) -> 'SearchResult':
        """Create search result from file list."""
        if total_count is None:
            total_count = len(files)
        
        has_more = limit is not None and (offset + len(files)) < total_count
        
        return cls(
            items=files,
            total_count=total_count,
            execution_time=execution_time,
            search_term=search_term,
            search_type="file",
            has_more=has_more,
            offset=offset,
            limit=limit
        )
    
    @classmethod
    def from_folders(
        cls, 
        folders: List[FolderItem], 
        search_term: str, 
        execution_time: float,
        total_count: Optional[int] = None,
        offset: int = 0,
        limit: Optional[int] = None
    ) -> 'SearchResult':
        """Create search result from folder list."""
        if total_count is None:
            total_count = len(folders)
        
        has_more = limit is not None and (offset + len(folders)) < total_count
        
        return cls(
            items=folders,
            total_count=total_count,
            execution_time=execution_time,
            search_term=search_term,
            search_type="folder",
            has_more=has_more,
            offset=offset,
            limit=limit
        )