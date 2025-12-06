"""
Helper Contract Generator Bot (@help_contract_bot)

Telegram-бот для генерации договоров оказания услуг
на основе шаблона DOCX с конвертацией в PDF.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import router
from middleware import AuthMiddleware, RateLimitMiddleware
from config import BOT_TOKEN, TEMPLATE_PATH, ALLOWED_USER_IDS

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""

    # BOT_TOKEN теперь загружается в config.py
    # Проверка уже выполнена при импорте config

    # Проверяем наличие шаблона
    if not TEMPLATE_PATH.exists():
        logger.warning(
            f"⚠️  Шаблон договора не найден: {TEMPLATE_PATH}\n"
            "Создайте файл dogovor_template.docx с переменными для подстановки.\n"
            "См. TEMPLATE_INSTRUCTIONS.md для инструкций."
        )

    # Инициализация бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # КРИТИЧНО: Регистрируем middleware
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())

    # Регистрируем роутер
    dp.include_router(router)

    # Логируем конфигурацию безопасности
    if ALLOWED_USER_IDS:
        logger.info(f"🔒 Аутентификация включена. Разрешённые пользователи: {ALLOWED_USER_IDS}")
    else:
        logger.warning("⚠️  Аутентификация отключена. Бот доступен всем пользователям!")

    logger.info("🚀 Бот запущен и готов к работе!")
    logger.info("Нажмите Ctrl+C для остановки")

    try:
        # Удаляем вебхуки и запускаем polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1)
