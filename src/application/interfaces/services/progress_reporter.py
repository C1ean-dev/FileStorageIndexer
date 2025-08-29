"""
Progress Reporter Interface

Defines the contract for progress reporting operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict


class ProgressReporter(ABC):
    """
    Abstract interface for progress reporting operations.
    
    This interface defines the contract that infrastructure implementations
    must follow for progress reporting functionality.
    """
    
    @abstractmethod
    def start(self, total: Optional[int] = None, description: str = "Processing") -> None:
        """
        Start progress reporting.
        
        Args:
            total: Total number of items to process (None for indeterminate)
            description: Description of the operation
        """
        pass
    
    @abstractmethod
    def update(self, increment: int = 1, description: Optional[str] = None) -> None:
        """
        Update progress.
        
        Args:
            increment: Number of items processed since last update
            description: Optional updated description
        """
        pass
    
    @abstractmethod
    def set_progress(self, current: int, description: Optional[str] = None) -> None:
        """
        Set absolute progress value.
        
        Args:
            current: Current progress value
            description: Optional updated description
        """
        pass
    
    @abstractmethod
    def finish(self, message: Optional[str] = None) -> None:
        """
        Finish progress reporting.
        
        Args:
            message: Optional completion message
        """
        pass
    
    @abstractmethod
    def set_total(self, total: int) -> None:
        """
        Set or update the total number of items.
        
        Args:
            total: Total number of items to process
        """
        pass
    
    @abstractmethod
    def get_current(self) -> int:
        """
        Get current progress value.
        
        Returns:
            Current progress value
        """
        pass
    
    @abstractmethod
    def get_total(self) -> Optional[int]:
        """
        Get total number of items.
        
        Returns:
            Total number of items, or None if indeterminate
        """
        pass
    
    @abstractmethod
    def get_percentage(self) -> Optional[float]:
        """
        Get completion percentage.
        
        Returns:
            Completion percentage (0.0-100.0), or None if indeterminate
        """
        pass
    
    @abstractmethod
    def is_finished(self) -> bool:
        """
        Check if progress reporting has finished.
        
        Returns:
            True if finished
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset progress to initial state."""
        pass
    
    @abstractmethod
    def pause(self) -> None:
        """Pause progress reporting."""
        pass
    
    @abstractmethod
    def resume(self) -> None:
        """Resume progress reporting."""
        pass
    
    @abstractmethod
    def is_paused(self) -> bool:
        """
        Check if progress reporting is paused.
        
        Returns:
            True if paused
        """
        pass
    
    @abstractmethod
    def set_postfix(self, **kwargs) -> None:
        """
        Set postfix information (additional details).
        
        Args:
            **kwargs: Key-value pairs for postfix information
        """
        pass
    
    @abstractmethod
    def clear_postfix(self) -> None:
        """Clear postfix information."""
        pass
    
    @abstractmethod
    def write(self, message: str) -> None:
        """
        Write a message without interfering with progress display.
        
        Args:
            message: Message to write
        """
        pass
    
    @abstractmethod
    def set_description(self, description: str) -> None:
        """
        Set the progress description.
        
        Args:
            description: New description
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the current progress description.
        
        Returns:
            Current description
        """
        pass
    
    @abstractmethod
    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since start.
        
        Returns:
            Elapsed time in seconds
        """
        pass
    
    @abstractmethod
    def get_estimated_remaining_time(self) -> Optional[float]:
        """
        Get estimated remaining time.
        
        Returns:
            Estimated remaining time in seconds, or None if unknown
        """
        pass
    
    @abstractmethod
    def get_rate(self) -> Optional[float]:
        """
        Get processing rate (items per second).
        
        Returns:
            Processing rate, or None if unknown
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the progress reporter and clean up resources."""
        pass