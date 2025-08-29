"""
Validation Errors

Specific validation exceptions for domain objects.
"""

from .domain_exceptions import DomainException


class ValidationError(DomainException):
    """Base class for validation errors."""
    pass


class InvalidFilenameError(ValidationError):
    """Raised when a filename is invalid."""
    
    def __init__(self, filename: str, reason: str = None):
        if reason is None:
            reason = "Nome de arquivo inválido"
        message = f"Filename inválido: '{filename}'"
        super().__init__(message, reason)
        self.filename = filename


class InvalidPathError(ValidationError):
    """Raised when a path is invalid."""
    
    def __init__(self, path: str, reason: str = None):
        if reason is None:
            reason = "Caminho inválido"
        message = f"Path inválido: '{path}'"
        super().__init__(message, reason)
        self.path = path


class InvalidExtensionError(ValidationError):
    """Raised when a file extension is invalid."""
    
    def __init__(self, extension: str, reason: str = None):
        if reason is None:
            reason = "Extensão inválida"
        message = f"Extensão inválida: '{extension}'"
        super().__init__(message, reason)
        self.extension = extension


class EmptyValueError(ValidationError):
    """Raised when a required value is empty."""
    
    def __init__(self, field_name: str):
        message = f"Campo obrigatório vazio: '{field_name}'"
        super().__init__(message)
        self.field_name = field_name


class ValueTooLongError(ValidationError):
    """Raised when a value exceeds maximum length."""
    
    def __init__(self, field_name: str, value: str, max_length: int):
        message = f"Valor muito longo para '{field_name}': {len(value)} > {max_length}"
        super().__init__(message)
        self.field_name = field_name
        self.value = value
        self.max_length = max_length