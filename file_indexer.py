import sys
import os
from core.indexer import FileIndexer
from utils.updateRelease.updater import AppUpdater
from modules.scan_streaming import scan_streaming_menu
from modules.scan_batch import scan_batch_menu
from modules.search_file import search_file_menu
from modules.search_extension import search_extension_menu
from modules.show_stats import show_stats_menu
from modules.clear_index import clear_index_menu
from modules.scan_folders import scan_folders_menu
from modules.search_folder import search_folder_menu
from modules.display_menu import display_menu

def main_menu():
    print("=== INDEXADOR DE ARQUIVOS DE REDE ===\n")

    current_app_version = "0.0.0-dev"
    try:
        import version
        current_app_version = version.__version__
        updater = AppUpdater(
            repo_owner="C1ean-dev",
            repo_name="FileStorageIndexer",
            current_version=current_app_version
        )
        updater.check_for_updates()
    except ImportError:
        print("Aviso: O arquivo 'version.py' não foi encontrado. Rodando em modo de desenvolvimento, verificações de atualização puladas.")
    except Exception as e:
        print(f"Erro ao verificar atualizações: {e}")

    max_workers = os.cpu_count() - 1
    indexer = FileIndexer(max_workers=max_workers)

    running = True
    try:
        while running:
            display_menu()
            choices = {
                "1": lambda: scan_streaming_menu(indexer),
                "2": lambda: scan_batch_menu(indexer),
                "3": lambda: search_file_menu(indexer),
                "4": lambda: search_extension_menu(indexer),
                "5": lambda: show_stats_menu(indexer),
                "6": lambda: clear_index_menu(indexer),
                "7": lambda: scan_folders_menu(indexer),
                "8": lambda: search_folder_menu(indexer),
                "0": lambda: False
            }
            choice = input("\nEscolha uma opção: ").strip()
            if choice in choices:
                if choice == "0":
                    running = False
                else:
                    choices[choice]()
            else:
                print("Opção inválida. Por favor, escolha uma opção válida.")
    finally:
        print("Saindo do indexador de arquivos. Fechando conexão com o banco de dados...")
        indexer.close()

if __name__ == "__main__":
    if sys.stdin.isatty():
        main_menu()
    else:
        print("o programa foi feito para rodar CLI.")
