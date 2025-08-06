import os
import time
import threading
from pathlib import Path
import sqlite3
from typing import List

def background_update_func(indexer, interval_seconds: int = 3600, stop_event: threading.Event = None):
    indexer.logger.info(f"Iniciando processo de atualização em segundo plano.")
    
    if stop_event is None:
        stop_event = threading.Event() # Create a default event if not provided

    def _run_update_cycle():
        while not stop_event.is_set():
            try:
                # Get all unique parent paths (mapped folders) from the database to monitor
                mapped_paths = set()
                conn = indexer.get_db_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT DISTINCT full_path FROM files WHERE item_type = 'folder'")
                    for row in cursor.fetchall():
                        mapped_paths.add(row[0])
                except Exception as e:
                    indexer.logger.error(f"Erro ao recuperar caminhos mapeados para atualização em segundo plano: {e}")
                finally:
                    pass # Connection is thread-local, do not close here

                if not mapped_paths:
                    indexer.logger.info("Nenhum caminho mapeado encontrado no banco de dados. Pulando ciclo de atualização.")
                    if not stop_event.is_set():
                        time.sleep(interval_seconds) # Still sleep to avoid busy-waiting
                    continue

                indexer.logger.info(f"Iniciando ciclo de atualização para {len(mapped_paths)} caminhos mapeados.")

                for network_path in mapped_paths:
                    if stop_event.is_set():
                        indexer.logger.info("Parando ciclo de atualização devido a evento de parada.")
                        break
                    
                    indexer.logger.info(f"Processando caminho: {network_path}...")
                    
                    try:
                        # Step 1: Get current file system state
                        current_fs_items = {}
                        if not os.path.exists(network_path):
                            indexer.logger.warning(f"Caminho '{network_path}' não encontrado no sistema de arquivos. Pulando atualização.")
                            # If a mapped path no longer exists, it should be removed from the DB
                            indexer.delete_record(network_path) 
                            continue

                        for root, dirs, files in os.walk(network_path):
                            if stop_event.is_set():
                                indexer.logger.info(f"Parando coleta de arquivos em {network_path} devido a evento de parada.")
                                break
                            for d in dirs:
                                full_path = os.path.join(root, d)
                                current_fs_items[full_path] = {
                                    'filename': d,
                                    'parent_path': str(Path(full_path).parent),
                                    'item_type': 'folder',
                                    'file_size': None,
                                    'modified_date': None
                                }
                            for f in files:
                                full_path = os.path.join(root, f)
                                try:
                                    stat = os.stat(full_path)
                                    current_fs_items[full_path] = {
                                        'filename': f,
                                        'parent_path': str(Path(full_path).parent),
                                        'item_type': 'file',
                                        'file_size': stat.st_size,
                                        'modified_date': time.ctime(stat.st_mtime)
                                    }
                                except (OSError, PermissionError) as e:
                                    indexer.logger.warning(f"Não foi possível obter metadados para {full_path}: {e}")
                                    continue
                        
                        if stop_event.is_set():
                            continue # Skip to next path or exit loop if stop event is set

                        # Step 2: Get current database state for the given network_path
                        db_items = {}
                        conn = indexer.get_db_connection()
                        cursor = conn.cursor()
                        try:
                            # Fetch only items that are children of the current network_path
                            cursor.execute("SELECT full_path, filename, parent_path, file_size, modified_date, item_type FROM files WHERE full_path LIKE ?", (f"{network_path}%",))
                            for row in cursor.fetchall():
                                db_items[row[0]] = {
                                    'filename': row[1],
                                    'parent_path': row[2],
                                    'file_size': row[3],
                                    'modified_date': row[4],
                                    'item_type': row[5]
                                }
                        except sqlite3.Error as e:
                            indexer.logger.error(f"Erro ao consultar o banco de dados para atualização de {network_path}: {e}")
                        finally:
                            pass # Connection is thread-local, do not close here

                        # Step 3: Compare and update
                        new_items = 0
                        updated_items = 0
                        deleted_items = 0

                        # Identify new and modified items
                        for fs_path, fs_data in current_fs_items.items():
                            if stop_event.is_set():
                                indexer.logger.info(f"Parando processamento de itens em {network_path} devido a evento de parada.")
                                break
                            if fs_path not in db_items:
                                indexer.insert_record(
                                    fs_data['filename'], fs_path, fs_data['parent_path'],
                                    fs_data['file_size'], fs_data['modified_date'], fs_data['item_type']
                                )
                                new_items += 1
                            else:
                                db_data = db_items[fs_path]
                                if fs_data['item_type'] == 'file' and (
                                   fs_data['file_size'] != db_data['file_size'] or
                                   fs_data['modified_date'] != db_data['modified_date']
                                ):
                                    indexer.update_record(
                                        fs_path, fs_data['file_size'], fs_data['modified_date']
                                    )
                                    updated_items += 1

                        # Identify deleted items
                        for db_path in db_items.keys():
                            if stop_event.is_set():
                                indexer.logger.info(f"Parando processamento de itens deletados em {network_path} devido a evento de parada.")
                                break
                            if db_path not in current_fs_items:
                                indexer.delete_record(db_path)
                                deleted_items += 1
                        
                        indexer.logger.info(f"Ciclo de atualização concluído para {network_path}. Novos: {new_items}, Atualizados: {updated_items}, Deletados: {deleted_items}")

                    except Exception as e:
                        indexer.logger.error(f"Erro inesperado no processo de atualização em segundo plano para {network_path}: {e}")
                
                if stop_event.is_set():
                    break # Exit the outer loop if stop event is set

            except Exception as e: # This is the missing except for the outer try block
                indexer.logger.error(f"Erro inesperado no ciclo principal de atualização em segundo plano: {e}")

            if not stop_event.is_set(): # Only sleep if not asked to stop
                time.sleep(interval_seconds)

        indexer.logger.info(f"Processo de atualização em segundo plano finalizado.")

    update_thread = threading.Thread(target=_run_update_cycle, daemon=True)
    update_thread.start()
    return update_thread, stop_event # Return thread and event for external control
