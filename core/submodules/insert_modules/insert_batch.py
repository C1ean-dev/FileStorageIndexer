import sqlite3
from pathlib import Path
from typing import List, Tuple

def insert_batch_records_func(indexer, batch_data: List[Tuple]):
    records_to_insert = []
    for filename, full_path, file_size, modified_date in batch_data:
        parent_path = str(Path(full_path).parent)
        records_to_insert.append((filename, full_path, parent_path, file_size, modified_date, 'file'))

    conn = indexer.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany('''
            INSERT OR REPLACE INTO files 
            (filename, full_path, parent_path, file_size, modified_date, item_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', records_to_insert)
        conn.commit()
    except sqlite3.Error as e:
        indexer.logger.error(f"Erro ao inserir lote de registros: {e}")
        raise
