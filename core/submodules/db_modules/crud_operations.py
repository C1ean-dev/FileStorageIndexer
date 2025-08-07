import sqlite3
import time
from typing import Optional

# Max retries for database operations
MAX_RETRIES = 5
RETRY_DELAY = 0.1 # seconds

def _execute_with_retry(indexer, query, params=(), is_write_op=False, error_msg="Erro na operação de banco de dados"):
    for attempt in range(MAX_RETRIES):
        conn = indexer.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if is_write_op:
                conn.commit()
            return True
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
    return False # Indicate failure after retries

def insert_record_func(indexer, filename: str, full_path: str, parent_path: Optional[str],
                      file_size: Optional[int], modified_date: Optional[str], item_type: str):
    query = '''
        INSERT OR IGNORE INTO files 
        (filename, full_path, parent_path, file_size, modified_date, item_type)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    params = (filename, full_path, parent_path, file_size, modified_date, item_type)
    _execute_with_retry(indexer, query, params, is_write_op=True, error_msg=f"Erro ao inserir registro para {full_path}")

def update_record_func(indexer, full_path: str, file_size: Optional[int], modified_date: Optional[str]):
    query = '''
        UPDATE files
        SET file_size = ?, modified_date = ?, indexed_date = CURRENT_TIMESTAMP
        WHERE full_path = ?
    '''
    params = (file_size, modified_date, full_path)
    _execute_with_retry(indexer, query, params, is_write_op=True, error_msg=f"Erro ao atualizar registro para {full_path}")

def delete_record_func(indexer, full_path: str):
    query = 'DELETE FROM files WHERE full_path = ?'
    params = (full_path,)
    _execute_with_retry(indexer, query, params, is_write_op=True, error_msg=f"Erro ao deletar registro para {full_path}")
