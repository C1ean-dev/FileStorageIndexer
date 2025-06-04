import logging

def setup_logging_func(indexer):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('file_indexer.log'),
            logging.StreamHandler()
        ]
    )
    indexer.logger = logging.getLogger(__name__)
