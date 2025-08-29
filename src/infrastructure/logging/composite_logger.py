"""
Composite Logger Implementation

Logger that combines multiple logging implementations.
"""

from typing import List, Optional, Dict, Any

from src.application.interfaces.services.logger import Logger, LogLevel


class CompositeLogger(Logger):
    """
    Composite logger that delegates to multiple logger implementations.
    
    Allows combining file logging, console logging, etc.
    """
    
    def __init__(self, loggers: List[Logger]):
        """
        Initialize the composite logger.
        
        Args:
            loggers: List of logger implementations to combine
        """
        self.loggers = loggers
        self._level = LogLevel.INFO
        self._context = {}
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a debug message to all loggers."""
        if self.is_enabled_for(LogLevel.DEBUG):
            combined_extra = {**self._context, **(extra or {})}
            for logger in self.loggers:
                logger.debug(message, combined_extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log an info message to all loggers."""
        if self.is_enabled_for(LogLevel.INFO):
            combined_extra = {**self._context, **(extra or {})}
            for logger in self.loggers:
                logger.info(message, combined_extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a warning message to all loggers."""
        if self.is_enabled_for(LogLevel.WARNING):
            combined_extra = {**self._context, **(extra or {})}
            for logger in self.loggers:
                logger.warning(message, combined_extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log an error message to all loggers."""
        if self.is_enabled_for(LogLevel.ERROR):
            combined_extra = {**self._context, **(extra or {})}
            for logger in self.loggers:
                logger.error(message, combined_extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a critical message to all loggers."""
        if self.is_enabled_for(LogLevel.CRITICAL):
            combined_extra = {**self._context, **(extra or {})}
            for logger in self.loggers:
                logger.critical(message, combined_extra)
    
    def log(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a message at the specified level to all loggers."""
        if self.is_enabled_for(level):
            combined_extra = {**self._context, **(extra or {})}
            for logger in self.loggers:
                logger.log(level, message, combined_extra)
    
    def exception(self, message: str, exc_info: Optional[Exception] = None) -> None:
        """Log an exception to all loggers."""
        for logger in self.loggers:
            logger.exception(message, exc_info)
    
    def set_level(self, level: LogLevel) -> None:
        """Set the minimum logging level for all loggers."""
        self._level = level
        for logger in self.loggers:
            logger.set_level(level)
    
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
        for logger in self.loggers:
            logger.add_context(**kwargs)
    
    def remove_context(self, *keys) -> None:
        """Remove context information."""
        for key in keys:
            self._context.pop(key, None)
        for logger in self.loggers:
            logger.remove_context(*keys)
    
    def clear_context(self) -> None:
        """Clear all context information."""
        self._context.clear()
        for logger in self.loggers:
            logger.clear_context()
    
    def flush(self) -> None:
        """Flush all loggers."""
        for logger in self.loggers:
            logger.flush()
    
    def close(self) -> None:
        """Close all loggers."""
        for logger in self.loggers:
            logger.close()
    
    def add_logger(self, logger: Logger) -> None:
        """Add a new logger to the composite."""
        self.loggers.append(logger)
        logger.set_level(self._level)
        logger.add_context(**self._context)
    
    def remove_logger(self, logger: Logger) -> None:
        """Remove a logger from the composite."""
        if logger in self.loggers:
            self.loggers.remove(logger)