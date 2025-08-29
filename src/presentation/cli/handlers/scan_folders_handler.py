"""
Scan Folders Handler

Handles folder-only scanning operations.
"""

from src.application.dtos.scan_request import ScanRequest
from src.domain.enums.scan_mode import ScanMode
from .base_handler import BaseHandler


class ScanFoldersHandler(BaseHandler):
    """
    Handler for folder-only scanning operations.

    Provides functionality to scan only folders without files.
    """

    def get_description(self) -> str:
        """Get description of this handler."""
        return "[FOLDERS] Escanear apenas pastas"

    def handle(self, *args, **kwargs) -> None:
        """Handle the scan folders operation."""
        self._display_header("[FOLDERS] ESCANEAR APENAS PASTAS")
        print("Modo otimizado para indexação apenas de pastas.")

        # Get scan path from user
        path = self._get_user_input("Digite o caminho da pasta")
        if not path:
            print("[ERRO] Caminho não pode estar vazio.")
            self._wait_for_user()
            return

        try:
            # Create scan request
            request = ScanRequest(
                path=path,
                scan_mode=ScanMode.FOLDERS_ONLY,
                update_existing=False
            )

            # Execute scan
            use_case = self.container.get_scan_folders_only_use_case()
            result = use_case.execute(request)

            # Display results
            self._display_scan_results(result)

        except Exception as e:
            print(f"[ERRO] Erro durante escaneamento de pastas: {str(e)}")

        self._wait_for_user()

    def _display_scan_results(self, result: dict) -> None:
        """Display scan operation results."""
        print(f"\n{'='*50}")
        print("RESULTADOS DO ESCANEAMENTO DE PASTAS")
        print(f"{'='*50}")
        print(f"Arquivos processados: {result.get('files_processed', 0):,}")
        print(f"Pastas processadas: {result.get('folders_processed', 0):,}")
        print(f"Erros: {result.get('errors', 0):,}")
        print(f"Tempo de execução: {result.get('execution_time', 0):.2f}s")
        print(f"Taxa de sucesso: {result.get('success_rate', 0):.1f}%")
        print(f"Modo: {result.get('scan_mode', 'unknown')}")
        print(f"{'='*50}")