# Helper Contract Generator Bot

Telegram-бот для автоматической генерации договоров оказания услуг на основе шаблона DOCX с конвертацией в PDF.

## Возможности

- **Динамический выбор полей**: пользователь сам выбирает, какие данные хочет заполнить
- **Предустановленные наборы**: минимальный, стандартный или полный набор полей
- **Предпросмотр данных**: возможность просмотреть и отредактировать введённые данные перед генерацией
- **Базовая валидация**: проверка на пустые значения и длину
- **FSM (Finite State Machine)**: структурированное управление состояниями диалога
- **Модульная архитектура**: разделение на отдельные файлы для удобства поддержки
- **Генерация PDF**: автоматическая конвертация DOCX в PDF через LibreOffice

## Структура проекта

```
help_contract_bot/
├── main.py                    # Точка входа, инициализация бота
├── handlers.py                # Обработчики сообщений и команд
├── states.py                  # FSM состояния
├── contract_generator.py      # Логика генерации договоров
├── dogovor_template.docx      # Шаблон договора (создайте сами)
├── TEMPLATE_INSTRUCTIONS.md   # Инструкция по созданию шаблона
├── requirements.txt           # Зависимости Python
├── .env                       # Переменные окружения (не в git)
├── .env.example               # Пример файла с переменными
├── .gitignore                 # Игнорируемые файлы
└── README.md                  # Документация
```

## Установка

### 1. Клонирование и установка зависимостей

```bash
# Переход в директорию проекта
cd help_contract_bot

# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Установка LibreOffice

LibreOffice необходим для конвертации DOCX в PDF.

**macOS:**
```bash
brew install --cask libreoffice
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libreoffice
```

**Windows:**
Скачайте и установите с [официального сайта](https://www.libreoffice.org/)

### 3. Создание бота в Telegram

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям и получите токен
4. Скопируйте токен

### 4. Настройка переменных окружения

```bash
# Скопируйте пример файла
cp .env.example .env

# Отредактируйте .env и добавьте ваш токен
# BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 5. Создание шаблона договора

Создайте файл `dogovor_template.docx` в корне проекта. В шаблоне используйте переменные в формате `{{ variable_name }}` и условные блоки Jinja2.

**⚠️ ВАЖНО:** Используйте условные блоки `{% if %}...{% endif %}` для скрытия незаполненных полей!

**Краткий пример с условиями:**

```
ДОГОВОР ОКАЗАНИЯ УСЛУГ
№ {{ contract_number }} от {{ current_date }}

1. СТОРОНЫ ДОГОВОРА

Заказчик: {{ client_full_name }}
{% if client_passport_series and client_passport_number %}Паспорт: серия {{ client_passport_series }} № {{ client_passport_number }}{% endif %}
{% if client_passport_issued_by %}Выдан: {{ client_passport_issued_by }}{% if client_passport_issue_date %}, {{ client_passport_issue_date }}{% endif %}{% endif %}
{% if client_birth_date %}Дата рождения: {{ client_birth_date }}{% endif %}
{% if client_address %}Адрес: {{ client_address }}{% endif %}
{% if client_phone %}Телефон: {{ client_phone }}{% endif %}
{% if client_email %}Email: {{ client_email }}{% endif %}
{% if client_inn %}ИНН: {{ client_inn }}{% endif %}

Исполнитель: {{ executor_full_name }}
{% if executor_passport_series and executor_passport_number %}Паспорт: серия {{ executor_passport_series }} № {{ executor_passport_number }}{% endif %}
{% if executor_address %}Адрес: {{ executor_address }}{% endif %}
... (аналогично для других полей)

2. ПРЕДМЕТ ДОГОВОРА
{{ contract_subject }}

3. СТОИМОСТЬ И ПОРЯДОК ОПЛАТЫ
{% if contract_amount %}Стоимость услуг: {{ contract_amount }}{% endif %}
{% if contract_payment_terms %}Условия оплаты: {{ contract_payment_terms }}{% endif %}

... остальные разделы ...
```

**📖 Подробная инструкция:** См. файл [TEMPLATE_INSTRUCTIONS.md](TEMPLATE_INSTRUCTIONS.md) с полным примером шаблона и объяснением синтаксиса условных блоков.

**Доступные переменные:**

- **Заказчик**: `client_full_name`, `client_passport_series`, `client_passport_number`, `client_passport_issued_by`, `client_passport_issue_date`, `client_birth_date`, `client_birth_place`, `client_address`, `client_phone`, `client_email`, `client_inn`
- **Исполнитель**: `executor_full_name`, `executor_passport_series`, `executor_passport_number`, `executor_passport_issued_by`, `executor_passport_issue_date`, `executor_birth_date`, `executor_birth_place`, `executor_address`, `executor_phone`, `executor_email`, `executor_inn`
- **Договор**: `contract_subject`, `contract_amount`, `contract_deadline`, `contract_start_date`, `contract_payment_terms`, `contract_additional_terms`
- **Банк**: `executor_bank_name`, `executor_bank_account`, `executor_bank_bik`, `executor_bank_corr_account`
- **Системные**: `current_date`, `contract_number`

## Запуск

```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Запустите бота
python main.py
```

## Использование

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Выберите набор полей для заполнения:
   - **Минимальный**: ФИО сторон, адреса, сумма
   - **Стандартный**: базовые + паспортные данные, телефоны, дата
   - **Полный**: все доступные поля
   - **Выбрать вручную**: укажите номера нужных полей
4. Ответьте на вопросы бота
5. Проверьте введённые данные в предпросмотре
6. При необходимости отредактируйте поля
7. Подтвердите генерацию договора
8. Получите готовый PDF

### Команды

- `/start` - Начать создание договора
- `/cancel` - Отменить текущую операцию

## Особенности реализации

### FSM (Finite State Machine)

Бот использует машину состояний для управления диалогом:
- `selecting_fields` - выбор полей для заполнения
- Динамические состояния для каждого поля
- `preview` - предпросмотр данных
- `editing_field` - редактирование поля

### Архитектура

**main.py**
- Инициализация бота и диспетчера
- Настройка логирования
- Запуск polling

**handlers.py**
- Обработчики команд `/start`, `/cancel`
- Логика сбора данных
- Предпросмотр и редактирование
- Интеграция с генератором договоров

**states.py**
- Определение всех состояний FSM
- Группировка состояний по категориям

**contract_generator.py**
- Загрузка и рендеринг шаблона DOCX
- Подготовка контекста данных
- Конвертация DOCX → PDF через LibreOffice
- Управление временными файлами

### Валидация

Реализована базовая валидация:
- Проверка на пустые значения
- Проверка длины строк (1-500 символов)
- Возможность пропустить необязательные поля

## Логирование

Все события записываются в:
- Консоль (stdout)
- Файл `bot.log`

Уровни логирования:
- INFO: основные события
- WARNING: предупреждения
- ERROR: ошибки

## Безопасность

- Токен бота хранится в `.env` (не попадает в git)
- Временные файлы удаляются после отправки
- Базовая валидация предотвращает некорректный ввод

## Возможные проблемы и решения

### LibreOffice не найден

**Ошибка**: `LibreOffice не найден`

**Решение**: Установите LibreOffice (см. раздел "Установка LibreOffice")

### Шаблон не найден

**Ошибка**: `Шаблон договора не найден`

**Решение**: Создайте файл `dogovor_template.docx` в корне проекта

### Ошибка при конвертации PDF

**Причина**: LibreOffice не установлен или недоступен

**Решение**:
```bash
# Проверьте установку LibreOffice
which soffice  # Linux/macOS
where soffice  # Windows
```

## Расширение функционала

### Добавление новых полей

1. Добавьте переменную в `AVAILABLE_FIELDS` в `handlers.py`
2. Добавьте состояние в `ContractStates` в `states.py`
3. Добавьте переменную в `prepare_context()` в `contract_generator.py`
4. Используйте переменную в шаблоне `dogovor_template.docx`

### Добавление строгой валидации

В `handlers.py` измените функцию `validate_not_empty()`:

```python
import re

def validate_inn(inn: str) -> bool:
    """Валидация ИНН"""
    return re.match(r'^\d{10}$|^\d{12}$', inn) is not None

def validate_phone(phone: str) -> bool:
    """Валидация телефона"""
    return re.match(r'^[\d\+\-\(\)\s]+$', phone) is not None
```

## Лицензия

MIT License

## Автор

Created with Claude Code

---

**Telegram**: [@help_contract_bot](https://t.me/help_contract_bot)
