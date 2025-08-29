"""
Search Files Handler

Handles file search operations by name.
"""

from src.application.dtos.search_request import SearchRequest
from .base_handler import BaseHandler


class SearchFilesHandler(BaseHandler):
    """
    Handler for file search operations.

    Provides search functionality for files by name with exact or partial matching.
    """

    def get_description(self) -> str:
        """Get description of this handler."""
        return "[SEARCH] Buscar arquivo por nome"

    def handle(self, *args, **kwargs) -> None:
        """Handle the file search operation."""
        self._display_header("[SEARCH] BUSCAR ARQUIVO POR NOME")

        # Get search term from user
        search_term = self._get_user_input("Digite o nome do arquivo")
        if not search_term:
            print("[ERRO] Termo de busca não pode estar vazio.")
            self._wait_for_user()
            return

        # Get exact match preference
        exact_match = self._confirm_action("Busca exata?")

        try:
            # Create search request
            request = SearchRequest.for_filename(search_term, exact_match)

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
            print("\nARQUIVOS ENCONTRADOS:")
            for i, file_item in enumerate(result.files[:10], 1):  # Show first 10
                print(f"{i:2d}. {file_item.filename}")
                print(f"    Local: {file_item.full_path}")
                print(f"    Tamanho: {file_item.size}")
                print()

            if len(result.files) > 10:
                print(f"... e mais {len(result.files) - 10} arquivo(s)")

        print(f"{'='*50}")