import sqlite3
from typing import List, Tuple

def search_files_func(indexer, search_term: str, exact_match: bool = False) -> List[Tuple]:
    conn = indexer.get_db_connection()
    cursor = conn.cursor()
    
    try:
        if exact_match:
            query = "SELECT filename, full_path, file_size, modified_date FROM files WHERE filename = ? AND item_type = 'file'"
            cursor.execute(query, (search_term,))
        else:
            query = "SELECT filename, full_path, file_size, modified_date FROM files WHERE filename LIKE ? AND item_type = 'file'"
            cursor.execute(query, (f"%{search_term}%",))
        
        results = cursor.fetchall()
        return results
        
    except sqlite3.Error as e:
        indexer.logger.error(f"Erro na busca: {e}")
        return []
