from core.indexer import FileIndexer

def scan_folders_menu(indexer: FileIndexer):
    """Handles the 'Scan Folders Only' menu option."""
    path = input("Digite o caminho da pasta de rede para escanear pastas: ").strip()
    if path:
        # Explicitly set show_progress to True for manual scans
        indexer.scan_network_folders(path, show_progress=True)
