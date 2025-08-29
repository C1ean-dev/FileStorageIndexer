"""
Logger Interface

Defines the contract for logging operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger(ABC):
    """
    Abstract interface for logging operations.
    
    This interface defines the contract that infrastructure implementations
    must follow for logging functionality.
    """
    
    @abstractmethod
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a debug message.
        
        Args:
            message: The message to log
            extra: Optional extra context information
        """
        pass
    
    @abstractmethod
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an info message.
        
        Args:
            message: The message to log
            extra: Optional extra context information
        """
        pass
    
    @abstractmethod
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a warning message.
        
        Args:
            message: The message to log
            extra: Optional extra context information
        """
        pass
    
    @abstractmethod
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error message.
        
        Args:
            message: The message to log
            extra: Optional extra context information
        """
        pass
    
    @abstractmethod
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a critical message.
        
        Args:
            message: The message to log
            extra: Optional extra context information
        """
        pass
    
    @abstractmethod
    def log(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a message at the specified level.
        
        Args:
            level: The log level
            message: The message to log
            extra: Optional extra context information
        """
        pass
    
    @abstractmethod
    def exception(self, message: str, exc_info: Optional[Exception] = None) -> None:
        """
        Log an exception with traceback information.
        
        Args:
            message: The message to log
            exc_info: Optional exception information
        """
        pass
    
    @abstractmethod
    def set_level(self, level: LogLevel) -> None:
        """
        Set the minimum logging level.
        
        Args:
            level: The minimum log level to record
        """
        pass
    
    @abstractmethod
    def get_level(self) -> LogLevel:
        """
        Get the current logging level.
        
        Returns:
            Current log level
        """
        pass
    
    @abstractmethod
    def is_enabled_for(self, level: LogLevel) -> bool:
        """
        Check if logging is enabled for the given level.
        
        Args:
            level: Log level to check
            
        Returns:
            True if logging is enabled for this level
        """
        pass
    
    @abstractmethod
    def add_context(self, **kwargs) -> None:
        """
        Add persistent context information to all log messages.
        
        Args:
            **kwargs: Context key-value pairs
        """
        pass
    
    @abstractmethod
    def remove_context(self, *keys) -> None:
        """
        Remove context information.
        
        Args:
            *keys: Context keys to remove
        """
        pass
    
    @abstractmethod
    def clear_context(self) -> None:
        """Clear all context information."""
        pass
    
    @abstractmethod
    def flush(self) -> None:
        """Flush any buffered log messages."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the logger and release resources."""
        pass