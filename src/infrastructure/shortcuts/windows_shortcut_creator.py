"""
Windows Shortcut Creator Implementation

Concrete implementation of ShortcutCreator interface for Windows using win32com.
"""

import os
import sys
from typing import Optional

from src.application.interfaces.services.shortcut_creator import ShortcutCreator
from src.application.interfaces.services.logger import Logger


class WindowsShortcutCreator(ShortcutCreator):
    """
    Windows implementation of the ShortcutCreator interface.

    Uses win32com to create desktop shortcuts on Windows systems.
    """

    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialize the Windows shortcut creator.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger
        self._win32com_available = self._check_win32com_availability()

    def _check_win32com_availability(self) -> bool:
        """
        Check if win32com is available.

        Returns:
            True if win32com is available, False otherwise
        """
        try:
            import win32com.client
            return True
        except ImportError:
            if self.logger:
                self.logger.warning("win32com não está disponível. Funcionalidade de atalho limitada.")
            return False

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
        if not self._win32com_available:
            if self.logger:
                self.logger.error("win32com não está disponível. Instale pywin32 para criar atalhos.")
            return False

        try:
            import win32com.client

            # Get paths
            target_path = sys.executable
            working_directory = os.path.dirname(target_path)
            desktop_path = self.get_desktop_path()
            shortcut_path = os.path.join(desktop_path, f"{name}.lnk")

            # Create shortcut
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(shortcut_path)

            # Set shortcut properties
            shortcut.TargetPath = target_path
            shortcut.WorkingDirectory = working_directory

            # Set icon
            if icon_path and os.path.exists(icon_path):
                shortcut.IconLocation = icon_path
            else:
                # Use the executable as icon source
                shortcut.IconLocation = target_path

            # Set description if provided
            if description:
                shortcut.Description = description

            # Save the shortcut
            shortcut.save()

            if self.logger:
                self.logger.info(f"Atalho '{name}.lnk' criado em '{shortcut_path}'")

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro ao criar atalho '{name}': {str(e)}")
            return False

    def get_desktop_path(self) -> str:
        """
        Get the path to the user's desktop directory.

        Returns:
            Path to desktop directory
        """
        try:
            return os.path.join(os.path.expanduser("~"), "Desktop")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro ao obter caminho da área de trabalho: {str(e)}")
            return os.path.expanduser("~")

    def shortcut_exists(self, name: str = "Pesquisa") -> bool:
        """
        Check if a shortcut with the given name already exists.

        Args:
            name: Name of the shortcut to check

        Returns:
            True if shortcut exists, False otherwise
        """
        try:
            desktop_path = self.get_desktop_path()
            shortcut_path = os.path.join(desktop_path, f"{name}.lnk")
            return os.path.exists(shortcut_path)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro ao verificar existência do atalho '{name}': {str(e)}")
            return False

    def remove_shortcut(self, name: str = "Pesquisa") -> bool:
        """
        Remove an existing shortcut.

        Args:
            name: Name of the shortcut to remove

        Returns:
            True if shortcut was removed successfully, False otherwise
        """
        try:
            desktop_path = self.get_desktop_path()
            shortcut_path = os.path.join(desktop_path, f"{name}.lnk")

            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                if self.logger:
                    self.logger.info(f"Atalho '{name}.lnk' removido de '{shortcut_path}'")
                return True
            else:
                if self.logger:
                    self.logger.warning(f"Atalho '{name}.lnk' não encontrado em '{shortcut_path}'")
                return False

        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro ao remover atalho '{name}': {str(e)}")
            return False

    def get_shortcut_info(self, name: str = "Pesquisa") -> Optional[dict]:
        """
        Get information about an existing shortcut.

        Args:
            name: Name of the shortcut

        Returns:
            Dictionary with shortcut information, or None if not found
        """
        if not self._win32com_available:
            return None

        try:
            import win32com.client

            desktop_path = self.get_desktop_path()
            shortcut_path = os.path.join(desktop_path, f"{name}.lnk")

            if not os.path.exists(shortcut_path):
                return None

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(shortcut_path)

            return {
                'name': name,
                'path': shortcut_path,
                'target_path': shortcut.TargetPath,
                'working_directory': shortcut.WorkingDirectory,
                'icon_location': shortcut.IconLocation,
                'description': getattr(shortcut, 'Description', ''),
                'exists': True
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro ao obter informações do atalho '{name}': {str(e)}")
            return None