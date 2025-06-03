import os
import sqlite3
import time
from pathlib import Path
from typing import List, Tuple, Optional
import argparse
import logging
import threading
from utils.updateRelease.updater import AppUpdater
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class FileIndexer:
    def __init__(self, db_path: str = "file_index.db", max_workers: int = 8):
        """
        Inicializa o indexador de arquivos
        
        Args:
            db_path: Caminho para o arquivo do banco de dados SQLite
            max_workers: Número máximo de threads para processamento paralelo
        """
        self.db_path = db_path
        self.max_workers = max_workers
        self.thread_local_db = threading.local() # Armazena a conexão do DB por thread
        self.setup_logging()
        self.setup_database_schema() # Apenas configura o esquema, não a conexão
    
    def setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('file_indexer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_db_connection(self):
        """Retorna uma conexão SQLite thread-local."""
        if not hasattr(self.thread_local_db, "conn"):
            self.thread_local_db.conn = sqlite3.connect(self.db_path)
            self.thread_local_db.conn.execute('PRAGMA journal_mode = WAL;')
            self.thread_local_db.conn.execute('PRAGMA synchronous = OFF;')
        return self.thread_local_db.conn

    def setup_database_schema(self):
        """Cria e configura o esquema do banco de dados SQLite (tabelas e índices)."""
        conn = sqlite3.connect(self.db_path) # Conexão temporária para setup
        cursor = conn.cursor()
        
        # Otimizações SQLite
        cursor.execute('PRAGMA journal_mode = WAL;')
        cursor.execute('PRAGMA synchronous = OFF;')
        
        # Criar tabela para armazenar informações dos arquivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                full_path TEXT NOT NULL UNIQUE,
                parent_path TEXT,
                file_size INTEGER,
                modified_date TEXT,
                item_type TEXT NOT NULL, -- 'file' or 'folder'
                indexed_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar índices para busca rápida
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_filename ON files(filename)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_full_path ON files(full_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_type ON files(item_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_parent_path ON files(parent_path)')
        
        conn.commit()
        conn.close() # Fechar a conexão temporária
        self.logger.info(f"Esquema do banco de dados configurado: {self.db_path}")
            
    def scan_network_folder(self, network_path: str, update_existing: bool = False):
        """
        Escaneia recursivamente uma pasta de rede e indexa todos os arquivos usando streaming
        
        Args:
            network_path: Caminho da pasta de rede (ex: \\192.168.7.209\bna)
            update_existing: Se True, atualiza registros existentes
        """
        self.logger.info(f"Iniciando escaneamento de: {network_path}")
        
        if not os.path.exists(network_path):
            self.logger.error(f"Caminho não encontrado: {network_path}")
            return
        
        # Limpar índice anterior se solicitado
        
        # Contadores e controle
        processed_files = 0
        errors = 0
        batch_data = []
        batch_size = 100
        
        # Queue para comunicação entre threads
        file_queue = Queue(maxsize=1000)  # Limitar tamanho da fila
        
        # Thread para coletar arquivos (producer)
        def file_collector():
            files_found_in_collector = 0
            try:
                for root, dirs, files in os.walk(network_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        file_queue.put((file, full_path))
                        files_found_in_collector += 1
                        if files_found_in_collector % 1000 == 0:
                            self.logger.info(f"Coletados {files_found_in_collector} arquivos na fila...")
                
            except Exception as e:
                self.logger.error(f"Erro durante coleta de arquivos: {e}")
            finally:
                # Sinalizar fim da coleta para todos os workers
                for _ in range(self.max_workers):
                    file_queue.put(None)
                self.logger.info(f"Coleta de arquivos finalizada. Total de arquivos encontrados pelo coletor: {files_found_in_collector}")
        
        # Iniciar thread de coleta
        collector_thread = threading.Thread(target=file_collector, daemon=True)
        collector_thread.start()
        
        # ThreadPool para processar arquivos (consumers)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create a list to hold futures
            futures = []
            
            # Create an indeterminate progress bar
            with tqdm(desc="Processando arquivos", unit="arquivo", 
                     dynamic_ncols=True, miniters=1) as pbar:
                
                # Submit tasks from the queue
                while True:
                    item = file_queue.get() # Blocking call
                    
                    if item is None: # Sentinel received
                        file_queue.task_done()
                        break # Exit loop for submitting tasks
                    
                    filename, full_path = item
                    futures.append(executor.submit(self.process_single_file, filename, full_path))
                    file_queue.task_done()
                
                # Process results as they complete
                for future in as_completed(futures):
                    try:
                        result = future.result() # This is the (filename, full_path, file_size, modified_date) tuple
                        if result:
                            batch_data.append(result)
                            processed_files += 1
                            
                            # Insert in batches for performance
                            if len(batch_data) >= batch_size:
                                self.insert_batch_records(batch_data)
                                batch_data = []
                        else:
                            errors += 1
                            # Error already logged by process_single_file if it failed due to OSError/PermissionError
                            
                    except Exception as e:
                        errors += 1
                        self.logger.error(f"Erro inesperado ao processar arquivo: {e}") # Cannot get original_full_path here easily
                    
                    pbar.update(1)
                
                # Insert last batch if there's remaining data
                if batch_data:
                    self.insert_batch_records(batch_data)
        
        # Ensure the collector thread has finished
        collector_thread.join()
        
        self.logger.info(f"Escaneamento concluído!")
        self.logger.info(f"Arquivos processados: {processed_files}")
        self.logger.info(f"Erros: {errors}")
        if processed_files > 0:
            self.logger.info(f"Taxa de sucesso: {(processed_files/(processed_files+errors))*100:.1f}%")
    
    def process_single_file(self, filename: str, full_path: str) -> Optional[Tuple]:
        """
        Processa um único arquivo e retorna suas informações
        
        Args:
            filename: Nome do arquivo
            full_path: Caminho completo do arquivo
            
        Returns:
            Tupla com (filename, full_path, file_size, modified_date) ou None se erro
        """
        try:
            # Obter informações do arquivo
            stat_info = os.stat(full_path)
            file_size = stat_info.st_size
            modified_date = time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(stat_info.st_mtime))
            
            return (filename, full_path, file_size, modified_date)
            
        except (OSError, PermissionError) as e:
            # Não logar cada erro individual para evitar spam nos logs
            return None

    def scan_network_folder_batch(self, network_path: str, update_existing: bool = False):
        """
        Versão alternativa que coleta todos os arquivos primeiro (para pastas pequenas/médias)
        Melhor quando você quer ver o total de arquivos e ter barra de progresso determinada
        """
        self.logger.info(f"Iniciando escaneamento em lote de: {network_path}")
        
        if not os.path.exists(network_path):
            self.logger.error(f"Caminho não encontrado: {network_path}")
            return
        
        
        # Coletar todos os arquivos primeiro
        self.logger.info("Coletando lista de arquivos...")
        all_files = []
        
        try:
            for root, dirs, files in os.walk(network_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    all_files.append((file, full_path))
                    
                    # Log a cada 10k arquivos coletados
                    if len(all_files) % 10000 == 0:
                        self.logger.info(f"Coletados {len(all_files)} arquivos...")
                        
        except Exception as e:
            self.logger.error(f"Erro ao coletar arquivos: {e}")
            return
        
        total_files = len(all_files)
        self.logger.info(f"Total de arquivos encontrados: {total_files}")
        
        if total_files == 0:
            self.logger.info("Nenhum arquivo encontrado para processar")
            return
        
        # Processar com barra de progresso determinada
        processed_files = 0
        errors = 0
        batch_data = []
        batch_size = 100
        
        with tqdm(total=total_files, desc="Processando arquivos", unit="arquivo") as pbar:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_file = {
                    executor.submit(self.process_single_file, filename, full_path): (filename, full_path)
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
                                self.insert_batch_records(batch_data)
                                batch_data = []
                        else:
                            errors += 1
                            
                    except Exception as e:
                        errors += 1
                        self.logger.debug(f"Erro ao processar {full_path}: {e}")
                    
                    pbar.update(1)
                
                if batch_data:
                    self.insert_batch_records(batch_data)
        
        # Limpar a lista da memória
        del all_files
        
        self.logger.info(f"Escaneamento concluído!")
        self.logger.info(f"Arquivos processados: {processed_files}")
        self.logger.info(f"Erros: {errors}")
        if processed_files > 0:
            self.logger.info(f"Taxa de sucesso: {(processed_files/(processed_files+errors))*100:.1f}%")
    
    def scan_network_folders(self, network_path: str):
        """
        Escaneia recursivamente uma pasta de rede e indexa apenas as pastas usando streaming.
        
        Args:
            network_path: Caminho da pasta de rede (ex: \\192.168.7.209\bna)
        """
        self.logger.info(f"Iniciando escaneamento de pastas em modo streaming: {network_path}")

        if not os.path.exists(network_path):
            self.logger.error(f"Caminho não encontrado: {network_path}")
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
                            self.logger.info(f"Coletadas {folders_found_in_collector} pastas na fila...")
            except Exception as e:
                self.logger.error(f"Erro durante coleta de pastas: {e}")
            finally:
                for _ in range(self.max_workers):
                    folder_queue.put(None)
                self.logger.info(f"Coleta de pastas finalizada. Total de pastas encontradas pelo coletor: {folders_found_in_collector}")

        collector_thread = threading.Thread(target=folder_collector, daemon=True)
        collector_thread.start()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            with tqdm(desc="Processando pastas", unit="pasta", dynamic_ncols=True, miniters=1) as pbar:
                while True:
                    item = folder_queue.get()
                    if item is None:
                        folder_queue.task_done()
                        break
                    
                    folder_name, full_path = item
                    futures.append(executor.submit(self._process_single_folder, folder_name, full_path))
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
                        self.logger.error(f"Erro inesperado ao processar pasta: {e}")
                    pbar.update(1)
        
        collector_thread.join()

        self.logger.info(f"Escaneamento de pastas concluído!")
        self.logger.info(f"Pastas processadas: {processed_folders}")
        self.logger.info(f"Erros: {errors}")
        if processed_folders > 0:
            self.logger.info(f"Taxa de sucesso: {(processed_folders/(processed_folders+errors))*100:.1f}%")

    def _process_single_folder(self, folder_name: str, full_path: str) -> bool:
        """
        Processa uma única pasta e a insere no banco de dados.
        
        Args:
            folder_name: Nome da pasta
            full_path: Caminho completo da pasta
            
        Returns:
            True se a pasta foi processada com sucesso, False caso contrário.
        """
        try:
            parent_path = str(Path(full_path).parent)
            self.insert_record(folder_name, full_path, parent_path, None, None, 'folder')
            return True
        except (OSError, PermissionError) as e:
            self.logger.warning(f"Não foi possível indexar a pasta {full_path}: {e}")
            return False

    def insert_batch_records(self, batch_data: List[Tuple]):
        """
        Insere um lote de registros de arquivos no banco de dados de forma thread-safe
        
        Args:
            batch_data: Lista de tuplas com dados dos arquivos (filename, full_path, file_size, modified_date)
        """
        records_to_insert = []
        for filename, full_path, file_size, modified_date in batch_data:
            parent_path = str(Path(full_path).parent)
            records_to_insert.append((filename, full_path, parent_path, file_size, modified_date, 'file'))

        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.executemany('''
                INSERT OR REPLACE INTO files 
                (filename, full_path, parent_path, file_size, modified_date, item_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', records_to_insert)
            conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao inserir lote de registros: {e}")
            raise
    
    def insert_record(self, filename: str, full_path: str, parent_path: Optional[str],
                      file_size: Optional[int], modified_date: Optional[str], item_type: str):
        """
        Insere um registro (arquivo ou pasta) no banco de dados
        
        Args:
            filename: Nome do arquivo/pasta
            full_path: Caminho completo do arquivo/pasta
            parent_path: Caminho da pasta pai
            file_size: Tamanho do arquivo em bytes (None para pastas)
            modified_date: Data de modificação (None para pastas)
            item_type: Tipo do item ('file' ou 'folder')
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO files 
                (filename, full_path, parent_path, file_size, modified_date, item_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, full_path, parent_path, file_size, modified_date, item_type))
            conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao inserir registro: {e}")
            raise

    def insert_file_record(self, filename: str, full_path: str, 
                          file_size: int, modified_date: str):
        """
        Insere um registro de arquivo no banco de dados (mantido para compatibilidade, mas usa insert_record)
        
        Args:
            filename: Nome do arquivo
            full_path: Caminho completo do arquivo
            file_size: Tamanho do arquivo em bytes
            modified_date: Data de modificação do arquivo
        """
        parent_path = str(Path(full_path).parent)
        self.insert_record(filename, full_path, parent_path, file_size, modified_date, 'file')
    
    def search_files(self, search_term: str, exact_match: bool = False) -> List[Tuple]:
        """
        Busca arquivos por nome
        
        Args:
            search_term: Termo de busca
            exact_match: Se True, busca exata. Se False, busca parcial
            
        Returns:
            Lista de tuplas com (filename, full_path, file_size, modified_date)
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            if exact_match:
                query = "SELECT filename, full_path, file_size, modified_date FROM files WHERE filename = ? AND item_type = 'file'"
                cursor.execute(query, (search_term,))
            else:
                query = "SELECT filename, full_path, file_size, modified_date FROM files WHERE filename LIKE ? AND item_type = 'file'"
                cursor.execute(query, (f"%{search_term}%",))
            
            results = cursor.fetchall()
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro na busca: {e}")
            return []
    
    def search_by_extension(self, extension: str) -> List[Tuple]:
        """
        Busca arquivos por extensão
        
        Args:
            extension: Extensão do arquivo (ex: .pdf, .docx)
            
        Returns:
            Lista de tuplas com informações dos arquivos
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            if not extension.startswith('.'):
                extension = '.' + extension
            
            query = "SELECT filename, full_path, file_size, modified_date FROM files WHERE filename LIKE ? AND item_type = 'file'"
            cursor.execute(query, (f"%{extension}",))
            
            results = cursor.fetchall()
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro na busca por extensão: {e}")
            return []
    
    def search_folders(self, search_term: str, exact_match: bool = False) -> List[Tuple]:
        """
        Busca pastas por nome
        
        Args:
            search_term: Termo de busca
            exact_match: Se True, busca exata. Se False, busca parcial
            
        Returns:
            Lista de tuplas com (filename, full_path, parent_path)
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            if exact_match:
                query = "SELECT filename, full_path, parent_path FROM files WHERE filename = ? AND item_type = 'folder'"
                cursor.execute(query, (search_term,))
            else:
                query = "SELECT filename, full_path, parent_path FROM files WHERE filename LIKE ? AND item_type = 'folder'"
                cursor.execute(query, (f"%{search_term}%",))
            
            results = cursor.fetchall()
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro na busca de pastas: {e}")
            return []

    def get_stats(self) -> dict:
        """
        Retorna estatísticas do índice
        
        Returns:
            Dicionário com estatísticas
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Total de arquivos
            cursor.execute("SELECT COUNT(*) FROM files WHERE item_type = 'file'")
            total_files = cursor.fetchone()[0]
            
            # Total de pastas
            cursor.execute("SELECT COUNT(*) FROM files WHERE item_type = 'folder'")
            total_folders = cursor.fetchone()[0]
            
            # Tamanho total de arquivos
            cursor.execute("SELECT SUM(file_size) FROM files WHERE item_type = 'file'")
            total_size = cursor.fetchone()[0] or 0
            
            # Extensões mais comuns
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
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def clear_index(self):
        """Limpa todos os registros do índice"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM files")
            conn.commit()
            self.logger.info("Índice limpo com sucesso")
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao limpar índice: {e}")
    
    def close(self):
        """Fecha a conexão com o banco de dados para a thread atual."""
        if hasattr(self.thread_local_db, "conn") and self.thread_local_db.conn:
            self.thread_local_db.conn.close()
            del self.thread_local_db.conn
            self.logger.info("Conexão com banco de dados da thread atual fechada")

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

def main():
    parser = argparse.ArgumentParser(description='Indexador de Arquivos de Rede')
    parser.add_argument('--scan', type=str, help='Caminho da pasta de rede para escanear')
    parser.add_argument('--search', type=str, help='Buscar arquivo por nome')
    parser.add_argument('--extension', type=str, help='Buscar por extensão')
    parser.add_argument('--exact', action='store_true', help='Busca exata')
    parser.add_argument('--stats', action='store_true', help='Mostrar estatísticas')
    parser.add_argument('--clear', action='store_true', help='Limpar índice')
    parser.add_argument('--db', type=str, default='file_index.db', help='Caminho do banco de dados')
    parser.add_argument('--workers', type=int, default=8, help='Número de threads para processamento (padrão: 8)')
    parser.add_argument('--streaming', action='store_true', help='Usar modo streaming (melhor para pastas muito grandes)')
    parser.add_argument('--batch', action='store_true', help='Usar modo batch com barra de progresso determinada (padrão)')
    parser.add_argument('--scan-folders', type=str, help='Caminho da pasta de rede para escanear apenas pastas')
    parser.add_argument('--search-folders', type=str, help='Buscar pasta por nome')
    
    args = parser.parse_args()
    
    # Inicializar indexador
    indexer = FileIndexer(args.db, max_workers=args.workers)
    
    try:
        if args.scan:
            print(f"Escaneando pasta: {args.scan}")
            
            # Escolher método baseado nos argumentos
            if args.streaming:
                print("Usando modo streaming (baixo uso de memória)")
                indexer.scan_network_folder(args.scan, update_existing=False)
            else:
                print("Usando modo batch (barra de progresso determinada)")
                indexer.scan_network_folder_batch(args.scan, update_existing=False)
        
        elif args.scan_folders:
            print(f"Escaneando apenas pastas em: {args.scan_folders}")
            indexer.scan_network_folders(args.scan_folders)
            
        elif args.search:
            print(f"Buscando por arquivo: {args.search}")
            results = indexer.search_files(args.search, args.exact)
            
            if results:
                print(f"\nEncontrados {len(results)} arquivo(s):")
                print("-" * 80)
                for filename, full_path, file_size, modified_date in results:
                    print(f"Arquivo: {filename}")
                    print(f"Caminho: {full_path}")
                    print(f"Tamanho: {format_file_size(file_size)}")
                    print(f"Modificado: {modified_date}")
                    print("-" * 80)
            else:
                print("Nenhum arquivo encontrado.")
        
        elif args.search_folders:
            print(f"Buscando por pasta: {args.search_folders}")
            results = indexer.search_folders(args.search_folders, args.exact)
            
            if results:
                print(f"\nEncontradas {len(results)} pasta(s):")
                print("-" * 80)
                for folder_name, full_path, parent_path in results:
                    print(f"Pasta: {folder_name}")
                    print(f"Caminho: {full_path}")
                    print(f"Pasta Pai: {parent_path}")
                    print("-" * 80)
            else:
                print("Nenhuma pasta encontrada.")
                
        elif args.extension:
            print(f"Buscando arquivos com extensão: {args.extension}")
            results = indexer.search_by_extension(args.extension)
            
            if results:
                print(f"\nEncontrados {len(results)} arquivo(s):")
                print("-" * 80)
                for filename, full_path, file_size, modified_date in results:
                    print(f"Arquivo: {filename}")
                    print(f"Caminho: {full_path}")
                    print(f"Tamanho: {format_file_size(file_size)}")
                    print(f"Modificado: {modified_date}")
                    print("-" * 80)
            else:
                print("Nenhum arquivo encontrado.")
                
        elif args.stats:
            stats = indexer.get_stats()
            print("\n=== ESTATÍSTICAS DO ÍNDICE ===")
            print(f"Total de arquivos: {stats.get('total_files', 0):,}")
            print(f"Total de pastas: {stats.get('total_folders', 0):,}")
            print(f"Tamanho total de arquivos: {stats.get('total_size_mb', 0):,.2f} MB")
            print("\nExtensões mais comuns:")
            for ext, count in stats.get('top_extensions', []):
                print(f"  {ext}: {count:,} arquivos")
                
        elif args.clear:
            confirm = input("Tem certeza que deseja limpar o índice? (s/N): ")
            if confirm.lower() == 's':
                indexer.clear_index()
                print("Índice limpo com sucesso.")
            else:
                print("Operação cancelada.")
                
        else:
            print("Use --help para ver as opções disponíveis")
            
    finally:
        indexer.close()

if __name__ == "__main__":
    # Exemplo de uso interativo se executado diretamente
    if len(os.sys.argv) == 1:
        # Initialize and check for updates
        current_app_version = "0.0.0-dev" # Default to development version
        try:
            import version
            current_app_version = version.__version__
            # Only run updater if a proper version is found (i.e., not in local dev)
            self.updater = AppUpdater(
                repo_owner="C1ean-dev", 
                repo_name="FileStorageIndexer", 
                current_version=current_app_version
            )
            self.updater.check_for_updates()
        except ImportError:
            print("Warning: version.py not found. Running in development mode, update checks skipped.")
            # No updater initialized if in development mode

        print("=== INDEXADOR DE ARQUIVOS DE REDE ===\n")
        
        workers = input("Número de threads para processamento (padrão 8): ").strip()
        max_workers = int(workers) if workers.isdigit() else 8
        
        indexer = FileIndexer(max_workers=max_workers)
        
        try:
            while True:
                print("\nOpções:")
                print("1. Escanear pasta de rede (Streaming - muito recomendado)")
                print("2. Escanear pasta de rede (Batch - progresso determinado)")
                print("3. Buscar arquivo")
                print("4. Buscar por extensão") 
                print("5. Mostrar estatísticas")
                print("6. Limpar índice")
                print("7. Escanear apenas pastas")
                print("8. Buscar pasta")
                print("0. Sair")
                
                choice = input("\nEscolha uma opção: ").strip()
                
                if choice == "1":
                    path = input("Digite o caminho da pasta de rede: ").strip()
                    if path:
                        print("Usando modo streaming (baixo uso de memória)")
                        indexer.scan_network_folder(path, update_existing=False)
                        
                elif choice == "2":
                    path = input("Digite o caminho da pasta de rede: ").strip()
                    if path:
                        print("Usando modo batch (barra de progresso determinada)")
                        indexer.scan_network_folder_batch(path, update_existing=False)
                        
                elif choice == "3":
                    search_term = input("Digite o nome do arquivo: ").strip()
                    if search_term:
                        results = indexer.search_files(search_term)
                        if results:
                            print(f"\nEncontrados {len(results)} arquivo(s):")
                            for filename, full_path, file_size, modified_date in results:
                                print(f"\nArquivo: {filename}")
                                print(f"Caminho: {full_path}")
                                print(f"Tamanho: {format_file_size(file_size)}")
                        else:
                            print("Nenhum arquivo encontrado.")
                            
                elif choice == "4":
                    ext = input("Digite a extensão (ex: pdf, docx): ").strip()
                    if ext:
                        results = indexer.search_by_extension(ext)
                        if results:
                            print(f"\nEncontrados {len(results)} arquivo(s) com extensão .{ext}")
                            current_display_index = 0
                            while True:
                                for filename, full_path, file_size, modified_date in results[current_display_index:current_display_index + 10]:
                                    print(f"  {filename} - {full_path}")
                                
                                current_display_index += 10
                                
                                if current_display_index >= len(results):
                                    print("\nTodos os arquivos foram listados.")
                                    break
                                
                                remaining_files = len(results) - current_display_index
                                print(f"  ... e mais {remaining_files} arquivos")
                                
                                while True:
                                    action = input("\nOpções:\n1. Listar mais 10 arquivos\n2. Baixar lista completa (TXT)\n3. Voltar ao menu\nEscolha uma opção: ").strip()
                                    if action == "1":
                                        break  # Continue o loop externo para listar mais
                                    elif action == "2":
                                        output_filename = input("Digite o nome do arquivo TXT para salvar (ex: resultados.txt): ").strip()
                                        if not output_filename:
                                            output_filename = "resultados_busca.txt"
                                        
                                        try:
                                            with open(output_filename, "w", encoding="utf-8") as f:
                                                for filename, full_path, file_size, modified_date in results:
                                                    f.write(f"Arquivo: {filename}\n")
                                                    f.write(f"Caminho: {full_path}\n")
                                                    f.write(f"Tamanho: {format_file_size(file_size)}\n")
                                                    f.write(f"Modificado: {modified_date}\n")
                                                    f.write("-" * 80 + "\n")
                                            print(f"Lista salva em '{output_filename}' com sucesso.")
                                        except IOError as e:
                                            print(f"Erro ao salvar arquivo: {e}")
                                        break # Voltar ao menu principal após salvar
                                    elif action == "3":
                                        break # Voltar ao menu principal
                                    else:
                                        print("Opção inválida. Tente novamente.")
                                if action == "2" or action == "3":
                                    break # Sair do loop principal se o usuário escolheu salvar ou voltar
                        else:
                            print("Nenhum arquivo encontrado.")
                            
                elif choice == "5":
                    stats = indexer.get_stats()
                    print("\n=== ESTATÍSTICAS DO ÍNDICE ===")
                    print(f"Total de arquivos: {stats.get('total_files', 0):,}")
                    print(f"Total de pastas: {stats.get('total_folders', 0):,}")
                    print(f"Tamanho total de arquivos: {stats.get('total_size_mb', 0):,.2f} MB")
                    print("\nExtensões mais comuns:")
                    for ext, count in stats.get('top_extensions', []):
                        print(f"  {ext}: {count:,} arquivos")
                        
                elif choice == "6":
                    confirm = input("Tem certeza? (s/N): ")
                    if confirm.lower() == 's':
                        indexer.clear_index()
                        
                elif choice == "7":
                    path = input("Digite o caminho da pasta de rede para escanear pastas: ").strip()
                    if path:
                        indexer.scan_network_folders(path)
                
                elif choice == "8":
                    search_term = input("Digite o nome da pasta: ").strip()
                    if search_term:
                        results = indexer.search_folders(search_term)
                        if results:
                            print(f"\nEncontradas {len(results)} pasta(s):")
                            for folder_name, full_path, parent_path in results:
                                print(f"\nPasta: {folder_name}")
                                print(f"Caminho: {full_path}")
                                print(f"Pasta Pai: {parent_path}")
                        else:
                            print("Nenhuma pasta encontrada.")
                            
                elif choice == "0":
                    break
                    
        finally:
            indexer.close()
    else:
        main()
