import sqlite3
import time
from typing import List, Tuple

# Max retries for database operations
MAX_RETRIES = 5
RETRY_DELAY = 0.1 # seconds

def _execute_read_with_retry(indexer, query, params=(), error_msg="Erro na operação de leitura de banco de dados"):
    for attempt in range(MAX_RETRIES):
        conn = indexer.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                indexer.logger.info(f"{error_msg} (tentativa {attempt + 1}/{MAX_RETRIES}): {e}") # Change to INFO
                time.sleep(RETRY_DELAY * (2 ** attempt)) # Exponential backoff
            else:
                indexer.logger.error(f"{error_msg}: {e}")
                raise
        except sqlite3.Error as e:
            indexer.logger.error(f"{error_msg}: {e}")
            raise
    indexer.logger.error(f"{error_msg}: Falha após {MAX_RETRIES} tentativas devido a bloqueio do banco de dados.")
    return [] # Indicate failure after retries

def search_folders_func(indexer, search_term: str, exact_match: bool = False) -> List[Tuple]:
    if exact_match:
        query = "SELECT filename, full_path, parent_path FROM files WHERE filename = ? AND item_type = 'folder'"
        params = (search_term,)
    else:
        query = "SELECT filename, full_path, parent_path FROM files WHERE filename LIKE ? AND item_type = 'folder'"
        params = (f"%{search_term}%",)
    
    results = _execute_read_with_retry(indexer, query, params, error_msg=f"Erro na busca de pastas para '{search_term}'")
    
    # Convert rows to dictionary for consistency if needed, or keep as tuple list
    # For now, keeping as list of tuples as per original return type
    return results
