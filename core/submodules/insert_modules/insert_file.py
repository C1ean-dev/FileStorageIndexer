from pathlib import Path

def insert_file_record_func(indexer, filename: str, full_path: str, 
                          file_size: int, modified_date: str):
    parent_path = str(Path(full_path).parent)
    indexer.insert_record(filename, full_path, parent_path, file_size, modified_date, 'file')
