"""
GitHub Updater Implementation

Concrete implementation of Updater interface using GitHub API.
"""

import requests
from typing import Dict, List, Optional
import json

from src.application.interfaces.services.updater import Updater
from src.application.interfaces.services.logger import Logger


class GitHubUpdater(Updater):
    """
    GitHub-based implementation of the Updater interface.

    Checks for updates using GitHub releases API.
    """

    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        current_version: str,
        logger: Optional[Logger] = None
    ):
        """
        Initialize the GitHub updater.

        Args:
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            current_version: Current application version
            logger: Optional logger instance
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.logger = logger
        self.api_base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

    def check_for_updates(self) -> Dict[str, any]:
        """
        Check for available updates using GitHub API.

        Returns:
            Dictionary with update information
        """
        try:
            if self.logger:
                self.logger.info(f"Verificando atualizações no GitHub: {self.repo_owner}/{self.repo_name}")

            # Get latest release from GitHub API
            response = requests.get(
                f"{self.api_base_url}/releases/latest",
                timeout=10
            )

            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get('tag_name', '').lstrip('v')
                release_notes = release_data.get('body', '')
                download_url = release_data.get('html_url', '')

                # Compare versions (simple string comparison)
                update_available = self._is_newer_version(latest_version, self.current_version)

                return {
                    'update_available': update_available,
                    'current_version': self.current_version,
                    'latest_version': latest_version,
                    'release_notes': release_notes,
                    'download_url': download_url
                }
            else:
                if self.logger:
                    self.logger.warning(f"Falha ao verificar atualizações: HTTP {response.status_code}")
                return {
                    'update_available': False,
                    'current_version': self.current_version,
                    'error': f"HTTP {response.status_code}"
                }

        except requests.RequestException as e:
            if self.logger:
                self.logger.error(f"Erro de rede ao verificar atualizações: {str(e)}")
            return {
                'update_available': False,
                'current_version': self.current_version,
                'error': f"Erro de rede: {str(e)}"
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro inesperado ao verificar atualizações: {str(e)}")
            return {
                'update_available': False,
                'current_version': self.current_version,
                'error': str(e)
            }

    def get_current_version(self) -> str:
        """Get the current application version."""
        return self.current_version

    def get_update_history(self) -> List[Dict[str, any]]:
        """
        Get update history from GitHub releases.

        Returns:
            List of recent releases
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/releases",
                params={'per_page': 10},
                timeout=10
            )

            if response.status_code == 200:
                releases = response.json()
                history = []

                for release in releases:
                    history.append({
                        'version': release.get('tag_name', '').lstrip('v'),
                        'name': release.get('name', ''),
                        'published_at': release.get('published_at', ''),
                        'body': release.get('body', ''),
                        'url': release.get('html_url', '')
                    })

                return history
            else:
                return []

        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro ao obter histórico: {str(e)}")
            return []

    def download_update(self, version: str) -> bool:
        """
        Download a specific update version.

        Note: This is a placeholder implementation.
        In a real scenario, this would download the update file.

        Args:
            version: Version to download

        Returns:
            True if download was successful
        """
        if self.logger:
            self.logger.info(f"Download da versão {version} solicitado")
            self.logger.info("Funcionalidade de download não implementada nesta versão")

        return False

    def install_update(self, version: str) -> bool:
        """
        Install a downloaded update.

        Note: This is a placeholder implementation.
        In a real scenario, this would install the downloaded update.

        Args:
            version: Version to install

        Returns:
            True if installation was successful
        """
        if self.logger:
            self.logger.info(f"Instalação da versão {version} solicitada")
            self.logger.info("Funcionalidade de instalação não implementada nesta versão")

        return False

    def _is_newer_version(self, latest: str, current: str) -> bool:
        """
        Compare two version strings.

        Args:
            latest: Latest version string
            current: Current version string

        Returns:
            True if latest is newer than current
        """
        try:
            # Simple version comparison (works for semantic versioning)
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]

            # Pad shorter version with zeros
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))

            return latest_parts > current_parts

        except (ValueError, AttributeError):
            # Fallback to string comparison if parsing fails
            return latest > current