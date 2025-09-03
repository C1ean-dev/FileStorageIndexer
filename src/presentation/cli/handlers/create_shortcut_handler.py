"""
Create Shortcut Handler

Handles the shortcut creation operation.
"""

from src.application.dtos.scan_request import ScanRequest
from .base_handler import BaseHandler


class CreateShortcutHandler(BaseHandler):
    """
    Handler for creating desktop shortcuts.

    Provides functionality to create, remove, and check desktop shortcuts
    for the application.
    """

    def get_description(self) -> str:
        """Get description of this handler."""
        return "[SHORTCUT] Criar atalho na área de trabalho"

    def handle(self, *args, **kwargs) -> None:
        """Handle the create shortcut operation."""
        self._display_header("[SHORTCUT] CRIAR ATALHO NA ÁREA DE TRABALHO")
        print("Esta opção cria um atalho na área de trabalho para facilitar o acesso.")

        # Show current status
        self._show_shortcut_status()

        # Ask user what to do
        print("\nOpções:")
        print("1. Criar atalho")
        print("2. Remover atalho existente")
        print("3. Verificar status do atalho")
        print("0. Voltar ao menu principal")

        choice = input("\nEscolha uma opção: ").strip()

        try:
            if choice == "1":
                self._handle_create_shortcut()
            elif choice == "2":
                self._handle_remove_shortcut()
            elif choice == "3":
                self._handle_check_status()
            elif choice == "0":
                return
            else:
                print("[ERRO] Opção inválida.")

        except Exception as e:
            print(f"[ERRO] Erro na operação: {str(e)}")

        self._wait_for_user()

    def _handle_create_shortcut(self) -> None:
        """Handle shortcut creation."""
        print("\n[CRIAR ATALHO]")
        print("Criando atalho 'Pesquisa' na área de trabalho...")

        try:
            # Get the create shortcut use case
            use_case = self.container.get_create_shortcut_use_case()
            result = use_case.execute(name="Pesquisa", force=False)

            # Display results
            self._display_shortcut_result(result)

        except Exception as e:
            print(f"[ERRO] Erro ao criar atalho: {str(e)}")

    def _handle_remove_shortcut(self) -> None:
        """Handle shortcut removal."""
        print("\n[REMOVER ATALHO]")
        print("Removendo atalho 'Pesquisa' da área de trabalho...")

        try:
            # Get the create shortcut use case
            use_case = self.container.get_create_shortcut_use_case()
            result = use_case.remove_shortcut(name="Pesquisa")

            # Display results
            self._display_shortcut_result(result)

        except Exception as e:
            print(f"[ERRO] Erro ao remover atalho: {str(e)}")

    def _handle_check_status(self) -> None:
        """Handle shortcut status check."""
        print("\n[VERIFICAR STATUS]")
        self._show_shortcut_status()

    def _show_shortcut_status(self) -> None:
        """Show current shortcut status."""
        try:
            use_case = self.container.get_create_shortcut_use_case()
            result = use_case.check_shortcut_status(name="Pesquisa")

            print(f"\n{'='*50}")
            print("STATUS DO ATALHO")
            print(f"{'='*50}")

            if result.get('status') == 'exists':
                print("✅ ATALHO ENCONTRADO")
                print(f"📁 Localização: {result.get('desktop_path', 'N/A')}")
                print(f"📄 Nome: Pesquisa.lnk")
            elif result.get('status') == 'not_found':
                print("❌ ATALHO NÃO ENCONTRADO")
                print(f"📁 Área de trabalho: {result.get('desktop_path', 'N/A')}")
            else:
                print("❓ STATUS DESCONHECIDO")
                print(f"📝 Mensagem: {result.get('message', 'Status não identificado')}")

            print(f"{'='*50}")

        except Exception as e:
            print(f"[ERRO] Erro ao verificar status: {str(e)}")

    def _display_shortcut_result(self, result: dict) -> None:
        """Display shortcut operation results."""
        print(f"\n{'='*50}")
        print("RESULTADO DA OPERAÇÃO")
        print(f"{'='*50}")

        status = result.get('status', 'unknown')

        if status == 'created':
            print("✅ ATALHO CRIADO COM SUCESSO!")
            print(f"📁 Localização: {result.get('desktop_path', 'N/A')}")
            print(f"📄 Nome: {result.get('shortcut_name', 'Pesquisa')}.lnk")
            print("\n💡 Dicas:")
            print("   • Clique com o botão direito no atalho")
            print("   • Selecione 'Fixar na Barra de Tarefas'")
            print("   • Ou 'Fixar no Menu Iniciar'")

        elif status == 'removed':
            print("✅ ATALHO REMOVIDO COM SUCESSO!")
            print(f"📄 Nome: {result.get('shortcut_name', 'Pesquisa')}.lnk")

        elif status == 'already_exists':
            print("ℹ️ ATALHO JÁ EXISTE")
            print(f"📁 Localização: {result.get('desktop_path', 'N/A')}")
            print(f"📄 Nome: {result.get('shortcut_name', 'Pesquisa')}.lnk")
            print("\n💡 O atalho já está disponível na área de trabalho.")

        elif status == 'not_found':
            print("ℹ️ ATALHO NÃO ENCONTRADO")
            print(f"📄 Nome: {result.get('shortcut_name', 'Pesquisa')}.lnk")
            print("   O atalho não existe na área de trabalho.")

        elif status == 'error':
            print("❌ ERRO NA OPERAÇÃO")
            print(f"📝 Detalhes: {result.get('message', 'Erro desconhecido')}")
            print(f"📄 Nome: {result.get('shortcut_name', 'Pesquisa')}")

        else:
            print("❓ RESULTADO DESCONHECIDO")
            print(f"📝 Mensagem: {result.get('message', 'Resultado não identificado')}")

        print(f"{'='*50}")