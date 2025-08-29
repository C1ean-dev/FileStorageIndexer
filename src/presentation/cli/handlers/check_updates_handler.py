"""
Check Updates Handler

Handles the update checking operation.
"""

from src.application.dtos.scan_request import ScanRequest
from .base_handler import BaseHandler


class CheckUpdatesHandler(BaseHandler):
    """
    Handler for checking application updates.

    Provides functionality to check for new versions and display update information.
    """

    def get_description(self) -> str:
        """Get description of this handler."""
        return "[UPDATE] Verificar atualizações"

    def handle(self, *args, **kwargs) -> None:
        """Handle the check updates operation."""
        self._display_header("[UPDATE] VERIFICAR ATUALIZAÇÕES")
        print("Verificando se há novas versões disponíveis...")

        try:
            # Get the check updates use case
            use_case = self.container.get_check_updates_use_case()
            result = use_case.execute()

            # Display results
            self._display_update_results(result)

        except Exception as e:
            print(f"[ERRO] Erro ao verificar atualizações: {str(e)}")

        self._wait_for_user()

    def _display_update_results(self, result: dict) -> None:
        """Display update check results."""
        print(f"\n{'='*50}")
        print("RESULTADOS DA VERIFICAÇÃO DE ATUALIZAÇÕES")
        print(f"{'='*50}")

        status = result.get('status', 'unknown')

        if status == 'update_available':
            print("🎉 UMA NOVA VERSÃO ESTÁ DISPONÍVEL!")
            print(f"📦 Versão atual: {result.get('current_version', 'N/A')}")
            print(f"✨ Nova versão: {result.get('latest_version', 'N/A')}")
            print(f"📝 Notas da versão: {result.get('release_notes', 'N/A')[:200]}...")

            if result.get('download_url'):
                print(f"🔗 Link para download: {result.get('download_url')}")

            print("\n💡 Recomendação: Baixe a nova versão para obter as últimas melhorias!")

        elif status == 'up_to_date':
            print("✅ SUA APLICAÇÃO ESTÁ ATUALIZADA!")
            print(f"📦 Versão atual: {result.get('current_version', 'N/A')}")
            print("\n💡 Você já possui a versão mais recente.")

        elif status == 'error':
            print("❌ ERRO AO VERIFICAR ATUALIZAÇÕES")
            print(f"📝 Detalhes: {result.get('message', 'Erro desconhecido')}")

        else:
            print("❓ STATUS DESCONHECIDO")
            print(f"📝 Mensagem: {result.get('message', 'Status não identificado')}")

        print(f"{'='*50}")

    def _show_update_history(self) -> None:
        """Show update history."""
        try:
            use_case = self.container.get_check_updates_use_case()
            history = use_case.get_update_history()

            if history:
                print(f"\n📚 HISTÓRICO DE VERSÕES:")
                print(f"{'='*30}")

                for i, update in enumerate(history[:5], 1):  # Show last 5 updates
                    print(f"{i}. Versão: {update.get('version', 'N/A')}")
                    print(f"   Data: {update.get('published_at', 'N/A')[:10]}")
                    print(f"   Nome: {update.get('name', 'N/A')}")
                    print()

                if len(history) > 5:
                    print(f"... e mais {len(history) - 5} versões")
            else:
                print("\n📝 Nenhum histórico de versões encontrado.")

        except Exception as e:
            print(f"[ERRO] Erro ao obter histórico: {str(e)}")