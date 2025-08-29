"""
SQLite File Repository Implementation

Concrete implementation of FileRepository interface using SQLite.
"""

from typing import List, Optional
from datetime import datetime

from src.domain.entities.file_item import FileItem
from src.domain.entities.folder_item import FolderItem
from src.domain.value_objects.file_path import FilePath
from src.domain.value_objects.file_size import FileSize
from src.domain.value_objects.search_criteria import SearchCriteria
from src.domain.enums.search_type import SearchType
from src.application.interfaces.repositories.file_repository import FileRepository
from src.application.interfaces.services.logger import Logger
from src.infrastructure.database.sqlite.connection_manager import SqliteConnectionManager


class SqliteFileRepository(FileRepository):
    """
    SQLite implementation of the FileRepository interface.
    
    Provides file and folder persistence using SQLite database.
    """
    
    def __init__(self, connection_manager: SqliteConnectionManager, logger: Optional[Logger] = None):
        """
        Initialize the repository.
        
        Args:
            connection_manager: SQLite connection manager
            logger: Optional logger for debugging
        """
        self.connection_manager = connection_manager
        self.logger = logger
    
    def save_file(self, file: FileItem) -> bool:
        """Save a single file to the repository."""
        try:
            sql = """
            INSERT OR REPLACE INTO files (
                filename, full_path, parent_path, file_size, modified_date,
                item_type, extension, category, is_hidden, is_system_file,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            params = (
                file.filename,
                str(file.full_path),
                str(file.parent_path),
                file.size.bytes,
                file.modified_date.isoformat(),
                'file',
                file.extension,
                file.get_category(),
                file.is_hidden(),
                file.is_system_file()
            )
            
            rows_affected = self.connection_manager.execute_command(sql, params)
            
            if self.logger and rows_affected > 0:
                self.logger.debug(f"Saved file: {file.filename}")
            
            return rows_affected > 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save file {file.filename}: {str(e)}")
            return False
    
    def save_files_batch(self, files: List[FileItem]) -> bool:
        """Save multiple files in a batch operation."""
        if not files:
            return True
        
        try:
            sql = """
            INSERT OR REPLACE INTO files (
                filename, full_path, parent_path, file_size, modified_date,
                item_type, extension, category, is_hidden, is_system_file,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            params_list = []
            for file in files:
                params = (
                    file.filename,
                    str(file.full_path),
                    str(file.parent_path),
                    file.size.bytes,
                    file.modified_date.isoformat(),
                    'file',
                    file.extension,
                    file.get_category(),
                    file.is_hidden(),
                    file.is_system_file()
                )
                params_list.append(params)
            
            rows_affected = self.connection_manager.execute_many(sql, params_list)
            
            if self.logger:
                self.logger.debug(f"Saved {len(files)} files in batch")
            
            return rows_affected > 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save file batch: {str(e)}")
            return False
    
    def save_folder(self, folder: FolderItem) -> bool:
        """Save a single folder to the repository."""
        try:
            sql = """
            INSERT OR REPLACE INTO folders (
                folder_name, full_path, parent_path, modified_date,
                depth_level, is_hidden, is_system_folder, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            params = (
                folder.folder_name,
                str(folder.full_path),
                str(folder.parent_path),
                folder.modified_date.isoformat(),
                folder.get_depth_level(),
                folder.is_hidden(),
                folder.is_system_folder()
            )
            
            rows_affected = self.connection_manager.execute_command(sql, params)
            
            if self.logger and rows_affected > 0:
                self.logger.debug(f"Saved folder: {folder.folder_name}")
            
            return rows_affected > 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save folder {folder.folder_name}: {str(e)}")
            return False
    
    def save_folders_batch(self, folders: List[FolderItem]) -> bool:
        """Save multiple folders in a batch operation."""
        if not folders:
            return True
        
        try:
            sql = """
            INSERT OR REPLACE INTO folders (
                folder_name, full_path, parent_path, modified_date,
                depth_level, is_hidden, is_system_folder, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            params_list = []
            for folder in folders:
                params = (
                    folder.folder_name,
                    str(folder.full_path),
                    str(folder.parent_path),
                    folder.modified_date.isoformat(),
                    folder.get_depth_level(),
                    folder.is_hidden(),
                    folder.is_system_folder()
                )
                params_list.append(params)
            
            rows_affected = self.connection_manager.execute_many(sql, params_list)
            
            if self.logger:
                self.logger.debug(f"Saved {len(folders)} folders in batch")
            
            return rows_affected > 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save folder batch: {str(e)}")
            return False
    
    def find_file_by_id(self, file_id: int) -> Optional[FileItem]:
        """Find a file by its ID."""
        try:
            sql = """
            SELECT filename, full_path, file_size, modified_date
            FROM files WHERE id = ? AND item_type = 'file'
            """
            
            results = self.connection_manager.execute_query(sql, (file_id,))
            
            if results:
                row = results[0]
                return self._create_file_item_from_row(row)
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to find file by ID {file_id}: {str(e)}")
            return None
    
    def find_folder_by_id(self, folder_id: int) -> Optional[FolderItem]:
        """Find a folder by its ID."""
        try:
            sql = """
            SELECT folder_name, full_path, modified_date
            FROM folders WHERE id = ?
            """
            
            results = self.connection_manager.execute_query(sql, (folder_id,))
            
            if results:
                row = results[0]
                return self._create_folder_item_from_row(row)
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to find folder by ID {folder_id}: {str(e)}")
            return None
    
    def find_files_by_criteria(self, criteria: SearchCriteria) -> List[FileItem]:
        """Find files matching the search criteria."""
        try:
            if criteria.search_type == SearchType.FILE_NAME:
                return self._find_files_by_name(criteria)
            elif criteria.search_type == SearchType.EXTENSION:
                return self._find_files_by_extension(criteria)
            else:
                return []
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to find files by criteria: {str(e)}")
            return []
    
    def find_folders_by_criteria(self, criteria: SearchCriteria) -> List[FolderItem]:
        """Find folders matching the search criteria."""
        try:
            if criteria.search_type == SearchType.FOLDER_NAME:
                return self._find_folders_by_name(criteria)
            else:
                return []
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to find folders by criteria: {str(e)}")
            return []
    
    def _find_files_by_name(self, criteria: SearchCriteria) -> List[FileItem]:
        """Find files by filename."""
        if criteria.exact_match:
            sql = """
            SELECT filename, full_path, file_size, modified_date
            FROM files WHERE filename = ? AND item_type = 'file'
            ORDER BY filename
            """
            params = (criteria.term,)
        else:
            sql = """
            SELECT filename, full_path, file_size, modified_date
            FROM files WHERE filename LIKE ? AND item_type = 'file'
            ORDER BY filename
            """
            params = (f"%{criteria.term}%",)
        
        results = self.connection_manager.execute_query(sql, params)
        return [self._create_file_item_from_row(row) for row in results]
    
    def _find_files_by_extension(self, criteria: SearchCriteria) -> List[FileItem]:
        """Find files by extension."""
        sql = """
        SELECT filename, full_path, file_size, modified_date
        FROM files WHERE extension = ? AND item_type = 'file'
        ORDER BY filename
        """
        
        results = self.connection_manager.execute_query(sql, (criteria.term,))
        return [self._create_file_item_from_row(row) for row in results]
    
    def _find_folders_by_name(self, criteria: SearchCriteria) -> List[FolderItem]:
        """Find folders by name."""
        if criteria.exact_match:
            sql = """
            SELECT folder_name, full_path, modified_date
            FROM folders WHERE folder_name = ?
            ORDER BY folder_name
            """
            params = (criteria.term,)
        else:
            sql = """
            SELECT folder_name, full_path, modified_date
            FROM folders WHERE folder_name LIKE ?
            ORDER BY folder_name
            """
            params = (f"%{criteria.term}%",)
        
        results = self.connection_manager.execute_query(sql, params)
        return [self._create_folder_item_from_row(row) for row in results]
    
    def get_all_files(self) -> List[FileItem]:
        """Get all files from the repository."""
        try:
            sql = """
            SELECT filename, full_path, file_size, modified_date
            FROM files WHERE item_type = 'file'
            ORDER BY filename
            """
            
            results = self.connection_manager.execute_query(sql)
            return [self._create_file_item_from_row(row) for row in results]
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get all files: {str(e)}")
            return []
    
    def get_all_folders(self) -> List[FolderItem]:
        """Get all folders from the repository."""
        try:
            sql = """
            SELECT folder_name, full_path, modified_date
            FROM folders
            ORDER BY folder_name
            """
            
            results = self.connection_manager.execute_query(sql)
            return [self._create_folder_item_from_row(row) for row in results]
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get all folders: {str(e)}")
            return []
    
    def delete_file(self, file_id: int) -> bool:
        """Delete a file by its ID."""
        try:
            sql = "DELETE FROM files WHERE id = ?"
            rows_affected = self.connection_manager.execute_command(sql, (file_id,))
            return rows_affected > 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to delete file {file_id}: {str(e)}")
            return False
    
    def delete_folder(self, folder_id: int) -> bool:
        """Delete a folder by its ID."""
        try:
            sql = "DELETE FROM folders WHERE id = ?"
            rows_affected = self.connection_manager.execute_command(sql, (folder_id,))
            return rows_affected > 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to delete folder {folder_id}: {str(e)}")
            return False
    
    def delete_all_files(self) -> bool:
        """Delete all files from the repository."""
        try:
            sql = "DELETE FROM files WHERE item_type = 'file'"
            self.connection_manager.execute_command(sql)
            
            if self.logger:
                self.logger.info("Deleted all files from repository")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to delete all files: {str(e)}")
            return False
    
    def delete_all_folders(self) -> bool:
        """Delete all folders from the repository."""
        try:
            sql = "DELETE FROM folders"
            self.connection_manager.execute_command(sql)
            
            if self.logger:
                self.logger.info("Deleted all folders from repository")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to delete all folders: {str(e)}")
            return False
    
    def clear_index(self) -> bool:
        """Clear the entire index (files and folders)."""
        try:
            success = self.delete_all_files() and self.delete_all_folders()
            
            if success and self.logger:
                self.logger.info("Cleared entire index")
            
            return success
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to clear index: {str(e)}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file with the given path exists in the repository."""
        try:
            sql = "SELECT 1 FROM files WHERE full_path = ? AND item_type = 'file' LIMIT 1"
            results = self.connection_manager.execute_query(sql, (file_path,))
            return len(results) > 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to check file existence {file_path}: {str(e)}")
            return False
    
    def folder_exists(self, folder_path: str) -> bool:
        """Check if a folder with the given path exists in the repository."""
        try:
            sql = "SELECT 1 FROM folders WHERE full_path = ? LIMIT 1"
            results = self.connection_manager.execute_query(sql, (folder_path,))
            return len(results) > 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to check folder existence {folder_path}: {str(e)}")
            return False
    
    def update_file(self, file: FileItem) -> bool:
        """Update an existing file in the repository."""
        # For SQLite, INSERT OR REPLACE handles updates
        return self.save_file(file)
    
    def update_folder(self, folder: FolderItem) -> bool:
        """Update an existing folder in the repository."""
        # For SQLite, INSERT OR REPLACE handles updates
        return self.save_folder(folder)
    
    def _create_file_item_from_row(self, row: tuple) -> FileItem:
        """Create a FileItem from a database row."""
        filename, full_path, file_size, modified_date = row
        
        # Parse the modified date
        if isinstance(modified_date, str):
            modified_dt = datetime.fromisoformat(modified_date)
        else:
            modified_dt = modified_date
        
        return FileItem(
            filename=filename,
            full_path=FilePath(full_path),
            size=FileSize(file_size),
            modified_date=modified_dt
        )
    
    def _create_folder_item_from_row(self, row: tuple) -> FolderItem:
        """Create a FolderItem from a database row."""
        folder_name, full_path, modified_date = row
        
        # Parse the modified date
        if isinstance(modified_date, str):
            modified_dt = datetime.fromisoformat(modified_date)
        else:
            modified_dt = modified_date
        
        return FolderItem(
            folder_name=folder_name,
            full_path=FilePath(full_path),
            modified_date=modified_dt
        )