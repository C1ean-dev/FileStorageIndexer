"""
Search Files Use Case

Use case for searching files in the index.
"""

import time
from typing import List

from src.domain.entities.file_item import FileItem
from src.domain.services.search_engine import SearchEngine
from src.domain.value_objects.search_criteria import SearchCriteria
from src.application.interfaces.repositories.file_repository import FileRepository
from src.application.interfaces.services.logger import Logger
from src.application.dtos.search_request import SearchRequest
from src.application.dtos.search_result import SearchResult


class SearchFilesUseCase:
    """
    Use case for searching files in the index.
    
    This use case implements file search functionality with
    relevance scoring and pagination support.
    """
    
    def __init__(
        self,
        file_repository: FileRepository,
        search_engine: SearchEngine,
        logger: Logger
    ):
        """
        Initialize the use case.
        
        Args:
            file_repository: Repository for file access
            search_engine: Domain service for search logic
            logger: Logger interface
        """
        self.file_repository = file_repository
        self.search_engine = search_engine
        self.logger = logger
    
    def execute(self, request: SearchRequest) -> SearchResult:
        """
        Execute the file search operation.
        
        Args:
            request: Search request parameters
            
        Returns:
            SearchResult with matching files and metadata
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Iniciando busca por arquivos: '{request.term}' ({request.search_type.value})")
            
            # Create search criteria from request
            criteria = SearchCriteria(
                term=request.term,
                search_type=request.search_type,
                exact_match=request.exact_match,
                case_sensitive=request.case_sensitive
            )
            
            # Validate search criteria
            self.search_engine.validate_search_criteria(criteria)
            
            # Perform search
            all_files = self.file_repository.find_files_by_criteria(criteria)
            
            # Apply domain-level filtering and sorting
            filtered_files = self.search_engine.filter_files(all_files, criteria)
            
            if request.sort_by_relevance:
                sorted_files = self.search_engine.sort_files_by_relevance(filtered_files, criteria)
            else:
                sorted_files = filtered_files
            
            # Apply pagination
            total_count = len(sorted_files)
            paginated_files = self._apply_pagination(sorted_files, request.offset, request.limit)
            
            execution_time = time.time() - start_time
            
            # Create result
            result = SearchResult.from_files(
                files=paginated_files,
                search_term=request.term,
                execution_time=execution_time,
                total_count=total_count,
                offset=request.offset,
                limit=request.limit
            )
            
            self.logger.info(
                f"Busca concluída em {execution_time*1000:.1f}ms. "
                f"Encontrados {total_count} arquivo(s)"
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erro durante busca: {str(e)}")
            
            # Return empty result on error
            return SearchResult.empty(
                search_term=request.term,
                search_type=request.search_type.value,
                execution_time=execution_time
            )
    
    def get_search_suggestions(self, partial_term: str, search_type) -> List[str]:
        """
        Get search suggestions for partial input.
        
        Args:
            partial_term: Partial search term
            search_type: Type of search
            
        Returns:
            List of suggested search terms
        """
        try:
            return self.search_engine.get_search_suggestions(partial_term, search_type)
        except Exception as e:
            self.logger.error(f"Erro ao obter sugestões: {str(e)}")
            return []
    
    def _apply_pagination(self, files: List[FileItem], offset: int, limit: int = None) -> List[FileItem]:
        """
        Apply pagination to file list.
        
        Args:
            files: List of files to paginate
            offset: Starting index
            limit: Maximum number of items to return
            
        Returns:
            Paginated list of files
        """
        if offset >= len(files):
            return []
        
        end_index = len(files)
        if limit is not None:
            end_index = min(offset + limit, len(files))
        
        return files[offset:end_index]