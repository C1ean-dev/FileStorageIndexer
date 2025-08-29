"""
Check Updates Use Case

Use case for checking and managing application updates.
"""

import requests
from typing import Dict, Optional
from datetime import datetime

from src.application.interfaces.services.logger import Logger
from src.application.interfaces.services.updater import Updater


class CheckUpdatesUseCase:
    """
    Use case for checking application updates.

    This use case handles checking for new versions and managing update operations.
    """

    def __init__(self, updater: Updater, logger: Logger):
        """
        Initialize the use case.

        Args:
            updater: Updater service for version checking
            logger: Logger interface
        """
        self.updater = updater
        self.logger = logger

    def execute(self) -> Dict[str, any]:
        """
        Execute the update check operation.

        Returns:
            Dictionary with update information
        """
        try:
            self.logger.info("Verificando atualizações...")

            # Check for updates
            update_info = self.updater.check_for_updates()

            if update_info.get('update_available', False):
                self.logger.info(f"Nova versão disponível: {update_info.get('latest_version', 'N/A')}")
                return {
                    'status': 'update_available',
                    'current_version': update_info.get('current_version', 'N/A'),
                    'latest_version': update_info.get('latest_version', 'N/A'),
                    'release_notes': update_info.get('release_notes', ''),
                    'download_url': update_info.get('download_url', ''),
                    'message': f"Uma nova versão está disponível: {update_info.get('latest_version', 'N/A')}"
                }
            else:
                self.logger.info("Aplicação está atualizada")
                return {
                    'status': 'up_to_date',
                    'current_version': update_info.get('current_version', 'N/A'),
                    'message': "Sua aplicação está atualizada!"
                }

        except Exception as e:
            error_msg = f"Erro ao verificar atualizações: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg
            }

    def get_current_version(self) -> str:
        """
        Get the current application version.

        Returns:
            Current version string
        """
        try:
            return self.updater.get_current_version()
        except Exception as e:
            self.logger.error(f"Erro ao obter versão atual: {str(e)}")
            return "Desconhecida"

    def get_update_history(self) -> list:
        """
        Get update history.

        Returns:
            List of past updates
        """
        try:
            return self.updater.get_update_history()
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico de atualizações: {str(e)}")
            return []