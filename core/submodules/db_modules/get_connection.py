import sqlite3

def get_db_connection_func(indexer):
    if not hasattr(indexer.thread_local_db, "conn"):
        indexer.thread_local_db.conn = sqlite3.connect(indexer.db_path)
        indexer.thread_local_db.conn.execute('PRAGMA journal_mode = WAL;')
        indexer.thread_local_db.conn.execute('PRAGMA synchronous = OFF;')
    return indexer.thread_local_db.conn
