"""
SQLite Schema Manager

Manages database schema creation, migration, and maintenance.
"""

from typing import Optional

from src.application.interfaces.services.logger import Logger
from .connection_manager import SqliteConnectionManager


class SqliteSchemaManager:
    """
    Manages SQLite database schema operations.
    
    Handles table creation, indexing, and schema migrations.
    """
    
    # Current schema version
    SCHEMA_VERSION = 2
    
    def __init__(self, connection_manager: SqliteConnectionManager, logger: Optional[Logger] = None):
        """
        Initialize the schema manager.
        
        Args:
            connection_manager: SQLite connection manager
            logger: Optional logger for debugging
        """
        self.connection_manager = connection_manager
        self.logger = logger
    
    def initialize_database(self) -> None:
        """
        Initialize the database with the current schema.
        
        Creates all necessary tables and indexes if they don't exist.
        """
        try:
            if self.logger:
                self.logger.info("Initializing database schema...")
            
            # Create schema version table first
            self._create_schema_version_table()
            
            # Check current schema version
            current_version = self._get_schema_version()
            
            if current_version == 0:
                # Fresh database - create all tables
                self._create_all_tables()
                self._create_all_indexes()
                self._set_schema_version(self.SCHEMA_VERSION)
                
                if self.logger:
                    self.logger.info(f"Created new database schema version {self.SCHEMA_VERSION}")
            
            elif current_version < self.SCHEMA_VERSION:
                # Need to migrate
                self._migrate_schema(current_version, self.SCHEMA_VERSION)
                
                if self.logger:
                    self.logger.info(f"Migrated database schema from {current_version} to {self.SCHEMA_VERSION}")
            
            elif current_version > self.SCHEMA_VERSION:
                # Database is newer than our code - this could be problematic
                if self.logger:
                    self.logger.warning(f"Database schema version {current_version} is newer than expected {self.SCHEMA_VERSION}")
            
            else:
                # Schema is up to date
                if self.logger:
                    self.logger.debug(f"Database schema is up to date (version {current_version})")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize database schema: {str(e)}")
            raise
    
    def _create_schema_version_table(self) -> None:
        """Create the schema version tracking table."""
        sql = """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.connection_manager.execute_command(sql)
    
    def _get_schema_version(self) -> int:
        """
        Get the current schema version.
        
        Returns:
            Current schema version, or 0 if not set
        """
        try:
            results = self.connection_manager.execute_query(
                "SELECT MAX(version) FROM schema_version"
            )
            return results[0][0] if results and results[0][0] is not None else 0
        except:
            return 0
    
    def _set_schema_version(self, version: int) -> None:
        """
        Set the schema version.
        
        Args:
            version: Schema version to set
        """
        self.connection_manager.execute_command(
            "INSERT INTO schema_version (version) VALUES (?)",
            (version,)
        )
    
    def _create_all_tables(self) -> None:
        """Create all database tables."""
        # Files table
        files_table_sql = """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            full_path TEXT NOT NULL UNIQUE,
            parent_path TEXT NOT NULL,
            file_size INTEGER NOT NULL DEFAULT 0,
            modified_date TIMESTAMP NOT NULL,
            item_type TEXT NOT NULL DEFAULT 'file',
            extension TEXT,
            category TEXT,
            is_hidden BOOLEAN DEFAULT 0,
            is_system_file BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Folders table
        folders_table_sql = """
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_name TEXT NOT NULL,
            full_path TEXT NOT NULL UNIQUE,
            parent_path TEXT NOT NULL,
            modified_date TIMESTAMP NOT NULL,
            depth_level INTEGER DEFAULT 0,
            is_hidden BOOLEAN DEFAULT 0,
            is_system_folder BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Statistics cache table
        stats_cache_sql = """
        CREATE TABLE IF NOT EXISTS stats_cache (
            id INTEGER PRIMARY KEY,
            cache_key TEXT NOT NULL UNIQUE,
            cache_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
        """
        
        # Execute table creation
        self.connection_manager.execute_command(files_table_sql)
        self.connection_manager.execute_command(folders_table_sql)
        self.connection_manager.execute_command(stats_cache_sql)
        
        if self.logger:
            self.logger.debug("Created all database tables")
    
    def _create_all_indexes(self) -> None:
        """Create all database indexes for performance."""
        indexes = [
            # Files table indexes
            "CREATE INDEX IF NOT EXISTS idx_files_filename ON files(filename)",
            "CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension)",
            "CREATE INDEX IF NOT EXISTS idx_files_category ON files(category)",
            "CREATE INDEX IF NOT EXISTS idx_files_parent_path ON files(parent_path)",
            "CREATE INDEX IF NOT EXISTS idx_files_size ON files(file_size)",
            "CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified_date)",
            "CREATE INDEX IF NOT EXISTS idx_files_type ON files(item_type)",
            
            # Folders table indexes
            "CREATE INDEX IF NOT EXISTS idx_folders_name ON folders(folder_name)",
            "CREATE INDEX IF NOT EXISTS idx_folders_parent_path ON folders(parent_path)",
            "CREATE INDEX IF NOT EXISTS idx_folders_depth ON folders(depth_level)",
            "CREATE INDEX IF NOT EXISTS idx_folders_modified ON folders(modified_date)",
            
            # Stats cache indexes
            "CREATE INDEX IF NOT EXISTS idx_stats_cache_key ON stats_cache(cache_key)",
            "CREATE INDEX IF NOT EXISTS idx_stats_cache_expires ON stats_cache(expires_at)",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_files_name_ext ON files(filename, extension)",
            "CREATE INDEX IF NOT EXISTS idx_files_parent_name ON files(parent_path, filename)",
        ]
        
        for index_sql in indexes:
            try:
                self.connection_manager.execute_command(index_sql)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Failed to create index: {str(e)}")
        
        if self.logger:
            self.logger.debug("Created all database indexes")
    
    def _migrate_schema(self, from_version: int, to_version: int) -> None:
        """
        Migrate schema from one version to another.

        Args:
            from_version: Current schema version
            to_version: Target schema version
        """
        if self.logger:
            self.logger.info(f"Migrating schema from version {from_version} to {to_version}")

        # Handle migrations based on version
        if from_version < 1 and to_version >= 1:
            self._migrate_to_version_1()
        elif from_version < 2 and to_version >= 2:
            self._migrate_to_version_2()

        # Update schema version
        self._set_schema_version(to_version)

    def _migrate_to_version_1(self) -> None:
        """
        Migrate to version 1: Add missing columns to existing tables.
        """
        if self.logger:
            self.logger.info("Applying migration to version 1: Adding missing columns")

        try:
            # Add missing columns to files table
            self._add_column_if_not_exists('files', 'extension', 'TEXT')
            self._add_column_if_not_exists('files', 'category', 'TEXT')
            self._add_column_if_not_exists('files', 'is_hidden', 'BOOLEAN DEFAULT 0')
            self._add_column_if_not_exists('files', 'is_system_file', 'BOOLEAN DEFAULT 0')
            self._add_column_if_not_exists('files', 'created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            self._add_column_if_not_exists('files', 'updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')

            # Add missing columns to folders table
            self._add_column_if_not_exists('folders', 'depth_level', 'INTEGER DEFAULT 0')
            self._add_column_if_not_exists('folders', 'is_hidden', 'BOOLEAN DEFAULT 0')
            self._add_column_if_not_exists('folders', 'is_system_folder', 'BOOLEAN DEFAULT 0')
            self._add_column_if_not_exists('folders', 'created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            self._add_column_if_not_exists('folders', 'updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')

            if self.logger:
                self.logger.info("Migration to version 1 completed successfully")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Migration to version 1 failed: {str(e)}")
            raise

    def _migrate_to_version_2(self) -> None:
        """
        Migrate to version 2: Ensure all required columns exist.
        """
        if self.logger:
            self.logger.info("Applying migration to version 2: Ensuring schema completeness")

        try:
            # Ensure all required columns exist (version 1 migration should have added them)
            # This migration is mainly for validation and future-proofing
            required_columns = {
                'files': ['extension', 'category', 'is_hidden', 'is_system_file', 'created_at', 'updated_at'],
                'folders': ['depth_level', 'is_hidden', 'is_system_folder', 'created_at', 'updated_at']
            }

            for table, columns in required_columns.items():
                for column in columns:
                    # This will add the column if it doesn't exist
                    if column == 'extension':
                        self._add_column_if_not_exists(table, column, 'TEXT')
                    elif column in ['category']:
                        self._add_column_if_not_exists(table, column, 'TEXT')
                    elif column in ['is_hidden', 'is_system_file', 'is_system_folder']:
                        self._add_column_if_not_exists(table, column, 'BOOLEAN DEFAULT 0')
                    elif column == 'depth_level':
                        self._add_column_if_not_exists(table, column, 'INTEGER DEFAULT 0')
                    elif column in ['created_at', 'updated_at']:
                        # SQLite doesn't allow CURRENT_TIMESTAMP as default when adding columns
                        # So we add without default and then update existing rows
                        self._add_timestamp_column(table, column)

            if self.logger:
                self.logger.info("Migration to version 2 completed successfully")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Migration to version 2 failed: {str(e)}")
            raise

    def _add_column_if_not_exists(self, table_name: str, column_name: str, column_definition: str) -> None:
        """
        Add a column to a table if it doesn't already exist.

        Args:
            table_name: Name of the table
            column_name: Name of the column to add
            column_definition: SQL definition of the column
        """
        try:
            # Check if column exists
            result = self.connection_manager.execute_query(
                f"PRAGMA table_info({table_name})"
            )

            column_exists = any(row[1] == column_name for row in result)

            if not column_exists:
                # Add the column
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
                self.connection_manager.execute_command(sql)

                if self.logger:
                    self.logger.debug(f"Added column {column_name} to table {table_name}")
            else:
                if self.logger:
                    self.logger.debug(f"Column {column_name} already exists in table {table_name}")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to add column {column_name} to {table_name}: {str(e)}")
            raise

    def _add_timestamp_column(self, table_name: str, column_name: str) -> None:
        """
        Add a timestamp column to a table, handling SQLite limitations.

        Args:
            table_name: Name of the table
            column_name: Name of the timestamp column to add
        """
        try:
            # Check if column exists
            result = self.connection_manager.execute_query(
                f"PRAGMA table_info({table_name})"
            )

            column_exists = any(row[1] == column_name for row in result)

            if not column_exists:
                # Add the column without default first
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} TIMESTAMP"
                self.connection_manager.execute_command(sql)

                # Update existing rows with current timestamp
                import datetime
                current_time = datetime.datetime.now().isoformat()
                sql = f"UPDATE {table_name} SET {column_name} = ? WHERE {column_name} IS NULL"
                self.connection_manager.execute_command(sql, (current_time,))

                if self.logger:
                    self.logger.debug(f"Added timestamp column {column_name} to table {table_name}")
            else:
                if self.logger:
                    self.logger.debug(f"Timestamp column {column_name} already exists in table {table_name}")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to add timestamp column {column_name} to {table_name}: {str(e)}")
            raise

    def drop_all_tables(self) -> None:
        """
        Drop all tables (for testing or complete reset).
        
        WARNING: This will delete all data!
        """
        if self.logger:
            self.logger.warning("Dropping all database tables - ALL DATA WILL BE LOST!")
        
        tables = ['files', 'folders', 'stats_cache', 'schema_version']
        
        for table in tables:
            try:
                self.connection_manager.execute_command(f"DROP TABLE IF EXISTS {table}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to drop table {table}: {str(e)}")
        
        if self.logger:
            self.logger.info("All tables dropped")
    
    def clear_all_data(self) -> None:
        """
        Clear all data from tables (but keep schema).
        
        WARNING: This will delete all data!
        """
        if self.logger:
            self.logger.warning("Clearing all data from database tables")
        
        tables = ['files', 'folders', 'stats_cache']
        
        for table in tables:
            try:
                self.connection_manager.execute_command(f"DELETE FROM {table}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to clear table {table}: {str(e)}")
        
        # Reset auto-increment counters
        self.connection_manager.execute_command("DELETE FROM sqlite_sequence")
        
        if self.logger:
            self.logger.info("All data cleared from database")
    
    def get_table_stats(self) -> dict:
        """
        Get statistics about database tables.
        
        Returns:
            Dictionary with table statistics
        """
        stats = {}
        
        tables = ['files', 'folders', 'stats_cache']
        
        for table in tables:
            try:
                # Get row count
                count_result = self.connection_manager.execute_query(f"SELECT COUNT(*) FROM {table}")
                row_count = count_result[0][0] if count_result else 0
                
                stats[table] = {
                    'row_count': row_count
                }
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to get stats for table {table}: {str(e)}")
                stats[table] = {'row_count': 0, 'error': str(e)}
        
        return stats
    
    def optimize_database(self) -> None:
        """Optimize the database for better performance."""
        if self.logger:
            self.logger.info("Optimizing database...")
        
        try:
            # Update statistics for query planner
            self.connection_manager.analyze()
            
            # Vacuum to reclaim space and defragment
            self.connection_manager.vacuum()
            
            if self.logger:
                self.logger.info("Database optimization completed")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Database optimization failed: {str(e)}")
            raise