"""
Конфигурация бота и константы
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Базовые пути
BASE_DIR = Path(__file__).parent
TEMPLATE_PATH = BASE_DIR / "dogovor_template.docx"
OUTPUT_DIR = BASE_DIR / "generated_contracts"

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не установлен в .env файле!\n"
        "Создайте файл .env и добавьте: BOT_TOKEN=your_token_here"
    )

# Безопасность: список разрешённых пользователей (user_id)
# Если список пуст - доступ открыт для всех
ALLOWED_USER_IDS_STR = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USER_IDS = [int(uid.strip()) for uid in ALLOWED_USER_IDS_STR.split(",") if uid.strip()]

# Rate limiting: максимум договоров на пользователя
MAX_CONTRACTS_PER_HOUR = int(os.getenv("MAX_CONTRACTS_PER_HOUR", "10"))
MAX_CONTRACTS_PER_DAY = int(os.getenv("MAX_CONTRACTS_PER_DAY", "50"))

# Валидация полей
FIELD_MIN_LENGTH = 1
FIELD_MAX_LENGTH = 500
FIELD_MAX_SIZE_BYTES = 10 * 1024  # 10 KB максимум для одного поля

# Конвертация PDF
PDF_CONVERSION_TIMEOUT = 30  # секунд
PDF_CONVERSION_RETRIES = 2  # количество попыток

# LibreOffice paths (в порядке приоритета)
LIBREOFFICE_PATHS = [
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
    "/usr/bin/soffice",  # Linux
    "/usr/bin/libreoffice",  # Linux alternative
    "soffice",  # Windows / PATH
]

# Логирование
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "bot.log"

# Тексты для UI
UI_TEXTS = {
    "access_denied": "⛔ Доступ запрещён. Этот бот доступен только авторизованным пользователям. Свяжитесь с @kiourntzidis для получения доступа.",
    "rate_limit_exceeded": "⚠️ Превышен лимит запросов. Попробуйте позже.",
    "server_error": "❌ Произошла ошибка на сервере. Попробуйте позже или обратитесь к администратору.",
    "template_not_found": "❌ Шаблон договора не найден. Обратитесь к администратору.",
    "pdf_conversion_error": "❌ Ошибка при создании PDF. Попробуйте позже.",
    "validation_error": "❌ Некорректные данные: {error}",
}

# Клавиатуры
BUTTON_MINIMAL = "📝 Минимальный набор"
BUTTON_STANDARD = "📄 Стандартный набор"
BUTTON_FULL = "📚 Полный набор"
BUTTON_CUSTOM = "✏️ Выбрать поля вручную"
BUTTON_SKIP = "⏭ Пропустить"
BUTTON_CANCEL = "❌ Отмена"
BUTTON_CANCEL_EDIT = "❌ Отмена редактирования"
BUTTON_GENERATE = "✅ Сгенерировать договор"
BUTTON_EDIT = "✏️ Изменить поле"
BUTTON_RESTART = "🔄 Начать заново"

# Предустановки полей
FIELD_PRESETS = {
    "minimal": [
        "client_full_name", "client_address", "executor_full_name",
        "executor_address", "contract_subject", "contract_amount"
    ],
    "standard": [
        "client_full_name", "client_passport_series", "client_passport_number",
        "client_address", "client_phone", "executor_full_name",
        "executor_passport_series", "executor_passport_number", "executor_address",
        "executor_phone", "contract_subject", "contract_amount", "contract_start_date"
    ],
    "full": [
        "client_full_name", "client_passport_series", "client_passport_number",
        "client_passport_issued_by", "client_passport_issue_date", "client_birth_date",
        "client_birth_place", "client_address", "client_phone", "client_email",
        "client_inn", "executor_full_name", "executor_passport_series",
        "executor_passport_number", "executor_passport_issued_by",
        "executor_passport_issue_date", "executor_birth_date", "executor_birth_place",
        "executor_address", "executor_phone", "executor_email", "executor_inn",
        "executor_bank_name", "executor_bank_account", "executor_bank_bik",
        "executor_bank_corr_account", "contract_subject", "contract_amount",
        "contract_deadline", "contract_start_date", "contract_payment_terms",
        "contract_additional_terms"
    ]
}

# Описания полей
AVAILABLE_FIELDS = {
    "client_full_name": "ФИО заказчика",
    "client_passport_series": "Серия паспорта заказчика",
    "client_passport_number": "Номер паспорта заказчика",
    "client_passport_issued_by": "Кем выдан паспорт заказчика",
    "client_passport_issue_date": "Дата выдачи паспорта заказчика",
    "client_birth_date": "Дата рождения заказчика",
    "client_birth_place": "Место рождения заказчика",
    "client_address": "Адрес заказчика",
    "client_phone": "Телефон заказчика",
    "client_email": "Email заказчика",
    "client_inn": "ИНН заказчика",
    "executor_full_name": "ФИО исполнителя",
    "executor_passport_series": "Серия паспорта исполнителя",
    "executor_passport_number": "Номер паспорта исполнителя",
    "executor_passport_issued_by": "Кем выдан паспорт исполнителя",
    "executor_passport_issue_date": "Дата выдачи паспорта исполнителя",
    "executor_birth_date": "Дата рождения исполнителя",
    "executor_birth_place": "Место рождения исполнителя",
    "executor_address": "Адрес исполнителя",
    "executor_phone": "Телефон исполнителя",
    "executor_email": "Email исполнителя",
    "executor_inn": "ИНН исполнителя",
    "executor_bank_name": "Название банка исполнителя",
    "executor_bank_account": "Расчетный счет исполнителя",
    "executor_bank_bik": "БИК банка исполнителя",
    "executor_bank_corr_account": "Корр. счет банка исполнителя",
    "contract_subject": "Предмет договора",
    "contract_amount": "Сумма договора",
    "contract_deadline": "Срок выполнения",
    "contract_start_date": "Дата начала действия договора",
    "contract_payment_terms": "Условия оплаты",
    "contract_additional_terms": "Дополнительные условия",
}

# Подсказки для полей
FIELD_HINTS = {
    "client_phone": "Например: +7-917-123-45-67 или +79171234567",
    "executor_phone": "Например: +7-917-123-45-67 или +79171234567",
    "client_email": "Например: user@example.com",
    "executor_email": "Например: user@example.com",
    "client_inn": "10 или 12 цифр (для физлиц 12, для ИП/ЮЛ 10)",
    "executor_inn": "10 или 12 цифр (для физлиц 12, для ИП/ЮЛ 10)",
    "executor_bank_bik": "9 цифр БИК банка",
    "executor_bank_account": "20 цифр расчётного счёта",
    "executor_bank_corr_account": "20 цифр корреспондентского счёта",
    "contract_amount": "Например: 50 000 рублей или 50000",
    "client_passport_series": "4 цифры (например: 1234)",
    "executor_passport_series": "4 цифры (например: 1234)",
    "client_passport_number": "6 цифр (например: 567890)",
    "executor_passport_number": "6 цифр (например: 567890)",
    "client_birth_date": "Формат: ДД.ММ.ГГГГ (например: 15.03.1990)",
    "executor_birth_date": "Формат: ДД.ММ.ГГГГ (например: 15.03.1990)",
    "client_passport_issue_date": "Формат: ДД.ММ.ГГГГ (например: 20.05.2010)",
    "executor_passport_issue_date": "Формат: ДД.ММ.ГГГГ (например: 20.05.2010)",
    "contract_start_date": "Формат: ДД.ММ.ГГГГ (например: 01.01.2024)",
    "contract_deadline": "Например: 30 дней или 01.02.2024",
}
