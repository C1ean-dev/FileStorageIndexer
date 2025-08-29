"""
File Processor Domain Service

Contains business logic for processing files and extracting metadata.
"""

import os
from datetime import datetime
from typing import Optional, Tuple

from ..entities.file_item import FileItem
from ..entities.folder_item import FolderItem
from ..value_objects.file_path import FilePath
from ..value_objects.file_size import FileSize
from ..exceptions.domain_exceptions import FileValidationError, BusinessRuleViolationError


class FileProcessor:
    """
    Domain service for processing files and folders.
    
    Contains business logic for extracting metadata and validating files.
    """
    
    def __init__(self):
        """Initialize the FileProcessor."""
        pass
    
    def process_file(self, file_path: str) -> Optional[FileItem]:
        """
        Process a single file and create a FileItem entity.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            FileItem if file should be processed, None otherwise
            
        Raises:
            FileValidationError: If file processing fails
        """
        try:
            # Create FilePath value object
            path_obj = FilePath(file_path)
            
            # Check if file exists
            if not path_obj.exists() or not path_obj.is_file():
                return None
            
            # Extract metadata
            filename = path_obj.name
            size_bytes, modified_date = self._extract_file_metadata(file_path)
            
            # Create value objects
            size = FileSize(size_bytes)
            
            # Create FileItem entity
            file_item = FileItem(
                filename=filename,
                full_path=path_obj,
                size=size,
                modified_date=modified_date
            )
            
            # Apply business rules
            if not file_item.should_be_indexed():
                return None
            
            return file_item
            
        except Exception as e:
            raise FileValidationError(
                file_path,
                f"Erro ao processar arquivo: {str(e)}"
            )
    
    def process_folder(self, folder_path: str) -> Optional[FolderItem]:
        """
        Process a single folder and create a FolderItem entity.
        
        Args:
            folder_path: Path to the folder to process
            
        Returns:
            FolderItem if folder should be processed, None otherwise
            
        Raises:
            FileValidationError: If folder processing fails
        """
        try:
            # Create FilePath value object
            path_obj = FilePath(folder_path)
            
            # Check if folder exists
            if not path_obj.exists() or not path_obj.is_dir():
                return None
            
            # Extract metadata
            folder_name = path_obj.name
            modified_date = self._extract_folder_metadata(folder_path)
            
            # Create FolderItem entity
            folder_item = FolderItem(
                folder_name=folder_name,
                full_path=path_obj,
                modified_date=modified_date
            )
            
            # Apply business rules
            if not folder_item.should_be_indexed():
                return None
            
            return folder_item
            
        except Exception as e:
            raise FileValidationError(
                folder_path,
                f"Erro ao processar pasta: {str(e)}"
            )
    
    def should_scan_folder(self, folder_path: str) -> bool:
        """
        Determine if a folder should be scanned for files.
        
        This applies business rules to decide whether to recurse into a folder.
        
        Args:
            folder_path: Path to the folder
            
        Returns:
            True if folder should be scanned
        """
        try:
            folder_item = self.process_folder(folder_path)
            if folder_item is None:
                return False
            
            return folder_item.should_be_scanned()
            
        except Exception:
            # If we can't process the folder, don't scan it
            return False
    
    def validate_scan_path(self, scan_path: str) -> None:
        """
        Validate that a path is suitable for scanning.
        
        Args:
            scan_path: Path to validate
            
        Raises:
            BusinessRuleViolationError: If path violates business rules
        """
        try:
            path_obj = FilePath(scan_path)
        except Exception as e:
            raise BusinessRuleViolationError(
                "Caminho inválido",
                f"Caminho '{scan_path}' é inválido: {str(e)}"
            )
        
        # Check if path exists
        if not path_obj.exists():
            raise BusinessRuleViolationError(
                "Caminho não existe",
                f"O caminho '{scan_path}' não existe"
            )
        
        # Check if it's a directory
        if not path_obj.is_dir():
            raise BusinessRuleViolationError(
                "Não é um diretório",
                f"O caminho '{scan_path}' não é um diretório"
            )
        
        # Check if we have permission to read
        if not os.access(scan_path, os.R_OK):
            raise BusinessRuleViolationError(
                "Sem permissão de leitura",
                f"Sem permissão para ler o diretório '{scan_path}'"
            )
    
    def calculate_processing_priority(self, file_path: str) -> int:
        """
        Calculate processing priority for a file.
        
        Higher priority files are processed first.
        This is a business rule that can be customized.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Priority score (higher = more priority)
        """
        try:
            path_obj = FilePath(file_path)
            
            # Base priority
            priority = 100
            
            # Prioritize certain file types
            extension = path_obj.suffix.lower()
            
            # High priority for documents
            if extension in {'.pdf', '.doc', '.docx', '.txt'}:
                priority += 50
            
            # Medium priority for media files
            elif extension in {'.jpg', '.png', '.mp4', '.mp3'}:
                priority += 20
            
            # Lower priority for system files
            elif extension in {'.tmp', '.log', '.cache'}:
                priority -= 30
            
            # Prioritize smaller files (process faster)
            try:
                size_bytes, _ = self._extract_file_metadata(file_path)
                if size_bytes < 1024 * 1024:  # < 1MB
                    priority += 10
                elif size_bytes > 100 * 1024 * 1024:  # > 100MB
                    priority -= 20
            except:
                pass
            
            return max(0, priority)
            
        except Exception:
            return 0  # Lowest priority if we can't analyze
    
    def _extract_file_metadata(self, file_path: str) -> Tuple[int, datetime]:
        """
        Extract file metadata from the filesystem.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (size_bytes, modified_date)
        """
        try:
            stat = os.stat(file_path)
            size_bytes = stat.st_size
            modified_timestamp = stat.st_mtime
            modified_date = datetime.fromtimestamp(modified_timestamp)
            
            return size_bytes, modified_date
            
        except OSError as e:
            raise FileValidationError(
                file_path,
                f"Erro ao obter metadados do arquivo: {str(e)}"
            )
    
    def _extract_folder_metadata(self, folder_path: str) -> datetime:
        """
        Extract folder metadata from the filesystem.
        
        Args:
            folder_path: Path to the folder
            
        Returns:
            Modified date
        """
        try:
            stat = os.stat(folder_path)
            modified_timestamp = stat.st_mtime
            return datetime.fromtimestamp(modified_timestamp)
            
        except OSError as e:
            raise FileValidationError(
                folder_path,
                f"Erro ao obter metadados da pasta: {str(e)}"
            )