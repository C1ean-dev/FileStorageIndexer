from core.indexer import FileIndexer

def scan_batch_menu(indexer: FileIndexer):
    """Handles the 'Scan Network Folder (Batch)' menu option."""
    path = input("Digite o caminho da pasta de rede: ").strip()
    if path:
        print("Usando modo batch (barra de progresso determinada)")
        indexer.scan_network_folder_batch(path, update_existing=False)
