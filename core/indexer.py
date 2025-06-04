import threading
from core.submodules.search_modules.search_files import search_files_func
from core.submodules.search_modules.search_by_extension import search_by_extension_func
from core.submodules.search_modules.search_folders import search_folders_func
from core.submodules.scan_modules.scan_streaming import scan_network_folder_func
from core.submodules.scan_modules.process_file import process_single_file_func
from core.submodules.scan_modules.scan_batch import scan_network_folder_batch_func
from core.submodules.scan_modules.scan_folders import scan_network_folders_func
from core.submodules.scan_modules.process_folder import process_single_folder_func
from core.submodules.db_modules.setup_logging import setup_logging_func
from core.submodules.db_modules.get_connection import get_db_connection_func
from core.submodules.db_modules.setup_schema import setup_database_schema_func
from core.submodules.db_modules.close_connection import close_connection_func
from core.submodules.insert_modules.insert_batch import insert_batch_records_func
from core.submodules.insert_modules.insert_single import insert_record_func
from core.submodules.insert_modules.insert_file import insert_file_record_func
from core.submodules.stats_modules.get_stats import get_stats_func
from core.submodules.stats_modules.clear_index import clear_index_func

class FileIndexer:
    def __init__(self, db_path: str = "file_index.db", max_workers: int = 8):
        self.db_path = db_path
        self.max_workers = max_workers
        self.thread_local_db = threading.local()
        
        setup_logging_func(self)
        setup_database_schema_func(self)

    def get_db_connection(self):
        return get_db_connection_func(self)

    def setup_database_schema(self):
        setup_database_schema_func(self)

    def scan_network_folder(self, network_path: str, update_existing: bool = False):
        scan_network_folder_func(self, network_path, update_existing)

    def process_single_file(self, filename: str, full_path: str):
        return process_single_file_func(self, filename, full_path)

    def scan_network_folder_batch(self, network_path: str, update_existing: bool = False):
        scan_network_folder_batch_func(self, network_path, update_existing)

    def scan_network_folders(self, network_path: str):
        scan_network_folders_func(self, network_path)

    def _process_single_folder(self, folder_name: str, full_path: str):
        return process_single_folder_func(self, folder_name, full_path)

    def insert_batch_records(self, batch_data):
        insert_batch_records_func(self, batch_data)

    def insert_record(self, filename, full_path, parent_path, file_size, modified_date, item_type):
        insert_record_func(self, filename, full_path, parent_path, file_size, modified_date, item_type)

    def insert_file_record(self, filename, full_path, file_size, modified_date):
        insert_file_record_func(self, filename, full_path, file_size, modified_date)

    def search_files(self, search_term: str, exact_match: bool = False):
        return search_files_func(self, search_term, exact_match)

    def search_by_extension(self, extension: str):
        return search_by_extension_func(self, extension)

    def search_folders(self, search_term: str, exact_match: bool = False):
        return search_folders_func(self, search_term, exact_match)

    def get_stats(self) -> dict:
        return get_stats_func(self)
    
    def clear_index(self):
        clear_index_func(self)

    def close(self):
        close_connection_func(self)

def format_file_size(size_bytes: int) -> str:
    """Formata o tamanho do arquivo em formato legível"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"
