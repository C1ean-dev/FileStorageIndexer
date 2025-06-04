import sqlite3

def get_stats_func(indexer) -> dict:
    conn = indexer.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM files WHERE item_type = 'file'")
        total_files = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM files WHERE item_type = 'folder'")
        total_folders = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(file_size) FROM files WHERE item_type = 'file'")
        total_size = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT SUBSTR(filename, INSTR(filename, '.')) as extension, COUNT(*) as count
            FROM files 
            WHERE filename LIKE '%.%' AND item_type = 'file'
            GROUP BY extension 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        top_extensions = cursor.fetchall()
        
        return {
            'total_files': total_files,
            'total_folders': total_folders,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'top_extensions': top_extensions
        }
        
    except sqlite3.Error as e:
        indexer.logger.error(f"Erro ao obter estatísticas: {e}")
        return {}
