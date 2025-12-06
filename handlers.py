"""
Обработчики сообщений для Telegram-бота
"""
import logging
import os
from typing import Dict, Any, List

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile

from states import ContractStates
from contract_generator import generate_contract

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем роутер
router = Router()

# Словарь с описанием всех доступных полей
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

# Предустановленные наборы полей
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
    "full": list(AVAILABLE_FIELDS.keys())
}


def create_keyboard(buttons: List[str], row_width: int = 2) -> ReplyKeyboardMarkup:
    """Создает клавиатуру из списка кнопок"""
    keyboard_buttons = [[KeyboardButton(text=btn)] for btn in buttons]
    return ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)


def validate_not_empty(text: str, min_length: int = 1, max_length: int = 500) -> bool:
    """Базовая валидация: проверка на пустоту и длину"""
    return text and min_length <= len(text.strip()) <= max_length


def format_data_for_preview(data: Dict[str, Any], selected_fields: List[str]) -> str:
    """Форматирует данные для предпросмотра"""
    preview_text = "📋 *Предпросмотр введенных данных:*\n\n"

    for i, field_name in enumerate(selected_fields, 1):
        field_label = AVAILABLE_FIELDS.get(field_name, field_name)
        field_value = data.get(field_name, "Не указано")
        preview_text += f"{i}. *{field_label}:*\n   {field_value}\n\n"

    return preview_text


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()

    keyboard = create_keyboard([
        "📝 Минимальный набор",
        "📄 Стандартный набор",
        "📚 Полный набор",
        "✏️ Выбрать поля вручную"
    ], row_width=1)

    await message.answer(
        "👋 Добро пожаловать в Helper Contract Generator!\n\n"
        "Я помогу вам создать договор оказания услуг.\n\n"
        "Выберите набор полей для заполнения:",
        reply_markup=keyboard
    )
    await state.set_state(ContractStates.selecting_fields)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Обработчик команды /cancel"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять. Используйте /start для начала работы.")
        return

    await state.clear()
    await message.answer(
        "❌ Создание договора отменено.\n"
        "Используйте /start для начала заново.",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(ContractStates.selecting_fields)
async def process_field_selection(message: Message, state: FSMContext):
    """Обработка выбора набора полей"""
    text = message.text

    if text == "📝 Минимальный набор":
        selected_fields = FIELD_PRESETS["minimal"]
    elif text == "📄 Стандартный набор":
        selected_fields = FIELD_PRESETS["standard"]
    elif text == "📚 Полный набор":
        selected_fields = FIELD_PRESETS["full"]
    elif text == "✏️ Выбрать поля вручную":
        fields_list = "\n".join([f"{i}. {label}" for i, (_, label) in enumerate(AVAILABLE_FIELDS.items(), 1)])
        await message.answer(
            "📝 Введите номера полей через запятую или пробел.\n\n"
            f"Доступные поля:\n{fields_list}",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    else:
        # Обработка ручного выбора полей
        try:
            numbers = [int(n.strip()) for n in text.replace(',', ' ').split() if n.strip().isdigit()]
            all_field_keys = list(AVAILABLE_FIELDS.keys())
            selected_fields = [all_field_keys[n-1] for n in numbers if 0 < n <= len(all_field_keys)]

            if not selected_fields:
                await message.answer("❌ Не выбрано ни одного поля. Попробуйте снова.")
                return
        except (ValueError, IndexError):
            await message.answer("❌ Неверный формат. Попробуйте снова.")
            return

    # Сохраняем выбранные поля
    await state.update_data(selected_fields=selected_fields, field_index=0)

    # Начинаем сбор данных
    await ask_next_field(message, state)


async def ask_next_field(message: Message, state: FSMContext):
    """Запрашивает следующее поле из списка"""
    data = await state.get_data()
    selected_fields = data.get("selected_fields", [])
    field_index = data.get("field_index", 0)

    if field_index >= len(selected_fields):
        # Все поля заполнены, переходим к предпросмотру
        await show_preview(message, state)
        return

    current_field = selected_fields[field_index]
    field_label = AVAILABLE_FIELDS[current_field]

    # Устанавливаем соответствующее состояние
    state_name = f"ContractStates:{current_field}"
    await state.set_state(state_name)

    keyboard = create_keyboard(["⏭ Пропустить", "❌ Отмена"], row_width=2)

    await message.answer(
        f"📝 [{field_index + 1}/{len(selected_fields)}]\n\n"
        f"Введите *{field_label}*:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.message(StateFilter(ContractStates))
async def process_field_input(message: Message, state: FSMContext):
    """Обработка ввода данных для полей"""
    text = message.text

    # Проверка команд
    if text == "❌ Отмена":
        await cmd_cancel(message, state)
        return

    current_state = await state.get_state()

    # Если мы в состоянии предпросмотра
    if current_state == "ContractStates:preview":
        await handle_preview_choice(message, state)
        return

    # Если мы в состоянии редактирования
    if current_state == "ContractStates:editing_field":
        await handle_field_edit(message, state)
        return

    # Обработка ввода поля
    data = await state.get_data()
    selected_fields = data.get("selected_fields", [])
    field_index = data.get("field_index", 0)

    if field_index >= len(selected_fields):
        return

    current_field = selected_fields[field_index]

    # Если пропускаем поле
    if text == "⏭ Пропустить":
        field_value = ""
    else:
        # Базовая валидация
        if not validate_not_empty(text):
            await message.answer("❌ Поле не может быть пустым. Попробуйте снова.")
            return
        field_value = text.strip()

    # Сохраняем значение
    await state.update_data({current_field: field_value, "field_index": field_index + 1})

    # Запрашиваем следующее поле
    await ask_next_field(message, state)


async def show_preview(message: Message, state: FSMContext):
    """Показывает предпросмотр введенных данных"""
    data = await state.get_data()
    selected_fields = data.get("selected_fields", [])

    preview_text = format_data_for_preview(data, selected_fields)
    preview_text += "\n✅ Все верно?\n\n"
    preview_text += "Выберите действие:"

    keyboard = create_keyboard([
        "✅ Сгенерировать договор",
        "✏️ Изменить поле",
        "🔄 Начать заново"
    ], row_width=1)

    await message.answer(preview_text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(ContractStates.preview)


async def handle_preview_choice(message: Message, state: FSMContext):
    """Обработка выбора в режиме предпросмотра"""
    text = message.text

    if text == "✅ Сгенерировать договор":
        await generate_and_send_contract(message, state)
    elif text == "✏️ Изменить поле":
        data = await state.get_data()
        selected_fields = data.get("selected_fields", [])

        fields_text = "\n".join([f"{i}. {AVAILABLE_FIELDS[field]}"
                                  for i, field in enumerate(selected_fields, 1)])

        await message.answer(
            f"Введите номер поля для редактирования:\n\n{fields_text}",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(ContractStates.editing_field)
    elif text == "🔄 Начать заново":
        await cmd_start(message, state)


async def handle_field_edit(message: Message, state: FSMContext):
    """Обработка редактирования поля"""
    try:
        field_num = int(message.text.strip())
        data = await state.get_data()
        selected_fields = data.get("selected_fields", [])

        if not (0 < field_num <= len(selected_fields)):
            await message.answer("❌ Неверный номер поля. Попробуйте снова.")
            return

        field_to_edit = selected_fields[field_num - 1]
        field_label = AVAILABLE_FIELDS[field_to_edit]

        await state.update_data(editing_field_name=field_to_edit)
        await state.set_state(f"ContractStates:{field_to_edit}")

        keyboard = create_keyboard(["❌ Отмена редактирования"], row_width=1)

        await message.answer(
            f"✏️ Введите новое значение для поля *{field_label}*:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("❌ Введите корректный номер поля.")


async def generate_and_send_contract(message: Message, state: FSMContext):
    """Генерирует договор и отправляет пользователю"""
    await message.answer("⏳ Генерирую договор...", reply_markup=ReplyKeyboardRemove())

    try:
        data = await state.get_data()

        # Генерируем договор
        pdf_path = await generate_contract(data)

        # Отправляем PDF
        document = FSInputFile(pdf_path)
        await message.answer_document(
            document,
            caption="✅ Ваш договор готов!"
        )

        # Удаляем временные файлы
        try:
            os.remove(pdf_path)
            docx_path = pdf_path.replace('.pdf', '.docx')
            if os.path.exists(docx_path):
                os.remove(docx_path)
        except Exception as e:
            logger.error(f"Ошибка при удалении временных файлов: {e}")

        await message.answer(
            "Хотите создать еще один договор? Используйте /start",
            reply_markup=ReplyKeyboardRemove()
        )

        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при генерации договора: {e}")
        await message.answer(
            f"❌ Произошла ошибка при генерации договора: {str(e)}\n\n"
            "Попробуйте снова с помощью /start"
        )
        await state.clear()
