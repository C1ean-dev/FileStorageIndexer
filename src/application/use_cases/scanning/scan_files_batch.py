"""
Scan Files Batch Use Case

Use case for scanning files in batch mode with progress bar.
"""

import os
import time
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from src.domain.entities.file_item import FileItem
from src.domain.entities.folder_item import FolderItem
from src.domain.services.file_processor import FileProcessor
from src.domain.exceptions.domain_exceptions import BusinessRuleViolationError
from src.application.interfaces.repositories.file_repository import FileRepository
from src.application.interfaces.external.file_system import FileSystem
from src.application.interfaces.services.logger import Logger
from src.application.interfaces.services.progress_reporter import ProgressReporter
from src.application.dtos.scan_request import ScanRequest


class ScanFilesBatchUseCase:
    """
    Use case for scanning files in batch mode.

    This use case implements file scanning with a determined progress bar,
    collecting all files first and then processing them.
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
        Execute the batch scan operation.

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

            self.logger.info(f"Iniciando escaneamento batch de: {request.path}")

            # Perform the batch scan
            results = self._perform_batch_scan(request)

            execution_time = time.time() - start_time

            # Log completion
            self.logger.info(
                f"Escaneamento batch concluído em {execution_time:.2f}s. "
                f"Arquivos: {results['files_processed']}, "
                f"Pastas: {results['folders_processed']}, "
                f"Erros: {results['errors']}"
            )

            return {
                **results,
                'execution_time': execution_time,
                'scan_mode': 'batch',
                'path': request.path
            }

        except Exception as e:
            self.logger.error(f"Erro durante escaneamento batch: {str(e)}")
            raise

    def _perform_batch_scan(self, request: ScanRequest) -> dict:
        """
        Perform the actual batch scan operation.

        Args:
            request: Scan request parameters

        Returns:
            Dictionary with scan statistics
        """
        # Collect all files first
        self.logger.info("Coletando lista de arquivos...")
        all_files = []
        all_folders = []

        try:
            for dirpath, dirnames, filenames in self.file_system.walk_directory(request.path):
                # Add folder
                if self.file_processor.should_scan_folder(dirpath):
                    all_folders.append(dirpath)

                # Add files
                for filename in filenames:
                    file_path = self.file_system.join_paths(dirpath, filename)

                    # Apply filters
                    if not request.include_hidden and filename.startswith('.'):
                        continue
                    if not request.include_system and filename.startswith(('~', '$')):
                        continue

                    all_files.append(file_path)

                    if (len(all_files) + len(all_folders)) % 10000 == 0:
                        self.logger.info(f"Coletados {len(all_files) + len(all_folders)} itens...")

        except Exception as e:
            self.logger.error(f"Erro ao coletar arquivos: {e}")
            raise

        total_items = len(all_files) + len(all_folders)
        self.logger.info(f"Total de itens encontrados: {total_items}")

        if total_items == 0:
            return {
                'files_processed': 0,
                'folders_processed': 0,
                'errors': 0,
                'success_rate': 0.0
            }

        # Process items with progress bar
        processed_files = 0
        processed_folders = 0
        errors = 0
        batch_size = 100

        # Initialize progress bar
        self.progress_reporter.start(total=total_items, description="Processando arquivos")

        try:
            max_workers = request.max_workers or 8

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                file_batch = []
                folder_batch = []

                # Process folders first
                folder_futures = {
                    executor.submit(self.file_processor.process_folder, folder_path): folder_path
                    for folder_path in all_folders
                }

                for future in as_completed(folder_futures):
                    folder_path = folder_futures[future]
                    try:
                        folder_item = future.result(timeout=30)
                        if folder_item:
                            folder_batch.append(folder_item)
                            processed_folders += 1

                            # Save batch when it reaches batch_size
                            if len(folder_batch) >= batch_size:
                                self._save_folder_batch(folder_batch)
                                folder_batch = []
                    except Exception as e:
                        errors += 1
                        self.logger.error(f"Erro ao processar pasta {folder_path}: {str(e)}")

                    self.progress_reporter.update(1)

                # Process files
                file_futures = {
                    executor.submit(self.file_processor.process_file, file_path): file_path
                    for file_path in all_files
                }

                for future in as_completed(file_futures):
                    file_path = file_futures[future]
                    try:
                        file_item = future.result(timeout=30)
                        if file_item:
                            file_batch.append(file_item)
                            processed_files += 1

                            # Save batch when it reaches batch_size
                            if len(file_batch) >= batch_size:
                                self._save_file_batch(file_batch)
                                file_batch = []
                    except Exception as e:
                        errors += 1
                        self.logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")

                    self.progress_reporter.update(1)

                # Save remaining items
                if file_batch:
                    self._save_file_batch(file_batch)
                if folder_batch:
                    self._save_folder_batch(folder_batch)

        finally:
            self.progress_reporter.finish("Escaneamento concluído")

        return {
            'files_processed': processed_files,
            'folders_processed': processed_folders,
            'errors': errors,
            'success_rate': (processed_files + processed_folders) / max(1, total_items) * 100
        }

    def _save_file_batch(self, files: List[FileItem]) -> None:
        """Save a batch of files to the repository."""
        try:
            self.file_repository.save_files_batch(files)
        except Exception as e:
            self.logger.error(f"Erro ao salvar lote de arquivos: {str(e)}")

    def _save_folder_batch(self, folders: List[FolderItem]) -> None:
        """Save a batch of folders to the repository."""
        try:
            self.file_repository.save_folders_batch(folders)
        except Exception as e:
            self.logger.error(f"Erro ao salvar lote de pastas: {str(e)}")