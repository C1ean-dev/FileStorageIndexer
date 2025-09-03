"""
Shortcut Creator Service Interface

Defines the contract for shortcut creation services.
"""

from abc import ABC, abstractmethod
from typing import Optional


class ShortcutCreator(ABC):
    """
    Interface for shortcut creation services.

    Defines methods for creating desktop shortcuts for the application.
    """

    @abstractmethod
    def create_desktop_shortcut(
        self,
        name: str = "Pesquisa",
        description: Optional[str] = None,
        icon_path: Optional[str] = None
    ) -> bool:
        """
        Create a desktop shortcut for the application.

        Args:
            name: Name of the shortcut (without extension)
            description: Optional description for the shortcut
            icon_path: Optional path to icon file

        Returns:
            True if shortcut was created successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_desktop_path(self) -> str:
        """
        Get the path to the user's desktop directory.

        Returns:
            Path to desktop directory
        """
        pass

    @abstractmethod
    def shortcut_exists(self, name: str = "Pesquisa") -> bool:
        """
        Check if a shortcut with the given name already exists.

        Args:
            name: Name of the shortcut to check

        Returns:
            True if shortcut exists, False otherwise
        """
        pass

    @abstractmethod
    def remove_shortcut(self, name: str = "Pesquisa") -> bool:
        """
        Remove an existing shortcut.

        Args:
            name: Name of the shortcut to remove

        Returns:
            True if shortcut was removed successfully, False otherwise
        """
        pass