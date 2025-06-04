from core.indexer import FileIndexer

def clear_index_menu(indexer: FileIndexer):
    """Handles the 'Clear Index' menu option."""
    confirm = input("Tem certeza que deseja limpar o índice? (s/N): ")
    if confirm.lower() == 's':
        indexer.clear_index()
        print("Índice limpo com sucesso.")
    else:
        print("Operação cancelada.")
