import logging

def setup_logging_func(indexer):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('file_indexer.log')
        ]
    )
    # Configure StreamHandler to only show WARNING level messages or higher
    # on the console, keeping INFO messages only in the log file.
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING) # Set level for the stream handler
    logging.getLogger().addHandler(stream_handler) # Add the stream handler to the root logger

    indexer.logger = logging.getLogger(__name__)
