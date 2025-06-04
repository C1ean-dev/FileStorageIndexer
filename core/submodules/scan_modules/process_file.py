import os
import time
from typing import Optional, Tuple

def process_single_file_func(indexer, filename: str, full_path: str) -> Optional[Tuple]:
    try:
        stat_info = os.stat(full_path)
        file_size = stat_info.st_size
        modified_date = time.strftime('%Y-%m-%d %H:%M:%S', 
                                    time.localtime(stat_info.st_mtime))
        
        return (filename, full_path, file_size, modified_date)
        
    except (OSError, PermissionError) as e:
        return None
