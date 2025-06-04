from core.indexer import FileIndexer, format_file_size

def search_file_menu(indexer: FileIndexer):
    """Handles the 'Search File' menu option."""
    search_term = input("Digite o nome do arquivo: ").strip()
    if search_term:
        results = indexer.search_files(search_term)
        if results:
            print(f"\nEncontrados {len(results)} arquivo(s):")
            for filename, full_path, file_size, modified_date in results:
                print(f"\nArquivo: {filename}")
                print(f"Caminho: {full_path}")
                print(f"Tamanho: {format_file_size(file_size)}")
        else:
            print("Nenhum arquivo encontrado.")
