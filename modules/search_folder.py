import os
from core.indexer import FileIndexer

def search_folder_menu(indexer: FileIndexer):
    """Handles the 'Search Folder' menu option."""
    search_term = input("Digite o nome da pasta: ").strip()
    if search_term:
        results = indexer.search_folders(search_term)
        if results:
            if len(results) == 1:
                folder_name, full_path, parent_path = results[0]
                print(f"Abrindo pasta encontrada: \"{full_path}\"")
                os.startfile(full_path)
            else:
                print(f"\nEncontradas {len(results)} pasta(s):")
                for folder_name, full_path, parent_path in results:
                    print(f"\nPasta: {folder_name}")
                    print(f"Caminho: \"{full_path}\"")
                    print(f"Pasta Pai: {parent_path}")
        else:
            print("Nenhuma pasta encontrada.")
