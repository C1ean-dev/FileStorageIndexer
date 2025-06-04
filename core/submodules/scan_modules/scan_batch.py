import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def scan_network_folder_batch_func(indexer, network_path: str, update_existing: bool = False):
    indexer.logger.info(f"Iniciando escaneamento em lote de: {network_path}")
    
    if not os.path.exists(network_path):
        indexer.logger.error(f"Caminho não encontrado: {network_path}")
        return
    
    indexer.logger.info("Coletando lista de arquivos...")
    all_files = []
    
    try:
        for root, dirs, files in os.walk(network_path):
            for file in files:
                full_path = os.path.join(root, file)
                all_files.append((file, full_path))
                
                if len(all_files) % 10000 == 0:
                    indexer.logger.info(f"Coletados {len(all_files)} arquivos...")
                    
    except Exception as e:
        indexer.logger.error(f"Erro ao coletar arquivos: {e}")
        return
    
    total_files = len(all_files)
    indexer.logger.info(f"Total de arquivos encontrados: {total_files}")
    
    if total_files == 0:
        indexer.logger.info("Nenhum arquivo encontrado para processar")
        return
    
    processed_files = 0
    errors = 0
    batch_data = []
    batch_size = 100
    
    with tqdm(total=total_files, desc="Processando arquivos", unit="arquivo") as pbar:
        with ThreadPoolExecutor(max_workers=indexer.max_workers) as executor:
            future_to_file = {
                executor.submit(indexer.process_single_file, filename, full_path): (filename, full_path)
                for filename, full_path in all_files
            }
            
            for future in as_completed(future_to_file):
                filename, full_path = future_to_file[future]
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
                    indexer.logger.debug(f"Erro ao processar {full_path}: {e}")
                
                pbar.update(1)
            
            if batch_data:
                indexer.insert_batch_records(batch_data)
    
    del all_files
    
    indexer.logger.info(f"Escaneamento concluído!")
    indexer.logger.info(f"Arquivos processados: {processed_files}")
    indexer.logger.info(f"Erros: {errors}")
    if processed_files > 0:
        indexer.logger.info(f"Taxa de sucesso: {(processed_files/(processed_files+errors))*100:.1f}%")
