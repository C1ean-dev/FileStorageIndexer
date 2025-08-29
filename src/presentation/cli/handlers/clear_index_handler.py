"""
Clear Index Handler

Handles index clearing operations.
"""

from .base_handler import BaseHandler


class ClearIndexHandler(BaseHandler):
    """
    Handler for index clearing operations.

    Provides functionality to clear all indexed files and folders.
    """

    def get_description(self) -> str:
        """Get description of this handler."""
        return "[CLEAR] Limpar índice - Remove todos os arquivos e pastas indexados"

    def handle(self, *args, **kwargs) -> None:
        """Handle the clear index operation."""
        self._display_header("[CLEAR] LIMPAR ÍNDICE")
        print("[ATENCAO] Esta operação irá remover TODOS os arquivos e pastas indexados!")

        # Confirm action
        confirm = self._get_user_input("Digite 'CONFIRMAR' para prosseguir")
        if confirm != "CONFIRMAR":
            print("[CANCELADO] Operação cancelada.")
            self._wait_for_user()
            return

        try:
            file_repository = self.container.get_file_repository()
            success = file_repository.clear_index()

            if success:
                print("[SUCESSO] Índice limpo com sucesso!")
            else:
                print("[ERRO] Erro ao limpar índice.")

        except Exception as e:
            print(f"[ERRO] Erro ao limpar índice: {str(e)}")

        self._wait_for_user()