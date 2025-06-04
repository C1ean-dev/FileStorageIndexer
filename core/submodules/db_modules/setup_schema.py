import sqlite3

def setup_database_schema_func(indexer):
    conn = sqlite3.connect(indexer.db_path)
    cursor = conn.cursor()
    
    cursor.execute('PRAGMA journal_mode = WAL;')
    cursor.execute('PRAGMA synchronous = OFF;')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            full_path TEXT NOT NULL UNIQUE,
            parent_path TEXT,
            file_size INTEGER,
            modified_date TEXT,
            item_type TEXT NOT NULL,
            indexed_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_filename ON files(filename)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_full_path ON files(full_path)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_type ON files(item_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_parent_path ON files(parent_path)')
    
    conn.commit()
    conn.close()
    indexer.logger.info(f"Esquema do banco de dados configurado: {indexer.db_path}")
