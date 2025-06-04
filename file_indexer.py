import sys
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

def main_menu():
    # Initialize and check for updates
    current_app_version = "0.0.0-dev" # Default to development version
    try:
        import version
        current_app_version = version.__version__
        # Only run updater if a proper version is found (i.e., not in local dev)
        updater = AppUpdater(
            repo_owner="C1ean-dev", 
            repo_name="FileStorageIndexer", 
            current_version=current_app_version
        )
        updater.check_for_updates()
    except ImportError:
        print("Warning: version.py not found. Running in development mode, update checks skipped.")
        # No updater initialized if in development mode

    print("=== INDEXADOR DE ARQUIVOS DE REDE ===\n")
    
    workers = input("Número de threads para processamento (padrão 8): ").strip()
    max_workers = int(workers) if workers.isdigit() else 8
    
    indexer = FileIndexer(max_workers=max_workers)
    
    try:
        while True:
            print("\nOpções:")
            print("1. Escanear pasta de rede (Streaming - muito recomendado)")
            print("2. Escanear pasta de rede (Batch - progresso determinado)")
            print("3. Buscar arquivo")
            print("4. Buscar por extensão") 
            print("5. Mostrar estatísticas")
            print("6. Limpar índice")
            print("7. Escanear apenas pastas")
            print("8. Buscar pasta")
            print("0. Sair")
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                scan_streaming_menu(indexer)
                    
            elif choice == "2":
                scan_batch_menu(indexer)
                            
            elif choice == "3":
                search_file_menu(indexer)
                        
            elif choice == "4":
                search_extension_menu(indexer)
                
            elif choice == "5":
                show_stats_menu(indexer)
                    
            elif choice == "6":
                clear_index_menu(indexer)
                    
            elif choice == "7":
                scan_folders_menu(indexer)
            
            elif choice == "8":
                search_folder_menu(indexer)
                        
            elif choice == "0":
                break
                
    finally:
        indexer.close()

if __name__ == "__main__":
    if sys.stdin.isatty(): # Check if running in an interactive terminal
        main_menu()
    else:
        print("Interactive mode skipped: Not running in a TTY. Please run directly or with a TTY.")
