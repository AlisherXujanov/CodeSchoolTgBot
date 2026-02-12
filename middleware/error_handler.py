"""
Error handling middleware.
Catches and handles errors gracefully, providing user-friendly error messages.
"""
import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from utils.errors import RestaurantBotError, ValidationError, PermissionError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Middleware to catch and handle errors.
    Provides user-friendly error messages and logs errors for debugging.
    """
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process update and handle any errors.
        
        Args:
            handler: Handler function
            event: Update event
            data: Handler data
            
        Returns:
            Handler result or None if error occurred
        """
        try:
            return await handler(event, data)
        except ValidationError as e:
            # Handle validation errors with user-friendly message
            await self._send_error_message(event, e.message)
            logger.warning(f"Validation error: {e.message} (field: {e.field})")
        except PermissionError as e:
            # Handle permission errors
            await self._send_error_message(event, "❌ Bu amalni bajarish uchun ruxsatingiz yo'q!")
            logger.warning(f"Permission error: {e}")
        except RestaurantBotError as e:
            # Handle custom bot errors
            await self._send_error_message(event, f"❌ Xatolik: {str(e)}")
            logger.error(f"Bot error: {e}", exc_info=True)
        except Exception as e:
            # Handle unexpected errors
            await self._send_error_message(
                event,
                "❌ Kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
            )
            logger.error(f"Unexpected error: {e}", exc_info=True)
    
    async def _send_error_message(self, event: Update, message: str):
        """
        Send error message to user.
        
        Args:
            event: Update event
            message: Error message
        """
        try:
            if isinstance(event, Message):
                await event.answer(message)
            elif isinstance(event, CallbackQuery):
                await event.answer(message, show_alert=True)
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
