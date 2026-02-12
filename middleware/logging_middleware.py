"""
Logging middleware.
Logs all incoming updates for monitoring and debugging.
"""
import logging
from typing import Any, Awaitable, Callable, Dict, Union
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, Update

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware to log all incoming updates.
    Useful for debugging and monitoring bot activity.
    """
    
    async def __call__(
        self,
        handler: Callable[..., Awaitable[Any]],
        event: Union[Message, CallbackQuery, Update],
        data: Dict[str, Any]
    ) -> Any:
        """
        Log update and process it.
        
        Args:
            handler: Handler function
            event: Event (Message, CallbackQuery, or Update)
            data: Handler data
            
        Returns:
            Handler result
        """
        # Log incoming update (aiogram passes Message or CallbackQuery directly to middleware)
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else 0
            text = event.text or event.caption or ""
            logger.info(f"Message from user {user_id}: {text[:50]}")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else 0
            callback_data = event.data or ""
            logger.info(f"Callback from user {user_id}: {callback_data}")
        elif isinstance(event, Update):
            if event.message:
                user_id = event.message.from_user.id if event.message.from_user else 0
                text = event.message.text or event.message.caption or ""
                logger.info(f"Message from user {user_id}: {text[:50]}")
            elif event.callback_query:
                user_id = event.callback_query.from_user.id if event.callback_query.from_user else 0
                callback_data = event.callback_query.data or ""
                logger.info(f"Callback from user {user_id}: {callback_data}")
        
        # Process update
        return await handler(event, data)
