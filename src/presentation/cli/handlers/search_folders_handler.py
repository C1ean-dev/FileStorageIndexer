"""
Search Folders Handler

Handles folder search operations.
"""

from .base_handler import BaseHandler


class SearchFoldersHandler(BaseHandler):
    """
    Handler for folder search operations.

    Provides functionality to search for folders by name.
    """

    def get_description(self) -> str:
        """Get description of this handler."""
        return "[FIND] Buscar pasta por nome"

    def handle(self, *args, **kwargs) -> None:
        """Handle the search folders operation."""
        self._display_header("[FIND] BUSCAR PASTA POR NOME")
        print("[INFO] Funcionalidade ainda não implementada nesta versão.")

        self._wait_for_user()