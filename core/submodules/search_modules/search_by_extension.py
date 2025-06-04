import sqlite3
from typing import List, Tuple

def search_by_extension_func(indexer, extension: str) -> List[Tuple]:
    conn = indexer.get_db_connection()
    cursor = conn.cursor()
    
    try:
        if not extension.startswith('.'):
            extension = '.' + extension
        
        query = "SELECT filename, full_path, file_size, modified_date FROM files WHERE filename LIKE ? AND item_type = 'file'"
        cursor.execute(query, (f"%{extension}",))
        
        results = cursor.fetchall()
        return results
        
    except sqlite3.Error as e:
        indexer.logger.error(f"Erro na busca por extensão: {e}")
        return []
