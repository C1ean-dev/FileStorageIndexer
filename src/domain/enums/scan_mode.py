"""
Scan Mode Enumeration

Defines the different modes available for scanning files.
"""

from enum import Enum


class ScanMode(Enum):
    """
    Enumeration for different scanning modes.
    
    STREAMING: Low memory usage, ideal for very large directories
    BATCH: Shows progress bar, better for medium-sized directories
    FOLDERS_ONLY: Scans only folders, not individual files
    """
    
    STREAMING = "streaming"
    BATCH = "batch"
    FOLDERS_ONLY = "folders_only"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def description(self) -> str:
        """Returns a human-readable description of the scan mode."""
        descriptions = {
            ScanMode.STREAMING: "Modo streaming - baixo uso de memória",
            ScanMode.BATCH: "Modo batch - barra de progresso determinada",
            ScanMode.FOLDERS_ONLY: "Apenas pastas - não indexa arquivos individuais"
        }
        return descriptions[self]