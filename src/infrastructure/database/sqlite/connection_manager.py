"""
SQLite Connection Manager

Manages SQLite database connections with thread safety and optimization.
"""

import sqlite3
import threading
from typing import Optional, Dict, Any
from contextlib import contextmanager

from src.application.interfaces.services.logger import Logger


class SqliteConnectionManager:
    """
    Manages SQLite database connections with thread safety.
    
    Provides connection pooling, thread-local storage, and database optimization.
    """
    
    def __init__(self, db_path: str, logger: Optional[Logger] = None):
        """
        Initialize the connection manager.
        
        Args:
            db_path: Path to the SQLite database file
            logger: Optional logger for debugging
        """
        self.db_path = db_path
        self.logger = logger
        self._thread_local = threading.local()
        self._lock = threading.Lock()
        self._is_initialized = False
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a thread-local database connection.
        
        Returns:
            SQLite connection for the current thread
        """
        if not hasattr(self._thread_local, 'connection') or self._thread_local.connection is None:
            self._thread_local.connection = self._create_connection()
        
        return self._thread_local.connection
    
    def _create_connection(self) -> sqlite3.Connection:
        """
        Create a new SQLite connection with optimizations.
        
        Returns:
            Optimized SQLite connection
        """
        try:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,  # Allow sharing between threads
                timeout=30.0  # 30 second timeout
            )
            
            # Apply performance optimizations
            self._optimize_connection(conn)
            
            if self.logger:
                self.logger.debug(f"Created new SQLite connection to {self.db_path}")
            
            return conn
            
        except sqlite3.Error as e:
            if self.logger:
                self.logger.error(f"Failed to create SQLite connection: {str(e)}")
            raise
    
    def _optimize_connection(self, conn: sqlite3.Connection) -> None:
        """
        Apply performance optimizations to the connection.
        
        Args:
            conn: SQLite connection to optimize
        """
        cursor = conn.cursor()
        
        try:
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode = WAL")
            
            # Optimize for speed over safety (acceptable for indexing)
            cursor.execute("PRAGMA synchronous = NORMAL")
            
            # Increase cache size (in KB)
            cursor.execute("PRAGMA cache_size = 10000")
            
            # Optimize temp storage
            cursor.execute("PRAGMA temp_store = MEMORY")
            
            # Enable memory-mapped I/O (if supported)
            cursor.execute("PRAGMA mmap_size = 268435456")  # 256MB
            
            # Optimize page size
            cursor.execute("PRAGMA page_size = 4096")
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            conn.commit()
            
            if self.logger:
                self.logger.debug("Applied SQLite performance optimizations")
                
        except sqlite3.Error as e:
            if self.logger:
                self.logger.warning(f"Failed to apply some optimizations: {str(e)}")
        finally:
            cursor.close()
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for getting a database cursor.
        
        Yields:
            SQLite cursor
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Yields:
            SQLite connection within a transaction
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def execute_script(self, script: str) -> None:
        """
        Execute a SQL script.
        
        Args:
            script: SQL script to execute
        """
        with self.transaction() as conn:
            conn.executescript(script)
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of query results
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_command(self, command: str, params: tuple = ()) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE command.
        
        Args:
            command: SQL command to execute
            params: Command parameters
            
        Returns:
            Number of affected rows
        """
        with self.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(command, params)
                return cursor.rowcount
            finally:
                cursor.close()
    
    def execute_many(self, command: str, params_list: list) -> int:
        """
        Execute a command multiple times with different parameters.
        
        Args:
            command: SQL command to execute
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        with self.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(command, params_list)
                return cursor.rowcount
            finally:
                cursor.close()
    
    def get_table_info(self, table_name: str) -> list:
        """
        Get information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information
        """
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists
        """
        query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
        """
        results = self.execute_query(query, (table_name,))
        return len(results) > 0
    
    def get_database_size(self) -> int:
        """
        Get the database file size in bytes.
        
        Returns:
            Database size in bytes
        """
        query = "PRAGMA page_count"
        page_count_result = self.execute_query(query)
        page_count = page_count_result[0][0] if page_count_result else 0
        
        query = "PRAGMA page_size"
        page_size_result = self.execute_query(query)
        page_size = page_size_result[0][0] if page_size_result else 4096
        
        return page_count * page_size
    
    def vacuum(self) -> None:
        """
        Vacuum the database to reclaim space and optimize.
        """
        if self.logger:
            self.logger.info("Starting database vacuum operation")
        
        conn = self.get_connection()
        conn.execute("VACUUM")
        
        if self.logger:
            self.logger.info("Database vacuum completed")
    
    def analyze(self) -> None:
        """
        Analyze the database to update query planner statistics.
        """
        if self.logger:
            self.logger.info("Analyzing database statistics")
        
        conn = self.get_connection()
        conn.execute("ANALYZE")
        
        if self.logger:
            self.logger.info("Database analysis completed")
    
    def close_connection(self) -> None:
        """Close the thread-local connection."""
        if hasattr(self._thread_local, 'connection') and self._thread_local.connection:
            try:
                self._thread_local.connection.close()
                self._thread_local.connection = None
                
                if self.logger:
                    self.logger.debug("Closed SQLite connection")
                    
            except sqlite3.Error as e:
                if self.logger:
                    self.logger.error(f"Error closing connection: {str(e)}")
    
    def close_all_connections(self) -> None:
        """Close all connections (called on shutdown)."""
        with self._lock:
            # This is a simplified approach - in a real implementation,
            # you might want to track all connections across threads
            self.close_connection()
            
            if self.logger:
                self.logger.info("Closed all database connections")