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
from dotenv import load_dotenv

from handlers import router

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

    # Загружаем переменные окружения
    load_dotenv()

    # Получаем токен бота
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.error(
            "Токен бота не найден!\n"
            "Создайте файл .env и добавьте: BOT_TOKEN=your_token_here"
        )
        sys.exit(1)

    # Проверяем наличие шаблона
    template_path = Path(__file__).parent / "dogovor_template.docx"
    if not template_path.exists():
        logger.warning(
            f"⚠️  Шаблон договора не найден: {template_path}\n"
            "Создайте файл dogovor_template.docx с переменными для подстановки.\n"
            "Пример переменных: {{{{ client_full_name }}}}, {{{{ contract_amount }}}}, и т.д."
        )

    # Инициализация бота и диспетчера
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутер
    dp.include_router(router)

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
