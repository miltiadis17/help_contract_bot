"""
Кастомные исключения для бота
"""


class ContractBotException(Exception):
    """Базовое исключение для всех ошибок бота"""
    pass


class TemplateNotFoundError(ContractBotException):
    """Шаблон договора не найден"""
    pass


class PDFConversionError(ContractBotException):
    """Ошибка при конвертации DOCX в PDF"""
    pass


class LibreOfficeNotFoundError(PDFConversionError):
    """LibreOffice не установлен или не найден"""
    pass


class PDFConversionTimeoutError(PDFConversionError):
    """Таймаут при конвертации в PDF"""
    pass


class ValidationError(ContractBotException):
    """Ошибка валидации данных"""

    def __init__(self, field_name: str, message: str):
        self.field_name = field_name
        self.message = message
        super().__init__(f"Ошибка валидации поля '{field_name}': {message}")


class RateLimitExceededError(ContractBotException):
    """Превышен лимит запросов"""

    def __init__(self, limit_type: str = "general"):
        self.limit_type = limit_type
        super().__init__(f"Превышен лимит: {limit_type}")


class AccessDeniedError(ContractBotException):
    """Доступ запрещён"""
    pass
