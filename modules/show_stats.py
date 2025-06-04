from core.indexer import FileIndexer

def show_stats_menu(indexer: FileIndexer):
    """Handles the 'Show Statistics' menu option."""
    stats = indexer.get_stats()
    print("\n=== ESTATÍSTICAS DO ÍNDICE ===")
    print(f"Total de arquivos: {stats.get('total_files', 0):,}")
    print(f"Total de pastas: {stats.get('total_folders', 0):,}")
    print(f"Tamanho total de arquivos: {stats.get('total_size_mb', 0):,.2f} MB")
    print("\nExtensões mais comuns:")
    for ext, count in stats.get('top_extensions', []):
        print(f"  {ext}: {count:,} arquivos")
