from core.indexer import FileIndexer

def search_folder_menu(indexer: FileIndexer):
    """Handles the 'Search Folder' menu option."""
    search_term = input("Digite o nome da pasta: ").strip()
    if search_term:
        results = indexer.search_folders(search_term)
        if results:
            print(f"\nEncontradas {len(results)} pasta(s):")
            for folder_name, full_path, parent_path in results:
                print(f"\nPasta: {folder_name}")
                print(f"Caminho: {full_path}")
                print(f"Pasta Pai: {parent_path}")
        else:
            print("Nenhuma pasta encontrada.")
