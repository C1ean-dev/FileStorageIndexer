import os
from core.indexer import FileIndexer

RED = '\033[91m'
BLUE = '\033[94m'
GREEN = '\033[92m'
RESET = '\033[0m'

def search_folder_menu(indexer: FileIndexer):
    """Handles the 'Search Folder' menu option."""
    while True:
        search_term = input(f"{BLUE}Digite o nome da pasta (ou '0' para voltar): {RESET}").strip()
        if search_term == '0':
            print(f"{BLUE}Voltando ao menu principal...{RESET}")
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
                    print(f"{BLUE}\nEncontradas {len(results)} pasta(s):{RESET}")
                    for folder_name, full_path, parent_path in results:
                        print(f"{BLUE}\nPasta: {folder_name}{RESET}")
                        print(f"{BLUE}Caminho: \"{full_path}\"{RESET}")
                        print(f"{BLUE}Pasta Pai: {parent_path}{RESET}")
            else:
                print(f"{RED}Nenhuma pasta encontrada.{RESET}")
        else:
            print(f"{RED}Por favor, digite um nome de pasta para pesquisar.{RESET}")
