"""
TQDM Progress Reporter Implementation

Progress reporter implementation using the tqdm library.
"""

import time
import threading
from typing import Optional
from tqdm import tqdm

from src.application.interfaces.services.progress_reporter import ProgressReporter


class TqdmProgressReporter(ProgressReporter):
    """
    Progress reporter implementation using tqdm.
    
    Provides a visual progress bar with detailed information.
    """
    
    def __init__(self):
        """Initialize the TQDM progress reporter."""
        self._progress_bar: Optional[tqdm] = None
        self._start_time: Optional[float] = None
        self._is_finished = False
        self._is_paused = False
        self._current = 0
        self._total: Optional[int] = None
        self._description = "Processing"
        self._lock = threading.Lock()
    
    def start(self, total: Optional[int] = None, description: str = "Processing") -> None:
        """Start progress reporting with tqdm."""
        self._total = total
        self._description = description
        self._current = 0
        self._is_finished = False
        self._is_paused = False
        self._start_time = time.time()

        # Ensure total is not None for tqdm compatibility
        tqdm_total = total if total is not None else 0

        self._progress_bar = tqdm(
            total=tqdm_total,
            desc=description,
            unit="item",
            dynamic_ncols=True,
            miniters=1,
            leave=True,
            disable=False  # Ensure tqdm is enabled
        )
    
    def update(self, increment: int = 1, description: Optional[str] = None) -> None:
        """Update progress."""
        with self._lock:
            if self._progress_bar and not self._is_finished and not self._is_paused:
                self._current += increment
                self._progress_bar.update(increment)

                if description:
                    self._description = description
                    self._progress_bar.set_description(description)
    
    def set_progress(self, current: int, description: Optional[str] = None) -> None:
        """Set absolute progress value."""
        if self._progress_bar and not self._is_finished and not self._is_paused:
            # Calculate the difference to update by
            increment = current - self._current
            if increment > 0:
                self._current = current
                self._progress_bar.update(increment)
            
            if description:
                self._description = description
                self._progress_bar.set_description(description)
    
    def finish(self, message: Optional[str] = None) -> None:
        """Finish progress reporting."""
        with self._lock:
            if self._progress_bar and not self._is_finished:
                if message:
                    self._progress_bar.set_description(message)

                self._progress_bar.close()
                self._is_finished = True

                # Print completion message
                if message:
                    print(f"\n{message}")
    
    def set_total(self, total: int) -> None:
        """Set or update the total number of items."""
        self._total = total
        if self._progress_bar:
            # Ensure total is not None for tqdm compatibility
            tqdm_total = total if total is not None and total > 0 else 0
            self._progress_bar.total = tqdm_total
            self._progress_bar.refresh()
    
    def get_current(self) -> int:
        """Get current progress value."""
        return self._current
    
    def get_total(self) -> Optional[int]:
        """Get total number of items."""
        return self._total
    
    def get_percentage(self) -> Optional[float]:
        """Get completion percentage."""
        if self._total and self._total > 0:
            return (self._current / self._total) * 100.0
        return None
    
    def is_finished(self) -> bool:
        """Check if progress reporting has finished."""
        return self._is_finished
    
    def reset(self) -> None:
        """Reset progress to initial state."""
        if self._progress_bar:
            self._progress_bar.close()
        
        self._progress_bar = None
        self._current = 0
        self._is_finished = False
        self._is_paused = False
        self._start_time = None
    
    def pause(self) -> None:
        """Pause progress reporting."""
        self._is_paused = True
        if self._progress_bar:
            self._progress_bar.set_description(f"{self._description} (Pausado)")
    
    def resume(self) -> None:
        """Resume progress reporting."""
        self._is_paused = False
        if self._progress_bar:
            self._progress_bar.set_description(self._description)
    
    def is_paused(self) -> bool:
        """Check if progress reporting is paused."""
        return self._is_paused
    
    def set_postfix(self, **kwargs) -> None:
        """Set postfix information."""
        if self._progress_bar and not self._is_finished:
            self._progress_bar.set_postfix(**kwargs)
    
    def clear_postfix(self) -> None:
        """Clear postfix information."""
        if self._progress_bar and not self._is_finished:
            self._progress_bar.set_postfix()
    
    def write(self, message: str) -> None:
        """Write a message without interfering with progress display."""
        if self._progress_bar:
            self._progress_bar.write(message)
        else:
            print(message)
    
    def set_description(self, description: str) -> None:
        """Set the progress description."""
        self._description = description
        if self._progress_bar and not self._is_finished:
            self._progress_bar.set_description(description)
    
    def get_description(self) -> str:
        """Get the current progress description."""
        return self._description
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since start."""
        if self._start_time:
            return time.time() - self._start_time
        return 0.0
    
    def get_estimated_remaining_time(self) -> Optional[float]:
        """Get estimated remaining time."""
        if not self._total or self._current == 0 or self._is_finished:
            return None
        
        elapsed = self.get_elapsed_time()
        if elapsed == 0:
            return None
        
        rate = self._current / elapsed
        remaining_items = self._total - self._current
        
        if rate > 0:
            return remaining_items / rate
        
        return None
    
    def get_rate(self) -> Optional[float]:
        """Get processing rate (items per second)."""
        elapsed = self.get_elapsed_time()
        if elapsed > 0 and self._current > 0:
            return self._current / elapsed
        return None
    
    def close(self) -> None:
        """Close the progress reporter and clean up resources."""
        if not self._is_finished:
            self.finish()