import os
import time
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def scan_network_folder_func(indexer, network_path: str, update_existing: bool = False):
    indexer.logger.info(f"Iniciando escaneamento de: {network_path}")
    
    if not os.path.exists(network_path):
        indexer.logger.error(f"Caminho não encontrado: {network_path}")
        return
    
    processed_files = 0
    errors = 0
    batch_data = []
    batch_size = 100
    
    file_queue = Queue(maxsize=1000)
    
    def file_collector():
        files_found_in_collector = 0
        try:
            for root, dirs, files in os.walk(network_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    file_queue.put((file, full_path))
                    files_found_in_collector += 1
                    if files_found_in_collector % 1000 == 0:
                        indexer.logger.info(f"Coletados {files_found_in_collector} arquivos na fila...")
            
        except Exception as e:
            indexer.logger.error(f"Erro durante coleta de arquivos: {e}")
        finally:
            for _ in range(indexer.max_workers):
                file_queue.put(None)
            indexer.logger.info(f"Coleta de arquivos finalizada. Total de arquivos encontrados pelo coletor: {files_found_in_collector}")
    
    collector_thread = threading.Thread(target=file_collector, daemon=True)
    collector_thread.start()
    
    with ThreadPoolExecutor(max_workers=indexer.max_workers) as executor:
        futures = []
        
        with tqdm(desc="Processando arquivos", unit="arquivo", 
                 dynamic_ncols=True, miniters=1) as pbar:
            
            while True:
                item = file_queue.get()
                
                if item is None:
                    file_queue.task_done()
                    break
                
                filename, full_path = item
                futures.append(executor.submit(indexer.process_single_file, filename, full_path))
                file_queue.task_done()
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        batch_data.append(result)
                        processed_files += 1
                        
                        if len(batch_data) >= batch_size:
                            indexer.insert_batch_records(batch_data)
                            batch_data = []
                    else:
                        errors += 1
                        
                except Exception as e:
                    errors += 1
                    indexer.logger.error(f"Erro inesperado ao processar arquivo: {e}")
                
                pbar.update(1)
            
            if batch_data:
                indexer.insert_batch_records(batch_data)
    
    collector_thread.join()
    
    indexer.logger.info(f"Escaneamento concluído!")
    indexer.logger.info(f"Arquivos processados: {processed_files}")
    indexer.logger.info(f"Erros: {errors}")
    if processed_files > 0:
        indexer.logger.info(f"Taxa de sucesso: {(processed_files/(processed_files+errors))*100:.1f}%")
