class DomainException(Exception):
    """Excepción base para errores de dominio."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class EntityNotFoundException(DomainException):
    """Lanzada cuando un recurso no existe en BD."""
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, 404)

class ValidationError(DomainException):
    """Lanzada ante errores de validación de negocio."""
    def __init__(self, message: str = "Error de validación"):
        super().__init__(message, 422)
