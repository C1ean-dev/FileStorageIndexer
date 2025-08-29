"""
Updater Service Interface

Defines the contract for update checking and management services.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class Updater(ABC):
    """
    Interface for application update services.

    Defines methods for checking updates, getting version information,
    and managing update operations.
    """

    @abstractmethod
    def check_for_updates(self) -> Dict[str, any]:
        """
        Check for available updates.

        Returns:
            Dictionary containing update information:
            - update_available: bool
            - current_version: str
            - latest_version: str
            - release_notes: str (optional)
            - download_url: str (optional)
        """
        pass

    @abstractmethod
    def get_current_version(self) -> str:
        """
        Get the current application version.

        Returns:
            Current version string
        """
        pass

    @abstractmethod
    def get_update_history(self) -> List[Dict[str, any]]:
        """
        Get the history of past updates.

        Returns:
            List of dictionaries containing update history information
        """
        pass

    @abstractmethod
    def download_update(self, version: str) -> bool:
        """
        Download a specific update version.

        Args:
            version: Version to download

        Returns:
            True if download was successful, False otherwise
        """
        pass

    @abstractmethod
    def install_update(self, version: str) -> bool:
        """
        Install a downloaded update.

        Args:
            version: Version to install

        Returns:
            True if installation was successful, False otherwise
        """
        pass