"""
File Repository Interface

Defines the contract for file persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.file_item import FileItem
from src.domain.entities.folder_item import FolderItem
from src.domain.value_objects.search_criteria import SearchCriteria


class FileRepository(ABC):
    """
    Abstract interface for file repository operations.
    
    This interface defines the contract that infrastructure implementations
    must follow for file and folder persistence.
    """
    
    @abstractmethod
    def save_file(self, file: FileItem) -> bool:
        """
        Save a single file to the repository.
        
        Args:
            file: FileItem to save
            
        Returns:
            True if save was successful
        """
        pass
    
    @abstractmethod
    def save_files_batch(self, files: List[FileItem]) -> bool:
        """
        Save multiple files in a batch operation.
        
        Args:
            files: List of FileItem objects to save
            
        Returns:
            True if batch save was successful
        """
        pass
    
    @abstractmethod
    def save_folder(self, folder: FolderItem) -> bool:
        """
        Save a single folder to the repository.
        
        Args:
            folder: FolderItem to save
            
        Returns:
            True if save was successful
        """
        pass
    
    @abstractmethod
    def save_folders_batch(self, folders: List[FolderItem]) -> bool:
        """
        Save multiple folders in a batch operation.
        
        Args:
            folders: List of FolderItem objects to save
            
        Returns:
            True if batch save was successful
        """
        pass
    
    @abstractmethod
    def find_file_by_id(self, file_id: int) -> Optional[FileItem]:
        """
        Find a file by its ID.
        
        Args:
            file_id: The file ID to search for
            
        Returns:
            FileItem if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_folder_by_id(self, folder_id: int) -> Optional[FolderItem]:
        """
        Find a folder by its ID.
        
        Args:
            folder_id: The folder ID to search for
            
        Returns:
            FolderItem if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_files_by_criteria(self, criteria: SearchCriteria) -> List[FileItem]:
        """
        Find files matching the search criteria.
        
        Args:
            criteria: Search criteria to match
            
        Returns:
            List of matching FileItem objects
        """
        pass
    
    @abstractmethod
    def find_folders_by_criteria(self, criteria: SearchCriteria) -> List[FolderItem]:
        """
        Find folders matching the search criteria.
        
        Args:
            criteria: Search criteria to match
            
        Returns:
            List of matching FolderItem objects
        """
        pass
    
    @abstractmethod
    def get_all_files(self) -> List[FileItem]:
        """
        Get all files from the repository.
        
        Returns:
            List of all FileItem objects
        """
        pass
    
    @abstractmethod
    def get_all_folders(self) -> List[FolderItem]:
        """
        Get all folders from the repository.
        
        Returns:
            List of all FolderItem objects
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_id: int) -> bool:
        """
        Delete a file by its ID.
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            True if deletion was successful
        """
        pass
    
    @abstractmethod
    def delete_folder(self, folder_id: int) -> bool:
        """
        Delete a folder by its ID.
        
        Args:
            folder_id: ID of the folder to delete
            
        Returns:
            True if deletion was successful
        """
        pass
    
    @abstractmethod
    def delete_all_files(self) -> bool:
        """
        Delete all files from the repository.
        
        Returns:
            True if deletion was successful
        """
        pass
    
    @abstractmethod
    def delete_all_folders(self) -> bool:
        """
        Delete all folders from the repository.
        
        Returns:
            True if deletion was successful
        """
        pass
    
    @abstractmethod
    def clear_index(self) -> bool:
        """
        Clear the entire index (files and folders).
        
        Returns:
            True if clearing was successful
        """
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file with the given path exists in the repository.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists in repository
        """
        pass
    
    @abstractmethod
    def folder_exists(self, folder_path: str) -> bool:
        """
        Check if a folder with the given path exists in the repository.
        
        Args:
            folder_path: Path to check
            
        Returns:
            True if folder exists in repository
        """
        pass
    
    @abstractmethod
    def update_file(self, file: FileItem) -> bool:
        """
        Update an existing file in the repository.
        
        Args:
            file: FileItem with updated information
            
        Returns:
            True if update was successful
        """
        pass
    
    @abstractmethod
    def update_folder(self, folder: FolderItem) -> bool:
        """
        Update an existing folder in the repository.
        
        Args:
            folder: FolderItem with updated information
            
        Returns:
            True if update was successful
        """
        pass