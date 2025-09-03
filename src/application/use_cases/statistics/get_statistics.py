"""
Get Statistics Use Case

Use case for retrieving index statistics.
"""

import time

from src.domain.entities.index_stats import IndexStats
from src.domain.services.statistics_calculator import StatisticsCalculator
from src.application.interfaces.repositories.file_repository import FileRepository
from src.application.interfaces.services.logger import Logger


class GetStatisticsUseCase:
    """
    Use case for retrieving comprehensive index statistics.
    
    This use case calculates and returns statistics about the indexed files and folders.
    """
    
    def __init__(
        self,
        file_repository: FileRepository,
        statistics_calculator: StatisticsCalculator,
        logger: Logger
    ):
        """
        Initialize the use case.

        Args:
            file_repository: Repository for file access
            statistics_calculator: Domain service for statistics calculation
            logger: Logger interface
        """
        self.file_repository = file_repository
        self.statistics_calculator = statistics_calculator
        self.logger = logger
    
    def execute(self, use_cache: bool = True) -> IndexStats:
        """
        Execute the statistics retrieval operation.
        
        Args:
            use_cache: Whether to use cached statistics if available
            
        Returns:
            IndexStats entity with comprehensive statistics
        """
        start_time = time.time()
        
        try:
            self.logger.info("Calculando estatísticas do índice...")
            
            # Calculate fresh statistics (cache not implemented yet)
            all_files = self.file_repository.get_all_files()
            all_folders = self.file_repository.get_all_folders()
            
            stats = self.statistics_calculator.calculate_index_stats(all_files, all_folders)
            
            execution_time = time.time() - start_time
            
            self.logger.info(
                f"Estatísticas calculadas em {execution_time*1000:.1f}ms. "
                f"Arquivos: {stats.total_files}, Pastas: {stats.total_folders}"
            )
            
            return stats
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erro ao calcular estatísticas: {str(e)}")
            
            # Return empty stats on error
            return IndexStats()
    
    def get_health_metrics(self) -> dict:
        """
        Get health metrics for the index.
        
        Returns:
            Dictionary with health metrics and recommendations
        """
        try:
            self.logger.info("Calculando métricas de saúde do índice...")
            
            all_files = self.file_repository.get_all_files()
            all_folders = self.file_repository.get_all_folders()
            
            health_metrics = self.statistics_calculator.calculate_indexing_health(all_files, all_folders)
            
            self.logger.info(f"Saúde do índice: {health_metrics['status']} ({health_metrics['health_score']}%)")
            
            return health_metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular métricas de saúde: {str(e)}")
            return {
                'health_score': 0.0,
                'status': 'error',
                'recommendations': ['Erro ao calcular métricas de saúde']
            }
    
    def get_storage_analysis(self) -> dict:
        """
        Get storage waste analysis.
        
        Returns:
            Dictionary with storage waste information
        """
        try:
            self.logger.info("Analisando desperdício de armazenamento...")
            
            all_files = self.file_repository.get_all_files()
            
            waste_analysis = self.statistics_calculator.calculate_storage_waste(all_files)
            
            self.logger.info(
                f"Análise de armazenamento: {waste_analysis['empty_files_count']} arquivos vazios, "
                f"{waste_analysis['hidden_files_count']} arquivos ocultos"
            )
            
            return waste_analysis
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar armazenamento: {str(e)}")
            return {
                'empty_files_count': 0,
                'hidden_files_count': 0,
                'system_files_count': 0,
                'total_waste_potential': 0
            }
    
    def refresh_statistics_cache(self) -> bool:
        """
        Refresh the statistics cache.

        Returns:
            True if cache refresh was successful (not implemented yet)
        """
        # TODO: Implement cache functionality
        self.logger.info("Cache de estatísticas não implementado ainda")
        return False