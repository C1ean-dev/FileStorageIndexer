import os
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def scan_network_folders_func(indexer, network_path: str):
    indexer.logger.info(f"Iniciando escaneamento de pastas em modo streaming: {network_path}")

    if not os.path.exists(network_path):
        indexer.logger.error(f"Caminho não encontrado: {network_path}")
        return

    processed_folders = 0
    errors = 0
    
    folder_queue = Queue(maxsize=1000)

    def folder_collector():
        folders_found_in_collector = 0
        try:
            for root, dirs, files in os.walk(network_path):
                for d in dirs:
                    full_path = os.path.join(root, d)
                    folder_queue.put((d, full_path))
                    folders_found_in_collector += 1
                    if folders_found_in_collector % 1000 == 0:
                        indexer.logger.info(f"Coletadas {folders_found_in_collector} pastas na fila...")
        except Exception as e:
            indexer.logger.error(f"Erro durante coleta de pastas: {e}")
        finally:
            for _ in range(indexer.max_workers):
                folder_queue.put(None)
            indexer.logger.info(f"Coleta de pastas finalizada. Total de pastas encontradas pelo coletor: {folders_found_in_collector}")

    collector_thread = threading.Thread(target=folder_collector, daemon=True)
    collector_thread.start()

    with ThreadPoolExecutor(max_workers=indexer.max_workers) as executor:
        futures = []
        with tqdm(desc="Processando pastas", unit="pasta", dynamic_ncols=True, miniters=1) as pbar:
            while True:
                item = folder_queue.get()
                if item is None:
                    folder_queue.task_done()
                    break
                
                folder_name, full_path = item
                futures.append(executor.submit(indexer._process_single_folder, folder_name, full_path))
                folder_queue.task_done()
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        processed_folders += 1
                    else:
                        errors += 1
                except Exception as e:
                    errors += 1
                    indexer.logger.error(f"Erro inesperado ao processar pasta: {e}")
                pbar.update(1)
    
    collector_thread.join()

    indexer.logger.info(f"Escaneamento de pastas concluído!")
    indexer.logger.info(f"Pastas processadas: {processed_folders}")
    indexer.logger.info(f"Erros: {errors}")
    if processed_folders > 0:
        indexer.logger.info(f"Taxa de sucesso: {(processed_folders/(processed_folders+errors))*100:.1f}%")
