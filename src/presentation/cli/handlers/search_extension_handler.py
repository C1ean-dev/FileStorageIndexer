"""
Search Extension Handler

Handles file search operations by extension.
"""

from src.application.dtos.search_request import SearchRequest
from .base_handler import BaseHandler


class SearchExtensionHandler(BaseHandler):
    """
    Handler for extension search operations.

    Provides search functionality for files by extension.
    """

    def get_description(self) -> str:
        """Get description of this handler."""
        return "[FILTER] Buscar por extensão"

    def handle(self, *args, **kwargs) -> None:
        """Handle the extension search operation."""
        self._display_header("[FILTER] BUSCAR POR EXTENSÃO")

        # Get extension from user
        extension = self._get_user_input("Digite a extensão (ex: .pdf, .txt)")
        if not extension:
            print("[ERRO] Extensão não pode estar vazia.")
            self._wait_for_user()
            return

        try:
            # Create search request
            request = SearchRequest.for_extension(extension)

            # Execute search
            use_case = self.container.get_search_files_use_case()
            result = use_case.execute(request)

            # Display results
            self._display_search_results(result)

        except Exception as e:
            print(f"[ERRO] Erro durante busca: {str(e)}")

        self._wait_for_user()

    def _display_search_results(self, result) -> None:
        """Display search operation results."""
        print(f"\n{'='*50}")
        print("RESULTADOS DA BUSCA")
        print(f"{'='*50}")
        print(result.get_summary())
        print(f"{'='*50}")

        if not result.is_empty:
            print("\n📋 ARQUIVOS ENCONTRADOS:")
            for i, file_item in enumerate(result.files[:10], 1):  # Show first 10
                print(f"{i:2d}. 📄 {file_item.filename}")
                print(f"    📍 {file_item.full_path}")
                print(f"    📏 {file_item.size}")
                print()

            if len(result.files) > 10:
                print(f"... e mais {len(result.files) - 10} arquivo(s)")

        print(f"{'='*50}")