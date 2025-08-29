"""
Scan Request DTO

Data Transfer Object for scan operation requests.
"""

from dataclasses import dataclass
from typing import Optional

from src.domain.enums.scan_mode import ScanMode


@dataclass
class ScanRequest:
    """
    DTO for scan operation requests.
    
    Contains all parameters needed to perform a scan operation.
    """
    
    path: str
    scan_mode: ScanMode = ScanMode.STREAMING
    update_existing: bool = False
    max_workers: Optional[int] = None
    include_hidden: bool = False
    include_system: bool = False
    
    def __post_init__(self):
        """Validate the request after initialization."""
        if not self.path or not self.path.strip():
            raise ValueError("Path cannot be empty")
        
        if self.max_workers is not None and self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
    
    @property
    def normalized_path(self) -> str:
        """Get the normalized path."""
        return self.path.strip()
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'path': self.path,
            'scan_mode': self.scan_mode.value,
            'update_existing': self.update_existing,
            'max_workers': self.max_workers,
            'include_hidden': self.include_hidden,
            'include_system': self.include_system
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScanRequest':
        """Create from dictionary representation."""
        scan_mode = ScanMode(data.get('scan_mode', ScanMode.STREAMING.value))
        
        return cls(
            path=data['path'],
            scan_mode=scan_mode,
            update_existing=data.get('update_existing', False),
            max_workers=data.get('max_workers'),
            include_hidden=data.get('include_hidden', False),
            include_system=data.get('include_system', False)
        )