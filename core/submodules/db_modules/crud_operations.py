import sqlite3
from typing import Optional

def insert_record_func(indexer, filename: str, full_path: str, parent_path: Optional[str],
                      file_size: Optional[int], modified_date: Optional[str], item_type: str):
    conn = indexer.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO files 
            (filename, full_path, parent_path, file_size, modified_date, item_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filename, full_path, parent_path, file_size, modified_date, item_type))
        conn.commit()
    except sqlite3.Error as e:
        indexer.logger.error(f"Erro ao inserir registro: {e}")
        raise

def update_record_func(indexer, full_path: str, file_size: Optional[int], modified_date: Optional[str]):
    conn = indexer.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE files
            SET file_size = ?, modified_date = ?, indexed_date = CURRENT_TIMESTAMP
            WHERE full_path = ?
        ''', (file_size, modified_date, full_path))
        conn.commit()
    except sqlite3.Error as e:
        indexer.logger.error(f"Erro ao atualizar registro para {full_path}: {e}")
        raise

def delete_record_func(indexer, full_path: str):
    conn = indexer.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM files WHERE full_path = ?', (full_path,))
        conn.commit()
    except sqlite3.Error as e:
        indexer.logger.error(f"Erro ao deletar registro para {full_path}: {e}")
        raise
