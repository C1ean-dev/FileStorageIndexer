import os
from core.indexer import FileIndexer

def search_folder_menu(indexer: FileIndexer):
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'
    """Handles the 'Search Folder' menu option."""
    while True:
        search_term = input("Digite o nome da pasta (ou '0' para voltar): ").strip()
        if search_term == '0':
            print("Voltando ao menu principal...")
            break # Exit the loop

        if search_term:
            results = indexer.search_folders(search_term)
            if results:
                if len(results) == 1:
                    folder_name, full_path, parent_path = results[0]
                    print(f"{GREEN}Abrindo pasta encontrada: \"{full_path}\"{RESET}")
                    try:
                        os.startfile(full_path)
                    except OSError as e:
                        print(f"{RED}Erro ao abrir a pasta: {e}{RESET}")
                else:
                    print(f"\nEncontradas {len(results)} pasta(s):")
                    for folder_name, full_path, parent_path in results:
                        print(f"\nPasta: {folder_name}")
                        print(f"Caminho: \"{full_path}\"")
                        print(f"Pasta Pai: {parent_path}")
            else:
                print(f"{RED}Nenhuma pasta encontrada.{RESET}")
        else:
            print(f"{RED}Por favor, digite um nome de pasta para pesquisar.{RESET}")
