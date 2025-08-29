"""
Console Logger Implementation

Simple logger that outputs to console/stdout.
"""

import sys
from datetime import datetime
from typing import Optional, Dict, Any

from src.application.interfaces.services.logger import Logger, LogLevel


class ConsoleLogger(Logger):
    """
    Simple console logger implementation.
    
    Outputs log messages to stdout/stderr with timestamps and level indicators.
    """
    
    def __init__(self, level: LogLevel = LogLevel.INFO):
        """
        Initialize the console logger.
        
        Args:
            level: Minimum log level to output
        """
        self._level = level
        self._context = {}
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a debug message."""
        if self.is_enabled_for(LogLevel.DEBUG):
            self._log_message(LogLevel.DEBUG, message, extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log an info message."""
        if self.is_enabled_for(LogLevel.INFO):
            self._log_message(LogLevel.INFO, message, extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a warning message."""
        if self.is_enabled_for(LogLevel.WARNING):
            self._log_message(LogLevel.WARNING, message, extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log an error message."""
        if self.is_enabled_for(LogLevel.ERROR):
            self._log_message(LogLevel.ERROR, message, extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a critical message."""
        if self.is_enabled_for(LogLevel.CRITICAL):
            self._log_message(LogLevel.CRITICAL, message, extra)
    
    def log(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a message at the specified level."""
        if self.is_enabled_for(level):
            self._log_message(level, message, extra)
    
    def exception(self, message: str, exc_info: Optional[Exception] = None) -> None:
        """Log an exception."""
        self._log_message(LogLevel.ERROR, f"EXCEPTION: {message}", None)
        if exc_info:
            self._log_message(LogLevel.ERROR, f"Exception details: {str(exc_info)}", None)
    
    def _log_message(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Internal method to format and output log messages."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_str = level.value.ljust(8)
        
        # Combine context and extra data
        combined_extra = {**self._context, **(extra or {})}
        extra_str = ""
        if combined_extra:
            extra_parts = [f"{k}={v}" for k, v in combined_extra.items()]
            extra_str = f" [{', '.join(extra_parts)}]"
        
        formatted_message = f"{timestamp} {level_str} {message}{extra_str}"
        
        # Output to appropriate stream
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            print(formatted_message, file=sys.stderr)
        else:
            print(formatted_message, file=sys.stdout)
    
    def set_level(self, level: LogLevel) -> None:
        """Set the minimum logging level."""
        self._level = level
    
    def get_level(self) -> LogLevel:
        """Get the current logging level."""
        return self._level
    
    def is_enabled_for(self, level: LogLevel) -> bool:
        """Check if logging is enabled for the given level."""
        level_values = {
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.WARNING: 30,
            LogLevel.ERROR: 40,
            LogLevel.CRITICAL: 50
        }
        
        return level_values.get(level, 0) >= level_values.get(self._level, 20)
    
    def add_context(self, **kwargs) -> None:
        """Add persistent context information."""
        self._context.update(kwargs)
    
    def remove_context(self, *keys) -> None:
        """Remove context information."""
        for key in keys:
            self._context.pop(key, None)
    
    def clear_context(self) -> None:
        """Clear all context information."""
        self._context.clear()
    
    def flush(self) -> None:
        """Flush output streams."""
        sys.stdout.flush()
        sys.stderr.flush()
    
    def close(self) -> None:
        """Close the logger (no-op for console logger)."""
        pass