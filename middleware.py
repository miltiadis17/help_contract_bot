"""
Middleware для бота: аутентификация и rate limiting
"""
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from config import ALLOWED_USER_IDS, MAX_CONTRACTS_PER_HOUR, MAX_CONTRACTS_PER_DAY, UI_TEXTS
from exceptions import AccessDeniedError, RateLimitExceededError

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки доступа пользователей"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Проверяет доступ пользователя

        Args:
            handler: Следующий обработчик
            event: Событие (Message, CallbackQuery и т.д.)
            data: Данные для обработчика

        Returns:
            Результат обработчика или None если доступ запрещён
        """
        # Получаем user_id из события
        user = None
        if isinstance(event, Message):
            user = event.from_user

        if not user:
            # Если не можем определить пользователя, пропускаем
            return await handler(event, data)

        user_id = user.id

        # Если список разрешённых пользователей пуст - доступ открыт для всех
        if not ALLOWED_USER_IDS:
            logger.debug(f"Доступ открыт для всех (пользователь {user_id})")
            return await handler(event, data)

        # Проверяем, есть ли пользователь в белом списке
        if user_id not in ALLOWED_USER_IDS:
            logger.warning(
                f"Попытка доступа от неавторизованного пользователя: "
                f"{user_id} (@{user.username})"
            )
            if isinstance(event, Message):
                await event.answer(UI_TEXTS["access_denied"])
            return None

        logger.info(f"Авторизованный доступ: {user_id} (@{user.username})")
        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов"""

    def __init__(self):
        super().__init__()
        # Хранилище счётчиков: {user_id: [(timestamp, action), ...]}
        self._user_actions: Dict[int, list] = defaultdict(list)

    def _cleanup_old_actions(self, user_id: int, hours: int = 24) -> None:
        """Удаляет устаревшие записи"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        self._user_actions[user_id] = [
            (ts, action) for ts, action in self._user_actions[user_id]
            if ts > cutoff_time
        ]

    def _count_actions(self, user_id: int, action: str, hours: int) -> int:
        """Подсчитывает количество действий за период"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return sum(
            1 for ts, act in self._user_actions[user_id]
            if ts > cutoff_time and act == action
        )

    def _record_action(self, user_id: int, action: str) -> None:
        """Записывает действие пользователя"""
        self._user_actions[user_id].append((datetime.now(), action))

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Проверяет лимиты запросов

        Args:
            handler: Следующий обработчик
            event: Событие
            data: Данные для обработчика

        Returns:
            Результат обработчика или None если лимит превышен
        """
        # Проверяем только для команды генерации договора
        if not isinstance(event, Message):
            return await handler(event, data)

        user = event.from_user
        if not user:
            return await handler(event, data)

        user_id = user.id

        # Очищаем старые записи
        self._cleanup_old_actions(user_id)

        # Проверяем только при генерации договора
        # (когда пользователь подтверждает в предпросмотре)
        text = event.text or ""
        is_generation_request = "✅ Сгенерировать договор" in text

        if not is_generation_request:
            return await handler(event, data)

        # Проверяем лимит за час
        contracts_per_hour = self._count_actions(user_id, "contract_generated", hours=1)
        if contracts_per_hour >= MAX_CONTRACTS_PER_HOUR:
            logger.warning(
                f"Пользователь {user_id} превысил лимит: "
                f"{contracts_per_hour}/{MAX_CONTRACTS_PER_HOUR} за час"
            )
            await event.answer(
                f"{UI_TEXTS['rate_limit_exceeded']}\n"
                f"Лимит: {MAX_CONTRACTS_PER_HOUR} договоров в час."
            )
            return None

        # Проверяем лимит за день
        contracts_per_day = self._count_actions(user_id, "contract_generated", hours=24)
        if contracts_per_day >= MAX_CONTRACTS_PER_DAY:
            logger.warning(
                f"Пользователь {user_id} превысил дневной лимит: "
                f"{contracts_per_day}/{MAX_CONTRACTS_PER_DAY}"
            )
            await event.answer(
                f"{UI_TEXTS['rate_limit_exceeded']}\n"
                f"Лимит: {MAX_CONTRACTS_PER_DAY} договоров в день."
            )
            return None

        # Записываем действие
        self._record_action(user_id, "contract_generated")
        logger.info(
            f"Пользователь {user_id}: генерация договора "
            f"({contracts_per_hour + 1}/{MAX_CONTRACTS_PER_HOUR} за час, "
            f"{contracts_per_day + 1}/{MAX_CONTRACTS_PER_DAY} за день)"
        )

        return await handler(event, data)
