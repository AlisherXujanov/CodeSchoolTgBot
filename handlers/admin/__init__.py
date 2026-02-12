"""
Admin panel handlers.
Provides administrative functionality for managing the restaurant bot.
"""
from .dashboard import router as dashboard_router
from .orders import router as orders_router
from .menu import router as menu_router

__all__ = ["dashboard_router", "orders_router", "menu_router"]
