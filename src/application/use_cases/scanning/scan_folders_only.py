"""
Scan Folders Only Use Case

Use case for scanning only folders without files.
"""

import os
import time
import threading
from typing import List, Optional
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from src.domain.entities.folder_item import FolderItem
from src.domain.services.file_processor import FileProcessor
from src.domain.exceptions.domain_exceptions import BusinessRuleViolationError
from src.application.interfaces.repositories.file_repository import FileRepository
from src.application.interfaces.external.file_system import FileSystem
from src.application.interfaces.services.logger import Logger
from src.application.interfaces.services.progress_reporter import ProgressReporter
from src.application.dtos.scan_request import ScanRequest


class ScanFoldersOnlyUseCase:
    """
    Use case for scanning only folders.

    This use case implements folder-only scanning with streaming processing.
    """

    def __init__(
        self,
        file_repository: FileRepository,
        file_system: FileSystem,
        file_processor: FileProcessor,
        logger: Logger,
        progress_reporter: ProgressReporter
    ):
        """
        Initialize the use case.

        Args:
            file_repository: Repository for file persistence
            file_system: File system interface
            file_processor: Domain service for file processing
            logger: Logger interface
            progress_reporter: Progress reporting interface
        """
        self.file_repository = file_repository
        self.file_system = file_system
        self.file_processor = file_processor
        self.logger = logger
        self.progress_reporter = progress_reporter

    def execute(self, request: ScanRequest) -> dict:
        """
        Execute the folders-only scan operation.

        Args:
            request: Scan request parameters

        Returns:
            Dictionary with scan results and statistics

        Raises:
            BusinessRuleViolationError: If scan parameters are invalid
        """
        start_time = time.time()

        try:
            # Validate scan path
            self.file_processor.validate_scan_path(request.path)

            self.logger.info(f"Iniciando escaneamento de pastas: {request.path}")

            # Perform the folders scan
            results = self._perform_folders_scan(request)

            execution_time = time.time() - start_time

            # Log completion
            self.logger.info(
                f"Escaneamento de pastas concluído em {execution_time:.2f}s. "
                f"Pastas: {results['folders_processed']}, "
                f"Erros: {results['errors']}"
            )

            return {
                **results,
                'execution_time': execution_time,
                'scan_mode': 'folders_only',
                'path': request.path
            }

        except Exception as e:
            self.logger.error(f"Erro durante escaneamento de pastas: {str(e)}")
            raise

    def _perform_folders_scan(self, request: ScanRequest) -> dict:
        """
        Perform the actual folders-only scan operation.

        Args:
            request: Scan request parameters

        Returns:
            Dictionary with scan statistics
        """
        processed_folders = 0
        errors = 0
        batch_size = 100

        # Create queues for streaming processing
        folder_queue = Queue(maxsize=1000)

        # Start folder collector thread
        collector_thread = threading.Thread(
            target=self._collect_folders,
            args=(request.path, folder_queue, request),
            daemon=True
        )
        collector_thread.start()

        # Initialize progress bar
        self.progress_reporter.start(description="Processando pastas")

        try:
            max_workers = request.max_workers or 8

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                folder_batch = []

                # Process folders from queue
                while True:
                    try:
                        folder_path = folder_queue.get(timeout=1.0)  # 1 second timeout
                        if folder_path is None:  # End marker
                            break

                        future = executor.submit(self.file_processor.process_folder, folder_path)
                        try:
                            folder_item = future.result(timeout=30)
                            if folder_item:
                                folder_batch.append(folder_item)
                                processed_folders += 1

                                # Save batch when it reaches batch_size
                                if len(folder_batch) >= batch_size:
                                    self._save_folder_batch(folder_batch)
                                    folder_batch = []
                            else:
                                errors += 1

                            self.progress_reporter.update(1)

                        except Exception as e:
                            errors += 1
                            self.logger.error(f"Erro ao processar pasta {folder_path}: {str(e)}")

                        folder_queue.task_done()

                    except:  # Queue empty
                        continue

                # Save remaining folders
                if folder_batch:
                    self._save_folder_batch(folder_batch)

        finally:
            self.progress_reporter.finish("Escaneamento de pastas concluído")

        # Wait for collector thread to finish
        collector_thread.join(timeout=60)

        return {
            'files_processed': 0,  # No files processed in folders-only mode
            'folders_processed': processed_folders,
            'errors': errors,
            'success_rate': processed_folders / max(1, processed_folders + errors) * 100
        }

    def _collect_folders(
        self,
        root_path: str,
        folder_queue: Queue,
        request: ScanRequest
    ) -> None:
        """
        Collect folders from the file system.

        Args:
            root_path: Root path to scan
            folder_queue: Queue for folder paths
            request: Scan request parameters
        """
        try:
            folders_found = 0

            for dirpath, dirnames, filenames in self.file_system.walk_directory(root_path):
                # Add folder to queue if it should be scanned
                if self.file_processor.should_scan_folder(dirpath):
                    folder_queue.put(dirpath)
                    folders_found += 1

                    if folders_found % 1000 == 0:
                        self.logger.debug(f"Coletadas {folders_found} pastas...")

            self.logger.info(f"Coleta de pastas finalizada. Total: {folders_found}")

        except Exception as e:
            self.logger.error(f"Erro durante coleta de pastas: {str(e)}")
        finally:
            # Add end marker
            folder_queue.put(None)

    def _save_folder_batch(self, folders: List[FolderItem]) -> None:
        """Save a batch of folders to the repository."""
        try:
            self.file_repository.save_folders_batch(folders)
        except Exception as e:
            self.logger.error(f"Erro ao salvar lote de pastas: {str(e)}")