"""
File Indexer - Clean Architecture Implementation

Main entry point for the File Indexer application using Clean Architecture.
Refactored with organized CLI handlers for better maintainability.
"""

import sys
import os
from typing import Optional

from src.presentation.config.dependency_injection import get_container, reset_container
from src.presentation.cli.menu_controller import MenuController


class FileIndexerApp:
    """
    Main application class for the File Indexer.

    Refactored to use organized CLI handlers for better maintainability.
    Coordinates the CLI interface with the Clean Architecture implementation.
    """

    def __init__(self, db_path: str = "file_index.db"):
        """
        Initialize the application.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.container = None
        self.menu_controller = None
        self.current_version = "2.0.0-clean-architecture-refactored"

    def run(self) -> None:
        """Run the main application."""
        try:
            with get_container(db_path=self.db_path) as container:
                self.container = container
                self.menu_controller = MenuController(container)
                self._show_welcome_message()
                self._run_main_loop()
        except KeyboardInterrupt:
            print("\n\nAplicação interrompida pelo usuário.")
        except Exception as e:
            print(f"\nErro fatal na aplicação: {str(e)}")
            sys.exit(1)
        finally:
            self._cleanup()

    def _show_welcome_message(self) -> None:
        """Show welcome message and version info."""
        print("=" * 50)
        print("INDEXADOR DE ARQUIVOS DE REDE")
        print("Clean Architecture Implementation")
        print("Refactored CLI Handlers")
        print(f"Versão: {self.current_version}")
        print("=" * 50)
        print()

    def _run_main_loop(self) -> None:
        """Run the main application loop."""
        running = True

        while running:
            self.menu_controller.display_menu()
            choice = input("\nEscolha uma opção: ").strip()
            running = self.menu_controller.handle_choice(choice)

    def _cleanup(self) -> None:
        """Cleanup resources."""
        if self.container:
            try:
                self.container.shutdown()
            except Exception as e:
                print(f"Erro durante limpeza: {e}")


def main():
    """Main entry point."""
    # Check if running in interactive mode
    if not sys.stdin.isatty():
        print("[ERRO] Este programa foi feito para rodar em modo interativo (CLI).")
        sys.exit(1)
    
    # Get database path from environment or use default
    db_path = os.environ.get('FILE_INDEXER_DB_PATH', 'file_index.db')
    
    # Create and run application
    app = FileIndexerApp(db_path=db_path)
    app.run()


if __name__ == "__main__":
    main()