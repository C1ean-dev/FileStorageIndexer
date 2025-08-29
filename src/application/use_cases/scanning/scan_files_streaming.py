"""
Scan Files Streaming Use Case

Use case for scanning files in streaming mode (low memory usage).
"""

import time
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading

from src.domain.entities.file_item import FileItem
from src.domain.entities.folder_item import FolderItem
from src.domain.services.file_processor import FileProcessor
from src.domain.exceptions.domain_exceptions import BusinessRuleViolationError
from src.application.interfaces.repositories.file_repository import FileRepository
from src.application.interfaces.external.file_system import FileSystem
from src.application.interfaces.services.logger import Logger
from src.application.interfaces.services.progress_reporter import ProgressReporter
from src.application.dtos.scan_request import ScanRequest


class ScanFilesStreamingUseCase:
    """
    Use case for scanning files in streaming mode.
    
    This use case implements file scanning with low memory usage,
    ideal for very large directories.
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
        Execute the streaming scan operation.
        
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
            
            self.logger.info(f"Iniciando escaneamento streaming de: {request.path}")
            
            # Initialize progress reporting
            self.progress_reporter.start(description="Escaneando arquivos")
            
            # Perform the scan
            results = self._perform_streaming_scan(request)
            
            execution_time = time.time() - start_time
            
            # Log completion
            self.logger.info(
                f"Escaneamento concluído em {execution_time:.2f}s. "
                f"Arquivos: {results['files_processed']}, "
                f"Pastas: {results['folders_processed']}, "
                f"Erros: {results['errors']}"
            )
            
            # Finish progress reporting
            self.progress_reporter.finish("Escaneamento concluído")
            
            return {
                **results,
                'execution_time': execution_time,
                'scan_mode': 'streaming',
                'path': request.path
            }
            
        except Exception as e:
            self.logger.error(f"Erro durante escaneamento: {str(e)}")
            self.progress_reporter.finish("Erro no escaneamento")
            raise
    
    def _perform_streaming_scan(self, request: ScanRequest) -> dict:
        """
        Perform the actual streaming scan operation.
        
        Args:
            request: Scan request parameters
            
        Returns:
            Dictionary with scan statistics
        """
        processed_files = 0
        processed_folders = 0
        errors = 0
        batch_size = 100
        
        # Create queues for streaming processing
        file_queue = Queue(maxsize=1000)
        folder_queue = Queue(maxsize=1000)
        
        # Start file collector thread
        collector_thread = threading.Thread(
            target=self._collect_items,
            args=(request.path, file_queue, folder_queue, request),
            daemon=True
        )
        collector_thread.start()
        
        # Process files and folders in parallel
        max_workers = request.max_workers or 8
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            file_batch = []
            folder_batch = []
            
            # Process items from queues
            while True:
                # Process files
                if not file_queue.empty():
                    try:
                        file_path = file_queue.get_nowait()
                        if file_path is None:  # End marker
                            break
                        
                        future = executor.submit(self.file_processor.process_file, file_path)
                        try:
                            file_item = future.result(timeout=30)  # 30 second timeout
                            if file_item:
                                file_batch.append(file_item)
                                processed_files += 1
                                
                                # Save batch when it reaches batch_size
                                if len(file_batch) >= batch_size:
                                    self._save_file_batch(file_batch)
                                    file_batch = []
                                
                                self.progress_reporter.update(1)
                        except Exception as e:
                            errors += 1
                            self.logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
                        
                        file_queue.task_done()
                        
                    except:
                        pass  # Queue empty, continue
                
                # Process folders
                if not folder_queue.empty():
                    try:
                        folder_path = folder_queue.get_nowait()
                        if folder_path is None:  # End marker
                            continue
                        
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
                        except Exception as e:
                            errors += 1
                            self.logger.error(f"Erro ao processar pasta {folder_path}: {str(e)}")
                        
                        folder_queue.task_done()
                        
                    except:
                        pass  # Queue empty, continue
                
                # Small delay to prevent busy waiting
                time.sleep(0.001)
            
            # Save remaining items in batches
            if file_batch:
                self._save_file_batch(file_batch)
            if folder_batch:
                self._save_folder_batch(folder_batch)
        
        # Wait for collector thread to finish
        collector_thread.join(timeout=60)
        
        return {
            'files_processed': processed_files,
            'folders_processed': processed_folders,
            'errors': errors,
            'success_rate': (processed_files + processed_folders) / max(1, processed_files + processed_folders + errors) * 100
        }
    
    def _collect_items(
        self, 
        root_path: str, 
        file_queue: Queue, 
        folder_queue: Queue, 
        request: ScanRequest
    ) -> None:
        """
        Collect files and folders from the file system.
        
        Args:
            root_path: Root path to scan
            file_queue: Queue for file paths
            folder_queue: Queue for folder paths
            request: Scan request parameters
        """
        try:
            items_found = 0
            
            for dirpath, dirnames, filenames in self.file_system.walk_directory(root_path):
                # Add folder to queue
                if self.file_processor.should_scan_folder(dirpath):
                    folder_queue.put(dirpath)
                    items_found += 1
                
                # Add files to queue
                for filename in filenames:
                    file_path = self.file_system.join_paths(dirpath, filename)
                    
                    # Apply filters
                    if not request.include_hidden and filename.startswith('.'):
                        continue
                    if not request.include_system and filename.startswith(('~', '$')):
                        continue
                    
                    file_queue.put(file_path)
                    items_found += 1
                    
                    if items_found % 1000 == 0:
                        self.logger.debug(f"Coletados {items_found} itens...")
            
            self.logger.info(f"Coleta finalizada. Total de itens encontrados: {items_found}")
            
        except Exception as e:
            self.logger.error(f"Erro durante coleta de itens: {str(e)}")
        finally:
            # Add end markers
            file_queue.put(None)
            folder_queue.put(None)
    
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