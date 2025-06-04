from pathlib import Path

def process_single_folder_func(indexer, folder_name: str, full_path: str) -> bool:
    try:
        parent_path = str(Path(full_path).parent)
        indexer.insert_record(folder_name, full_path, parent_path, None, None, 'folder')
        return True
    except (OSError, PermissionError) as e:
        indexer.logger.warning(f"Não foi possível indexar a pasta {full_path}: {e}")
        return False
