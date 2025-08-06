import sqlite3
import threading # Import threading for thread-local storage

def _is_connection_alive(conn):
    try:
        # Attempt a simple query to check if the connection is still active
        conn.execute("SELECT 1")
        return True
    except sqlite3.ProgrammingError as e:
        # If the error message indicates a closed database, return False
        if "closed database" in str(e).lower():
            return False
        # Re-raise other programming errors
        raise
    except Exception:
        # Catch any other unexpected errors that might indicate a broken connection
        return False

def get_db_connection_func(indexer):
    # Check if connection exists, is not None, and is still alive
    if not hasattr(indexer.thread_local_db, "conn") or \
       indexer.thread_local_db.conn is None or \
       not _is_connection_alive(indexer.thread_local_db.conn):
        indexer.thread_local_db.conn = sqlite3.connect(indexer.db_path)
        indexer.thread_local_db.conn.execute('PRAGMA journal_mode = WAL;')
        indexer.thread_local_db.conn.execute('PRAGMA synchronous = OFF;')
    return indexer.thread_local_db.conn
