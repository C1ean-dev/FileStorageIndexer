"""
Search Type Enumeration

Defines the different types of searches available in the system.
"""

from enum import Enum


class SearchType(Enum):
    """
    Enumeration for different search types.
    
    FILE_NAME: Search by file name
    EXTENSION: Search by file extension
    FOLDER_NAME: Search by folder name
    """
    
    FILE_NAME = "file_name"
    EXTENSION = "extension"
    FOLDER_NAME = "folder_name"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def description(self) -> str:
        """Returns a human-readable description of the search type."""
        descriptions = {
            SearchType.FILE_NAME: "Busca por nome de arquivo",
            SearchType.EXTENSION: "Busca por extensão de arquivo",
            SearchType.FOLDER_NAME: "Busca por nome de pasta"
        }
        return descriptions[self]