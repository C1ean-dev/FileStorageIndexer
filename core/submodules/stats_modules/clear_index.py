import sqlite3

def clear_index_func(indexer):
    conn = indexer.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM files")
        conn.commit()
        indexer.logger.info("Índice limpo com sucesso")
    except sqlite3.Error as e:
        indexer.logger.error(f"Erro ao limpar índice: {e}")
