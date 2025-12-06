"""
Дополнительные функции для handlers.py
Эти функции заменяют/дополняют существующие

ИНСТРУКЦИЯ ПО ПРИМЕНЕНИЮ:
1. Замените функцию process_field_input в handlers.py на эту версию
2. Замените функцию generate_and_send_contract в handlers.py на эту версию
3. Замените функцию ask_next_field в handlers.py на эту версию
"""

import logging
from typing import Dict, Any, List

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove

from config import AVAILABLE_FIELDS, FIELD_HINTS, BUTTON_SKIP, BUTTON_CANCEL, UI_TEXTS
from contract_generator import generate_contract
from exceptions import TemplateNotFoundError, PDFConversionError, LibreOfficeNotFoundError, ValidationError
from validators import validate_field, validate_not_empty

logger = logging.getLogger(__name__)


async def ask_next_field(message: Message, state: FSMContext):
    """Запрашивает следующее поле из списка С ПОДСКАЗКАМИ"""
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

    # Формируем сообщение с подсказкой
    hint_text = ""
    if current_field in FIELD_HINTS:
        hint_text = f"\n💡 {FIELD_HINTS[current_field]}"

    keyboard = create_keyboard([BUTTON_SKIP, BUTTON_CANCEL], row_width=2)

    await message.answer(
        f"📝 [{field_index + 1}/{len(selected_fields)}]\n\n"
        f"Введите *{field_label}*:{hint_text}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


async def process_field_input(message: Message, state: FSMContext):
    """Обработка ввода данных для полей С ВАЛИДАЦИЕЙ"""
    text = message.text

    # Проверка команд
    if text == BUTTON_CANCEL:
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
    if text == BUTTON_SKIP:
        field_value = ""
        logger.debug(f"Пользователь {message.from_user.id} пропустил поле {current_field}")
    else:
        # КРИТИЧНО: Валидация поля
        try:
            validate_field(current_field, text)
            field_value = text.strip()
            logger.debug(f"Поле {current_field} прошло валидацию")
        except ValidationError as e:
            # Сообщаем пользователю об ошибке валидации
            logger.warning(f"Ошибка валидации поля {current_field}: {e.message}")
            await message.answer(
                f"❌ {e.message}\n\nПопробуйте снова."
            )
            return  # Не переходим к следующему полю

    # Сохраняем значение
    await state.update_data({current_field: field_value, "field_index": field_index + 1})

    # Запрашиваем следующее поле
    await ask_next_field(message, state)


async def generate_and_send_contract(message: Message, state: FSMContext):
    """Генерирует договор и отправляет пользователю С ОБРАБОТКОЙ ОШИБОК"""
    user_id = message.from_user.id

    await message.answer("⏳ Генерирую договор...", reply_markup=ReplyKeyboardRemove())

    try:
        data = await state.get_data()

        # Добавляем user_id для логирования
        data["user_id"] = user_id

        # Генерируем договор
        logger.info(f"Начало генерации договора для пользователя {user_id}")
        pdf_path = await generate_contract(data)

        # Отправляем PDF
        document = FSInputFile(pdf_path)
        await message.answer_document(
            document,
            caption="✅ Ваш договор готов!"
        )

        logger.info(f"Договор успешно отправлен пользователю {user_id}")

        # Удаляем временные файлы
        try:
            import os
            from pathlib import Path

            os.remove(pdf_path)
            docx_path = Path(pdf_path).with_suffix('.docx')
            if docx_path.exists():
                os.remove(docx_path)
            logger.debug(f"Временные файлы удалены для {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при удалении временных файлов: {e}")

        await message.answer(
            "Хотите создать еще один договор? Используйте /start",
            reply_markup=ReplyKeyboardRemove()
        )

        await state.clear()

    except TemplateNotFoundError as e:
        logger.error(f"Шаблон не найден: {e}")
        await message.answer(UI_TEXTS["template_not_found"])
        await state.clear()

    except LibreOfficeNotFoundError as e:
        logger.error(f"LibreOffice не найден: {e}")
        await message.answer(
            "❌ LibreOffice не установлен на сервере. "
            "Обратитесь к администратору."
        )
        await state.clear()

    except PDFConversionError as e:
        logger.error(f"Ошибка конвертации PDF для пользователя {user_id}: {e}")
        await message.answer(UI_TEXTS["pdf_conversion_error"])
        await state.clear()

    except Exception as e:
        logger.critical(f"Неожиданная ошибка при генерации договора для {user_id}: {e}", exc_info=True)
        await message.answer(UI_TEXTS["server_error"])
        await state.clear()


# Импортируйте эти функции в handlers.py:
# from handlers_patch import ask_next_field, process_field_input, generate_and_send_contract
