import sqlite3
from typing import List, Tuple

def search_folders_func(indexer, search_term: str, exact_match: bool = False) -> List[Tuple]:
    conn = indexer.get_db_connection()
    cursor = conn.cursor()
    
    try:
        if exact_match:
            query = "SELECT filename, full_path, parent_path FROM files WHERE filename = ? AND item_type = 'folder'"
            cursor.execute(query, (search_term,))
        else:
            query = "SELECT filename, full_path, parent_path FROM files WHERE filename LIKE ? AND item_type = 'folder'"
            cursor.execute(query, (f"%{search_term}%",))
        
        results = cursor.fetchall()
        return results
        
    except sqlite3.Error as e:
        indexer.logger.error(f"Erro na busca de pastas: {e}")
        return []
