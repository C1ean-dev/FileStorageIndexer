from core.indexer import FileIndexer

def scan_streaming_menu(indexer: FileIndexer):
    """Handles the 'Scan Network Folder (Streaming)' menu option."""
    path = input("Digite o caminho da pasta de rede: ").strip()
    if path:
        print("Usando modo streaming (baixo uso de memória)")
        indexer.scan_network_folder(path, update_existing=False)
