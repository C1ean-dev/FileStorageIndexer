"""
CLI Handlers Package

This package contains handlers for different CLI menu options.
Each handler encapsulates the logic for a specific menu operation.
"""

from .base_handler import BaseHandler
from .scan_streaming_handler import ScanStreamingHandler
from .scan_batch_handler import ScanBatchHandler
from .search_files_handler import SearchFilesHandler
from .search_extension_handler import SearchExtensionHandler
from .statistics_handler import StatisticsHandler
from .clear_index_handler import ClearIndexHandler
from .scan_folders_handler import ScanFoldersHandler
from .search_folders_handler import SearchFoldersHandler

__all__ = [
    'BaseHandler',
    'ScanStreamingHandler',
    'ScanBatchHandler',
    'SearchFilesHandler',
    'SearchExtensionHandler',
    'StatisticsHandler',
    'ClearIndexHandler',
    'ScanFoldersHandler',
    'SearchFoldersHandler'
]