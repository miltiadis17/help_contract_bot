"""
Валидаторы для проверки полей договора
"""
import re
from datetime import datetime
from typing import Tuple

from exceptions import ValidationError


def validate_not_empty(text: str, min_length: int = 1, max_length: int = 500) -> bool:
    """
    Базовая валидация: проверка на пустоту и длину

    Args:
        text: Текст для проверки
        min_length: Минимальная длина
        max_length: Максимальная длина

    Returns:
        True если валидно
    """
    if not text:
        return False
    text_stripped = text.strip()
    return min_length <= len(text_stripped) <= max_length


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Проверка формата телефона

    Поддерживаемые форматы:
    - +7-917-123-45-67
    - +79171234567
    - 89171234567
    - 79171234567

    Args:
        phone: Номер телефона

    Returns:
        (True, "") если валидно, (False, "сообщение об ошибке") если невалидно
    """
    if not phone:
        return False, "Телефон не может быть пустым"

    # Удаляем все символы кроме цифр и +
    cleaned = re.sub(r'[^\d+]', '', phone)

    # Проверяем формат
    patterns = [
        r'^\+7\d{10}$',  # +7XXXXXXXXXX
        r'^8\d{10}$',     # 8XXXXXXXXXX
        r'^7\d{10}$',     # 7XXXXXXXXXX
        r'^\+\d{11,15}$', # международный формат
    ]

    for pattern in patterns:
        if re.match(pattern, cleaned):
            return True, ""

    return False, "Неверный формат телефона. Используйте формат: +7-XXX-XXX-XX-XX или +79XXXXXXXXX"


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Проверка формата email

    Args:
        email: Email адрес

    Returns:
        (True, "") если валидно, (False, "сообщение об ошибке") если невалидно
    """
    if not email:
        return False, "Email не может быть пустым"

    # RFC 5322 упрощённый паттерн
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(pattern, email):
        return True, ""

    return False, "Неверный формат email. Используйте формат: user@example.com"


def validate_inn(inn: str) -> Tuple[bool, str]:
    """
    Проверка формата ИНН

    ИНН может быть:
    - 10 цифр (для организаций)
    - 12 цифр (для физических лиц)

    Args:
        inn: ИНН

    Returns:
        (True, "") если валидно, (False, "сообщение об ошибке") если невалидно
    """
    if not inn:
        return False, "ИНН не может быть пустым"

    # Удаляем все символы кроме цифр
    cleaned = re.sub(r'\D', '', inn)

    if len(cleaned) == 10 or len(cleaned) == 12:
        return True, ""

    return False, "ИНН должен содержать 10 цифр (для организаций) или 12 цифр (для физлиц)"


def validate_passport_series(series: str) -> Tuple[bool, str]:
    """
    Проверка серии паспорта (4 цифры)

    Args:
        series: Серия паспорта

    Returns:
        (True, "") если валидно, (False, "сообщение об ошибке") если невалидно
    """
    if not series:
        return False, "Серия паспорта не может быть пустой"

    cleaned = re.sub(r'\D', '', series)

    if len(cleaned) == 4:
        return True, ""

    return False, "Серия паспорта должна содержать 4 цифры"


def validate_passport_number(number: str) -> Tuple[bool, str]:
    """
    Проверка номера паспорта (6 цифр)

    Args:
        number: Номер паспорта

    Returns:
        (True, "") если валидно, (False, "сообщение об ошибке") если невалидно
    """
    if not number:
        return False, "Номер паспорта не может быть пустым"

    cleaned = re.sub(r'\D', '', number)

    if len(cleaned) == 6:
        return True, ""

    return False, "Номер паспорта должен содержать 6 цифр"


def validate_date(date_str: str, date_format: str = '%d.%m.%Y') -> Tuple[bool, str]:
    """
    Проверка формата даты

    Args:
        date_str: Дата в строковом формате
        date_format: Формат даты (по умолчанию ДД.ММ.ГГГГ)

    Returns:
        (True, "") если валидно, (False, "сообщение об ошибке") если невалидно
    """
    if not date_str:
        return False, "Дата не может быть пустой"

    try:
        parsed_date = datetime.strptime(date_str, date_format)

        # Проверка на разумность даты (не в далёком прошлом или будущем)
        current_year = datetime.now().year
        if not (1900 <= parsed_date.year <= current_year + 10):
            return False, f"Дата должна быть между 1900 и {current_year + 10} годом"

        return True, ""
    except ValueError:
        return False, f"Неверный формат даты. Используйте формат: {date_format} (например: 15.03.1990)"


def validate_birth_date(date_str: str) -> Tuple[bool, str]:
    """
    Проверка даты рождения (не в будущем, не слишком давно)

    Args:
        date_str: Дата рождения

    Returns:
        (True, "") если валидно, (False, "сообщение об ошибке") если невалидно
    """
    is_valid, error = validate_date(date_str)
    if not is_valid:
        return is_valid, error

    try:
        birth_date = datetime.strptime(date_str, '%d.%m.%Y')
        today = datetime.now()

        # Проверка что дата не в будущем
        if birth_date > today:
            return False, "Дата рождения не может быть в будущем"

        # Проверка разумного возраста (от 18 до 120 лет)
        age = (today - birth_date).days // 365
        if age < 18:
            return False, "Возраст должен быть не менее 18 лет"
        if age > 120:
            return False, "Проверьте правильность даты рождения"

        return True, ""
    except ValueError:
        return False, "Неверный формат даты рождения"


def validate_bik(bik: str) -> Tuple[bool, str]:
    """
    Проверка БИК банка (9 цифр)

    Args:
        bik: БИК банка

    Returns:
        (True, "") если валидно, (False, "сообщение об ошибке") если невалидно
    """
    if not bik:
        return False, "БИК не может быть пустым"

    cleaned = re.sub(r'\D', '', bik)

    if len(cleaned) == 9:
        return True, ""

    return False, "БИК должен содержать 9 цифр"


def validate_bank_account(account: str) -> Tuple[bool, str]:
    """
    Проверка банковского счёта (20 цифр)

    Args:
        account: Номер счёта

    Returns:
        (True, "") если валидно, (False, "сообщение об ошибке") если невалидно
    """
    if not account:
        return False, "Номер счёта не может быть пустым"

    cleaned = re.sub(r'\D', '', account)

    if len(cleaned) == 20:
        return True, ""

    return False, "Номер счёта должен содержать 20 цифр"


def validate_amount(amount: str) -> Tuple[bool, str]:
    """
    Проверка суммы договора

    Поддерживаемые форматы:
    - 50000
    - 50 000
    - 50000.00
    - 50 000 рублей
    - 50000 руб

    Args:
        amount: Сумма

    Returns:
        (True, "") если валидно, (False, "сообщение об ошибке") если невалидно
    """
    if not amount:
        return False, "Сумма не может быть пустой"

    # Паттерн для проверки суммы
    pattern = r'^\d+(?:[.,\s]\d+)*(?:[.,]\d{1,2})?\s*(?:рубл(?:ей|я|ь)?|руб\.?|р\.?)?$'

    if re.match(pattern, amount.strip(), re.IGNORECASE):
        return True, ""

    return False, "Неверный формат суммы. Используйте формат: 50000 или 50 000 рублей"


def sanitize_text(text: str) -> str:
    """
    Очистка текста от потенциально опасных символов

    Args:
        text: Исходный текст

    Returns:
        Очищенный текст
    """
    if not text:
        return ""

    # Удаляем управляющие символы (кроме переноса строки и табуляции)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

    # Удаляем потенциально опасные конструкции для Jinja2
    dangerous_patterns = [
        r'\{\{.*?\}\}',  # {{ ... }}
        r'\{%.*?%\}',    # {% ... %}
        r'\{#.*?#\}',    # {# ... #}
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)

    # Ограничиваем длину
    max_length = 1000
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


# Словарь валидаторов для каждого поля
FIELD_VALIDATORS = {
    'client_phone': validate_phone,
    'executor_phone': validate_phone,
    'client_email': validate_email,
    'executor_email': validate_email,
    'client_inn': validate_inn,
    'executor_inn': validate_inn,
    'client_passport_series': validate_passport_series,
    'executor_passport_series': validate_passport_series,
    'client_passport_number': validate_passport_number,
    'executor_passport_number': validate_passport_number,
    'client_birth_date': validate_birth_date,
    'executor_birth_date': validate_birth_date,
    'client_passport_issue_date': validate_date,
    'executor_passport_issue_date': validate_date,
    'contract_start_date': validate_date,
    'executor_bank_bik': validate_bik,
    'executor_bank_account': validate_bank_account,
    'executor_bank_corr_account': validate_bank_account,
    'contract_amount': validate_amount,
}


def validate_field(field_name: str, value: str) -> None:
    """
    Валидирует поле по его имени

    Args:
        field_name: Название поля
        value: Значение поля

    Raises:
        ValidationError: Если валидация не прошла
    """
    # Базовая валидация на пустоту и длину
    if not validate_not_empty(value):
        raise ValidationError(field_name, "Поле не может быть пустым")

    # Специфичная валидация для конкретных полей
    if field_name in FIELD_VALIDATORS:
        validator = FIELD_VALIDATORS[field_name]
        is_valid, error_message = validator(value)

        if not is_valid:
            raise ValidationError(field_name, error_message)
