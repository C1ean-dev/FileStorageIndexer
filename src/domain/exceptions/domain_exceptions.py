"""
Domain Exceptions

Custom exceptions for domain-specific errors and business rule violations.
"""


class DomainException(Exception):
    """Base exception for all domain-related errors."""
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class FileValidationError(DomainException):
    """Raised when file validation fails."""
    
    def __init__(self, filename: str, reason: str):
        message = f"Validação de arquivo falhou para '{filename}'"
        super().__init__(message, reason)
        self.filename = filename


class PathValidationError(DomainException):
    """Raised when path validation fails."""
    
    def __init__(self, path: str, reason: str):
        message = f"Validação de caminho falhou para '{path}'"
        super().__init__(message, reason)
        self.path = path


class InvalidFileSizeError(DomainException):
    """Raised when file size is invalid."""
    
    def __init__(self, size: int, reason: str = None):
        message = f"Tamanho de arquivo inválido: {size}"
        super().__init__(message, reason)
        self.size = size


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
    
    def __init__(self, rule: str, context: str = None):
        message = f"Violação de regra de negócio: {rule}"
        super().__init__(message, context)
        self.rule = rule