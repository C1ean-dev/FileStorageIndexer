"""
Create Shortcut Use Case

Use case for creating desktop shortcuts for the application.
"""

from typing import Optional

from src.application.interfaces.services.shortcut_creator import ShortcutCreator
from src.application.interfaces.services.logger import Logger


class CreateShortcutUseCase:
    """
    Use case for creating desktop shortcuts.

    This use case handles the creation of desktop shortcuts for the application,
    providing a clean interface for shortcut management.
    """

    def __init__(self, shortcut_creator: ShortcutCreator, logger: Logger):
        """
        Initialize the use case.

        Args:
            shortcut_creator: Shortcut creation service
            logger: Logger interface
        """
        self.shortcut_creator = shortcut_creator
        self.logger = logger

    def execute(
        self,
        name: str = "Pesquisa",
        description: Optional[str] = None,
        icon_path: Optional[str] = None,
        force: bool = False
    ) -> dict:
        """
        Execute the shortcut creation operation.

        Args:
            name: Name of the shortcut
            description: Optional description
            icon_path: Optional path to icon file
            force: If True, overwrite existing shortcut

        Returns:
            Dictionary with operation result
        """
        try:
            self.logger.info(f"Criando atalho '{name}' na área de trabalho...")

            # Check if shortcut already exists
            if self.shortcut_creator.shortcut_exists(name) and not force:
                return {
                    'status': 'already_exists',
                    'message': f"Atalho '{name}' já existe na área de trabalho.",
                    'shortcut_name': name,
                    'desktop_path': self.shortcut_creator.get_desktop_path()
                }

            # Create the shortcut
            success = self.shortcut_creator.create_desktop_shortcut(
                name=name,
                description=description,
                icon_path=icon_path
            )

            if success:
                self.logger.info(f"Atalho '{name}' criado com sucesso")
                return {
                    'status': 'created',
                    'message': f"Atalho '{name}' criado com sucesso na área de trabalho!",
                    'shortcut_name': name,
                    'desktop_path': self.shortcut_creator.get_desktop_path()
                }
            else:
                error_msg = f"Falha ao criar atalho '{name}'"
                self.logger.error(error_msg)
                return {
                    'status': 'error',
                    'message': error_msg,
                    'shortcut_name': name
                }

        except Exception as e:
            error_msg = f"Erro ao criar atalho: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'shortcut_name': name
            }

    def remove_shortcut(self, name: str = "Pesquisa") -> dict:
        """
        Remove an existing shortcut.

        Args:
            name: Name of the shortcut to remove

        Returns:
            Dictionary with operation result
        """
        try:
            self.logger.info(f"Removendo atalho '{name}' da área de trabalho...")

            if not self.shortcut_creator.shortcut_exists(name):
                return {
                    'status': 'not_found',
                    'message': f"Atalho '{name}' não encontrado na área de trabalho.",
                    'shortcut_name': name
                }

            success = self.shortcut_creator.remove_shortcut(name)

            if success:
                self.logger.info(f"Atalho '{name}' removido com sucesso")
                return {
                    'status': 'removed',
                    'message': f"Atalho '{name}' removido com sucesso!",
                    'shortcut_name': name
                }
            else:
                error_msg = f"Falha ao remover atalho '{name}'"
                self.logger.error(error_msg)
                return {
                    'status': 'error',
                    'message': error_msg,
                    'shortcut_name': name
                }

        except Exception as e:
            error_msg = f"Erro ao remover atalho: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'shortcut_name': name
            }

    def check_shortcut_status(self, name: str = "Pesquisa") -> dict:
        """
        Check if a shortcut exists and get its information.

        Args:
            name: Name of the shortcut to check

        Returns:
            Dictionary with shortcut status information
        """
        try:
            exists = self.shortcut_creator.shortcut_exists(name)
            desktop_path = self.shortcut_creator.get_desktop_path()

            if exists:
                return {
                    'status': 'exists',
                    'message': f"Atalho '{name}' encontrado na área de trabalho.",
                    'shortcut_name': name,
                    'desktop_path': desktop_path,
                    'exists': True
                }
            else:
                return {
                    'status': 'not_found',
                    'message': f"Atalho '{name}' não encontrado na área de trabalho.",
                    'shortcut_name': name,
                    'desktop_path': desktop_path,
                    'exists': False
                }

        except Exception as e:
            error_msg = f"Erro ao verificar status do atalho: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'shortcut_name': name,
                'exists': False
            }