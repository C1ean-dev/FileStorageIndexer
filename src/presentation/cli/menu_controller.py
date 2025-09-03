"""
Menu Controller

Orchestrates the CLI menu and delegates operations to appropriate handlers.
"""

from typing import Dict, Type

from src.presentation.config.dependency_injection import DIContainer
from .handlers import (
    BaseHandler,
    ScanStreamingHandler,
    ScanBatchHandler,
    SearchFilesHandler,
    SearchExtensionHandler,
    StatisticsHandler,
    ClearIndexHandler,
    ScanFoldersHandler,
    SearchFoldersHandler,
    CheckUpdatesHandler,
    CreateShortcutHandler
)


class MenuController:
    """
    Controller for CLI menu operations.

    Manages the menu display and delegates operations to specific handlers
    based on user selection.
    """

    def __init__(self, container: DIContainer):
        """
        Initialize the menu controller.

        Args:
            container: DI container with all dependencies
        """
        self.container = container
        self.handlers: Dict[str, BaseHandler] = {}
        self._initialize_handlers()

    def _initialize_handlers(self) -> None:
        """Initialize all menu handlers."""
        self.handlers = {
            "1": ScanStreamingHandler(self.container),
            "2": ScanBatchHandler(self.container),
            "3": SearchFilesHandler(self.container),
            "4": SearchExtensionHandler(self.container),
            "5": StatisticsHandler(self.container),
            "6": ClearIndexHandler(self.container),
            "7": ScanFoldersHandler(self.container),
            "8": SearchFoldersHandler(self.container),
            "9": CheckUpdatesHandler(self.container),
            "10": CreateShortcutHandler(self.container),
        }

    def display_menu(self) -> None:
        """Display the main menu."""
        menu = """
MENU PRINCIPAL:
   1. [STREAMING] Escanear pasta (Modo recomendado)
   2. [BATCH] Escanear pasta (Com barra de progresso)
   3. [SEARCH] Buscar arquivo por nome
   4. [FILTER] Buscar por extensão
   5. [STATS] Mostrar estatísticas
   6. [CLEAR] Limpar índice
   7. [FOLDERS] Escanear apenas pastas
   8. [FIND] Buscar pasta por nome
   9. [UPDATE] Verificar atualizações
  10. [SHORTCUT] Criar atalho na área de trabalho
   0. [EXIT] Sair
        """
        print(menu)

    def handle_choice(self, choice: str) -> bool:
        """
        Handle user menu choice.

        Args:
            choice: User's menu selection

        Returns:
            True if should continue, False if should exit
        """
        if choice == "0":
            print("\nSaindo do indexador de arquivos...")
            return False

        handler = self.handlers.get(choice)
        if handler:
            try:
                handler.handle()
            except Exception as e:
                print(f"[ERRO] Erro ao executar operação: {str(e)}")
                input("\nPressione Enter para continuar...")
        else:
            print("[ERRO] Opção inválida. Por favor, escolha uma opção válida.")
            input("\nPressione Enter para continuar...")

        return True

    def get_handler_description(self, choice: str) -> str:
        """
        Get description for a menu choice.

        Args:
            choice: Menu choice

        Returns:
            Handler description or empty string
        """
        handler = self.handlers.get(choice)
        return handler.get_description() if handler else ""