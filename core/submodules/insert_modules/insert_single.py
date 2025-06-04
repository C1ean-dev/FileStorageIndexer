import sqlite3
from typing import Optional

def insert_record_func(indexer, filename: str, full_path: str, parent_path: Optional[str],
                      file_size: Optional[int], modified_date: Optional[str], item_type: str):
    conn = indexer.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO files 
            (filename, full_path, parent_path, file_size, modified_date, item_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filename, full_path, parent_path, file_size, modified_date, item_type))
        conn.commit()
    except sqlite3.Error as e:
        indexer.logger.error(f"Erro ao inserir registro: {e}")
        raise
