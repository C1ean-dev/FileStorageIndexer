from core.indexer import FileIndexer, format_file_size

RED = '\033[91m'
BLUE = '\033[94m'
GREEN = '\033[92m'
RESET = '\033[0m'

def search_file_menu(indexer: FileIndexer):
    """Handles the 'Search File' menu option."""
    while True:
        search_term = input(f"{BLUE}Digite o nome do arquivo (ou '0' para voltar): {RESET}").strip()
        if search_term == '0':
            print(f"{BLUE}Voltando ao menu principal...{RESET}")
            break # Exit the loop

        if search_term:
            results = indexer.search_files(search_term)
            if results:
                print(f"{GREEN}\nEncontrados {len(results)} arquivo(s):{RESET}")
                for filename, full_path, file_size, modified_date in results:
                    print(f"{GREEN}\nArquivo: {filename}{RESET}")
                    print(f"{GREEN}Caminho: {full_path}{RESET}")
                    print(f"{GREEN}Tamanho: {format_file_size(file_size)}{RESET}")
            else:
                print(f"{RED}Nenhum arquivo encontrado.{RESET}")
        else:
            print(f"{RED}Por favor, digite um nome de arquivo para pesquisar.{RESET}")
