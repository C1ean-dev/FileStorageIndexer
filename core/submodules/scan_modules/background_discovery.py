import os
import time
import threading
import string
import sqlite3
from typing import List
from config import SKIP_C_DRIVE_DISCOVERY # Import the feature flag

# Max retries for database operations
MAX_RETRIES = 5
RETRY_DELAY = 0.1 # seconds

def _execute_read_with_retry(indexer, query, params=(), error_msg="Erro na operação de leitura de banco de dados"):
    for attempt in range(MAX_RETRIES):
        conn = indexer.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                indexer.logger.warning(f"{error_msg} (tentativa {attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY * (2 ** attempt)) # Exponential backoff
            else:
                indexer.logger.error(f"{error_msg}: {e}")
                raise
        except sqlite3.Error as e:
            indexer.logger.error(f"{error_msg}: {e}")
            raise
    indexer.logger.error(f"{error_msg}: Falha após {MAX_RETRIES} tentativas devido a bloqueio do banco de dados.")
    return [] # Indicate failure after retries

def background_discovery_func(indexer, interval_seconds: int = 3600, stop_event: threading.Event = None):
    indexer.logger.info(f"Iniciando processo de descoberta de novas pastas em segundo plano.")
    
    if stop_event is None:
        stop_event = threading.Event()

    def _run_discovery_cycle():
        while not stop_event.is_set():
            try:
                indexer.logger.info(f"Iniciando ciclo de descoberta de novas pastas...")
                
                # Step 1: Discover potential root paths (drives on Windows)
                potential_roots = []
                # This tool is specifically for Windows, so only check Windows drives
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:/"
                    
                    if SKIP_C_DRIVE_DISCOVERY and drive.upper() == "C:/":
                        indexer.logger.info(f"Descoberta do drive C: pulada por feature flag.")
                        continue

                    if os.path.exists(drive) and os.path.isdir(drive):
                        potential_roots.append(drive)
                    else:
                        indexer.logger.info(f"Caminho '{drive}' não encontrado ou não é um diretório. Pulando descoberta.")

                # Step 2: Get currently mapped top-level folders from the database
                mapped_top_level_folders = set()
                query = "SELECT full_path FROM files WHERE item_type = 'folder' AND LENGTH(full_path) = 3 AND SUBSTR(full_path, 2, 1) = ':'"
                results = _execute_read_with_retry(indexer, query, error_msg="Erro ao recuperar pastas mapeadas para descoberta")
                for row in results:
                    mapped_top_level_folders.add(row[0])

                new_folders_discovered = 0
                # Step 3: Identify and scan new root paths
                for root_path in potential_roots:
                    if stop_event.is_set():
                        indexer.logger.info("Parando descoberta de novas pastas devido a evento de parada.")
                        break
                    
                    if root_path not in mapped_top_level_folders:
                        indexer.logger.info(f"Nova pasta raiz descoberta: {root_path}. Iniciando escaneamento em segundo plano...")
                        # Use existing scan_network_folders_func to scan the new root silently
                        indexer.scan_network_folders(root_path, show_progress=False)
                        new_folders_discovered += 1
                
                indexer.logger.info(f"Ciclo de descoberta de novas pastas concluído. Novas pastas descobertas: {new_folders_discovered}")

            except Exception as e:
                indexer.logger.error(f"Erro inesperado no processo de descoberta em segundo plano: {e}")
            
            if not stop_event.is_set():
                time.sleep(interval_seconds)

        indexer.logger.info(f"Processo de descoberta em segundo plano finalizado.")

    discovery_thread = threading.Thread(target=_run_discovery_cycle, daemon=True)
    discovery_thread.start()
    return discovery_thread, stop_event
