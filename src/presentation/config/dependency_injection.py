"""
Dependency Injection Container

Configures and manages all application dependencies following Clean Architecture principles.
"""

import os
from typing import Dict, Any, Optional

# Domain Services
from src.domain.services.file_processor import FileProcessor
from src.domain.services.search_engine import SearchEngine
from src.domain.services.statistics_calculator import StatisticsCalculator

# Application Use Cases
from src.application.use_cases.scanning.scan_files_streaming import ScanFilesStreamingUseCase
from src.application.use_cases.scanning.scan_files_batch import ScanFilesBatchUseCase
from src.application.use_cases.scanning.scan_folders_only import ScanFoldersOnlyUseCase
from src.application.use_cases.searching.search_files import SearchFilesUseCase
from src.application.use_cases.statistics.get_statistics import GetStatisticsUseCase

# Infrastructure Implementations
from src.infrastructure.file_system.os_file_system import OsFileSystem
from src.infrastructure.database.sqlite.connection_manager import SqliteConnectionManager
from src.infrastructure.database.sqlite.schema_manager import SqliteSchemaManager
from src.infrastructure.database.repositories.sqlite_file_repository import SqliteFileRepository
from src.infrastructure.logging.composite_logger import CompositeLogger
from src.infrastructure.logging.console_logger import ConsoleLogger
from src.infrastructure.progress.tqdm_progress_reporter import TqdmProgressReporter


class DIContainer:
    """
    Dependency Injection Container for the File Indexer application.
    
    Manages the creation and lifecycle of all application dependencies
    following Clean Architecture principles.
    """
    
    def __init__(self, db_path: str = "file_index.db", max_workers: Optional[int] = None):
        """
        Initialize the DI container.
        
        Args:
            db_path: Path to the SQLite database file
            max_workers: Maximum number of worker threads (defaults to CPU count - 1)
        """
        self.db_path = db_path
        self.max_workers = max_workers or max(1, os.cpu_count() - 1)
        self._services: Dict[str, Any] = {}
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize all services and dependencies."""
        if self._initialized:
            return
        
        # Initialize infrastructure layer
        self._configure_infrastructure()
        
        # Initialize domain services
        self._configure_domain_services()
        
        # Initialize application layer
        self._configure_application_layer()
        
        # Initialize database schema
        self._initialize_database()
        
        self._initialized = True
    
    def _configure_infrastructure(self) -> None:
        """Configure infrastructure layer dependencies."""
        # File System
        self._services['file_system'] = OsFileSystem()
        
        # Database Connection Manager
        self._services['connection_manager'] = SqliteConnectionManager(
            db_path=self.db_path,
            logger=None  # Will be set after logger is created
        )
        
        # Schema Manager
        self._services['schema_manager'] = SqliteSchemaManager(
            connection_manager=self._services['connection_manager'],
            logger=None  # Will be set after logger is created
        )
        
        # Repositories
        self._services['file_repository'] = SqliteFileRepository(
            connection_manager=self._services['connection_manager'],
            logger=None  # Will be set after logger is created
        )
        
        # Progress Reporter
        self._services['progress_reporter'] = TqdmProgressReporter()
        
        # Logger (composite with console logger)
        console_logger = ConsoleLogger()
        self._services['logger'] = CompositeLogger([console_logger])
        
        # Update logger references
        self._update_logger_references()
    
    def _configure_domain_services(self) -> None:
        """Configure domain layer services."""
        self._services['file_processor'] = FileProcessor()
        self._services['search_engine'] = SearchEngine()
        self._services['statistics_calculator'] = StatisticsCalculator()
    
    def _configure_application_layer(self) -> None:
        """Configure application layer use cases."""
        # Scanning Use Cases
        self._services['scan_files_streaming_use_case'] = ScanFilesStreamingUseCase(
            file_repository=self._services['file_repository'],
            file_system=self._services['file_system'],
            file_processor=self._services['file_processor'],
            logger=self._services['logger'],
            progress_reporter=self._services['progress_reporter']
        )

        self._services['scan_files_batch_use_case'] = ScanFilesBatchUseCase(
            file_repository=self._services['file_repository'],
            file_system=self._services['file_system'],
            file_processor=self._services['file_processor'],
            logger=self._services['logger'],
            progress_reporter=self._services['progress_reporter']
        )

        self._services['scan_folders_only_use_case'] = ScanFoldersOnlyUseCase(
            file_repository=self._services['file_repository'],
            file_system=self._services['file_system'],
            file_processor=self._services['file_processor'],
            logger=self._services['logger'],
            progress_reporter=self._services['progress_reporter']
        )
        
        # Search Use Cases
        self._services['search_files_use_case'] = SearchFilesUseCase(
            file_repository=self._services['file_repository'],
            search_engine=self._services['search_engine'],
            logger=self._services['logger']
        )
        
        # Statistics Use Cases
        self._services['get_statistics_use_case'] = GetStatisticsUseCase(
            file_repository=self._services['file_repository'],
            stats_repository=None,  # TODO: Implement stats repository
            statistics_calculator=self._services['statistics_calculator'],
            logger=self._services['logger']
        )
    
    def _update_logger_references(self) -> None:
        """Update logger references in services that need it."""
        logger = self._services['logger']
        
        # Update connection manager logger
        self._services['connection_manager'].logger = logger
        
        # Update schema manager logger
        self._services['schema_manager'].logger = logger
        
        # Update file repository logger
        self._services['file_repository'].logger = logger
    
    def _initialize_database(self) -> None:
        """Initialize the database schema."""
        schema_manager = self._services['schema_manager']
        schema_manager.initialize_database()
    
    def get(self, service_name: str) -> Any:
        """
        Get a service by name.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            The requested service instance
            
        Raises:
            KeyError: If service is not found
        """
        if not self._initialized:
            self.initialize()
        
        if service_name not in self._services:
            raise KeyError(f"Service '{service_name}' not found")
        
        return self._services[service_name]
    
    def get_file_system(self) -> OsFileSystem:
        """Get the file system service."""
        return self.get('file_system')
    
    def get_file_repository(self) -> SqliteFileRepository:
        """Get the file repository service."""
        return self.get('file_repository')
    
    def get_logger(self) -> CompositeLogger:
        """Get the logger service."""
        return self.get('logger')
    
    def get_progress_reporter(self) -> TqdmProgressReporter:
        """Get the progress reporter service."""
        return self.get('progress_reporter')
    
    def get_file_processor(self) -> FileProcessor:
        """Get the file processor domain service."""
        return self.get('file_processor')
    
    def get_search_engine(self) -> SearchEngine:
        """Get the search engine domain service."""
        return self.get('search_engine')
    
    def get_statistics_calculator(self) -> StatisticsCalculator:
        """Get the statistics calculator domain service."""
        return self.get('statistics_calculator')
    
    def get_scan_files_streaming_use_case(self) -> ScanFilesStreamingUseCase:
        """Get the scan files streaming use case."""
        return self.get('scan_files_streaming_use_case')

    def get_scan_files_batch_use_case(self) -> ScanFilesBatchUseCase:
        """Get the scan files batch use case."""
        return self.get('scan_files_batch_use_case')

    def get_scan_folders_only_use_case(self) -> ScanFoldersOnlyUseCase:
        """Get the scan folders only use case."""
        return self.get('scan_folders_only_use_case')
    
    def get_search_files_use_case(self) -> SearchFilesUseCase:
        """Get the search files use case."""
        return self.get('search_files_use_case')
    
    def get_statistics_use_case(self) -> GetStatisticsUseCase:
        """Get the statistics use case."""
        return self.get('get_statistics_use_case')
    
    def shutdown(self) -> None:
        """Shutdown all services and clean up resources."""
        if not self._initialized:
            return
        
        try:
            # Close progress reporter
            if 'progress_reporter' in self._services:
                self._services['progress_reporter'].close()
            
            # Close logger
            if 'logger' in self._services:
                self._services['logger'].close()
            
            # Close database connections
            if 'connection_manager' in self._services:
                self._services['connection_manager'].close_all_connections()
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
        
        self._services.clear()
        self._initialized = False
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()


# Global container instance
_container: Optional[DIContainer] = None


def get_container(db_path: str = "file_index.db", max_workers: Optional[int] = None) -> DIContainer:
    """
    Get the global DI container instance.
    
    Args:
        db_path: Path to the SQLite database file
        max_workers: Maximum number of worker threads
        
    Returns:
        DIContainer instance
    """
    global _container
    
    if _container is None:
        _container = DIContainer(db_path=db_path, max_workers=max_workers)
    
    return _container


def reset_container() -> None:
    """Reset the global container (useful for testing)."""
    global _container
    
    if _container:
        _container.shutdown()
        _container = None