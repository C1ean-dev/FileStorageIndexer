def close_connection_func(indexer):
    if hasattr(indexer.thread_local_db, "conn") and indexer.thread_local_db.conn:
        indexer.thread_local_db.conn.close()
        del indexer.thread_local_db.conn
        indexer.logger.info("Conexão com banco de dados da thread atual fechada")
