"""
Scan Streaming Handler

Handles the streaming scan operation for large directories.
"""

from src.application.dtos.scan_request import ScanRequest
from src.domain.enums.scan_mode import ScanMode
from .base_handler import BaseHandler


class ScanStreamingHandler(BaseHandler):
    """
    Handler for streaming scan operations.

    Provides optimized scanning for large volumes of data with low memory usage.
    """

    def get_description(self) -> str:
        """Get description of this handler."""
        return "[STREAMING] Escaneamento otimizado para grandes volumes de dados"

    def handle(self, *args, **kwargs) -> None:
        """Handle the streaming scan operation."""
        self._display_header("[STREAMING] ESCANEAMENTO")
        print("Modo otimizado para grandes volumes de dados com baixo uso de memória.")

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
                scan_mode=ScanMode.STREAMING,
                update_existing=False
            )

            # Execute scan
            use_case = self.container.get_scan_files_streaming_use_case()
            result = use_case.execute(request)

            # Display results
            self._display_scan_results(result)

        except Exception as e:
            print(f"[ERRO] Erro durante escaneamento: {str(e)}")

        self._wait_for_user()

    def _display_scan_results(self, result: dict) -> None:
        """Display scan operation results."""
        print(f"\n{'='*50}")
        print("RESULTADOS DO ESCANEAMENTO")
        print(f"{'='*50}")
        print(f"Arquivos processados: {result.get('files_processed', 0):,}")
        print(f"Pastas processadas: {result.get('folders_processed', 0):,}")
        print(f"Erros: {result.get('errors', 0):,}")
        print(f"Tempo de execução: {result.get('execution_time', 0):.2f}s")
        print(f"Taxa de sucesso: {result.get('success_rate', 0):.1f}%")
        print(f"Modo: {result.get('scan_mode', 'unknown')}")
        print(f"{'='*50}")