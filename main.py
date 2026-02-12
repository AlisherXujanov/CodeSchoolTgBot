"""
Main entry point for the restaurant bot.
Initializes bot, registers all handlers and middleware, and starts polling.
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Import handlers
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.cart import router as cart_router
from handlers.orders import router as orders_router
from handlers.profile import router as profile_router
from handlers.reservations import router as reservations_router
from handlers.reviews import router as reviews_router
from handlers.promotions import router as promotions_router
from handlers.payment import router as payment_router
from handlers.admin.dashboard import router as admin_dashboard_router
from handlers.admin.orders import router as admin_orders_router
from handlers.admin.menu import router as admin_menu_router

# Import middleware
from middleware.error_handler import ErrorHandlerMiddleware
from middleware.logging_middleware import LoggingMiddleware

from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Main function to start the bot.
    Sets up all routers, middleware, and starts polling for updates.
    """
    # Initialize Bot instance with default bot properties
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Initialize Dispatcher
    dp = Dispatcher()

    # Register middleware (order matters - first registered is called first)
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Register routers (order matters - first matching handler wins)
    # Admin routers should be registered first to handle admin commands
    dp.include_router(admin_dashboard_router)
    dp.include_router(admin_orders_router)
    dp.include_router(admin_menu_router)
    
    # User-facing routers
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(cart_router)
    dp.include_router(orders_router)
    dp.include_router(profile_router)
    dp.include_router(reservations_router)
    dp.include_router(reviews_router)
    dp.include_router(promotions_router)
    dp.include_router(payment_router)

    # Start polling
    logger.info("Starting restaurant bot...")
    logger.info("Bot features: Menu, Cart, Orders, Profile, Reservations, Reviews, Promotions, Admin Panel")
    try:
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
