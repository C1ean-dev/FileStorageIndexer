"""
Statistics Handler

Handles statistics display operations.
"""

from .base_handler import BaseHandler


class StatisticsHandler(BaseHandler):
    """
    Handler for statistics display operations.

    Shows comprehensive statistics about the indexed files and folders.
    """

    def get_description(self) -> str:
        """Get description of this handler."""
        return "[STATS] Mostrar estatísticas do índice"

    def handle(self, *args, **kwargs) -> None:
        """Handle the statistics display operation."""
        self._display_header("[STATS] ESTATÍSTICAS DO ÍNDICE")

        try:
            use_case = self.container.get_statistics_use_case()
            stats = use_case.execute()

            print(f"\n{'='*50}")
            print(stats.get_summary_text())
            print(f"{'='*50}")

        except Exception as e:
            print(f"[ERRO] Erro ao obter estatísticas: {str(e)}")

        self._wait_for_user()