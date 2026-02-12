"""
Enhanced database helper with comprehensive restaurant bot functionality.
This module handles all database operations including users, orders, reservations, reviews, and promotions.
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from utils.constants import (
    ORDER_STATUS_PENDING, ORDER_STATUS_CONFIRMED, ORDER_STATUS_PREPARING,
    ORDER_STATUS_READY, ORDER_STATUS_DELIVERED, ORDER_STATUS_CANCELLED
)


class DatabaseHelper:
    """
    Main database helper class.
    Manages all data operations for the restaurant bot using JSON file storage.
    In production, this would be replaced with PostgreSQL or similar database.
    """
    
    def __init__(self, db_file: str = "database/data.json"):
        """
        Initialize database helper.
        
        Args:
            db_file: Path to JSON database file
        """
        self.db_file = db_file
        self.data = self.load_data()
        # Ensure data structure is up to date
        self._migrate_data()

    def load_data(self) -> Dict[str, Any]:
        """
        Load data from JSON file or create default structure.
        
        Returns:
            Dictionary containing all bot data
        """
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure all required keys exist
                    return self._ensure_data_structure(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading database: {e}. Creating new database.")
                return self._get_default_data()
        
        # Create default data structure
        default_data = self._get_default_data()
        self.save_data_dict(default_data)
        return default_data

    def _get_default_data(self) -> Dict[str, Any]:
        """Get default data structure with all required keys."""
        return {
            "menu": {
                "pizza": [
                    {"id": 1, "name": "Margherita", "price": 12.00,
                     "description": "Yangi pomidor, mozzarella, rayhon", "available": True},
                    {"id": 2, "name": "Pepperoni", "price": 14.00,
                     "description": "Pepperoni, mozzarella, pomidor sousi", "available": True},
                    {"id": 3, "name": "Gavayskiy", "price": 15.00,
                     "description": "Goʻsht, ananas, mozzarella", "available": True}
                ],
                "burgers": [
                    {"id": 4, "name": "Klassik Burger", "price": 10.00,
                     "description": "Mol goʻshti, karam, pomidor, piyoz", "available": True},
                    {"id": 5, "name": "Pishloqli Burger", "price": 11.00,
                     "description": "Mol goʻshti, pishloq, karam, pomidor", "available": True},
                    {"id": 6, "name": "Vegetarian Burger", "price": 9.00,
                     "description": "Oʻsimlik asosidagi kotleta, karam, pomidor", "available": True}
                ],
                "drinks": [
                    {"id": 7, "name": "Coca Cola", "price": 3.00,
                     "description": "Klassik gazlangan ichimlik", "available": True},
                    {"id": 8, "name": "Kofe", "price": 4.00,
                     "description": "Yangi qaynatilgan kofe", "available": True},
                    {"id": 9, "name": "Apelsin sharbati", "price": 5.00,
                     "description": "Yangi siqilgan apelsin sharbati", "available": True}
                ]
            },
            "users": {},  # User profiles
            "carts": {},  # Active shopping carts (separate from orders)
            "orders": {},  # Completed orders
            "reservations": {},  # Table reservations
            "reviews": {},  # Reviews and ratings
            "promo_codes": {},  # Promotional codes
            "order_counter": 1,  # Auto-incrementing order ID
            "reservation_counter": 1,  # Auto-incrementing reservation ID
            "review_counter": 1,  # Auto-incrementing review ID
            "settings": {
                "delivery_fee": 2.50,
                "min_order": 15.00,
                "business_hours": {
                    "monday": {"open": "11:00", "close": "22:00"},
                    "tuesday": {"open": "11:00", "close": "22:00"},
                    "wednesday": {"open": "11:00", "close": "22:00"},
                    "thursday": {"open": "11:00", "close": "22:00"},
                    "friday": {"open": "11:00", "close": "23:00"},
                    "saturday": {"open": "11:00", "close": "23:00"},
                    "sunday": {"open": "12:00", "close": "21:00"}
                }
            }
        }

    def _ensure_data_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required keys exist in data structure."""
        default = self._get_default_data()
        for key in default:
            if key not in data:
                data[key] = default[key]
        return data

    def _migrate_data(self):
        """Migrate old data structure to new structure if needed."""
        # Migrate old orders structure (carts) to new carts structure
        if "orders" in self.data and isinstance(self.data["orders"], dict):
            for user_id, order_data in list(self.data["orders"].items()):
                # Check if this is actually a cart (has items but no order_id)
                if isinstance(order_data, dict) and "items" in order_data and "order_id" not in order_data:
                    # This is a cart, move it to carts
                    if "carts" not in self.data:
                        self.data["carts"] = {}
                    self.data["carts"][user_id] = order_data
                    # Remove from orders
                    del self.data["orders"][user_id]
        
        # Ensure counters exist
        if "order_counter" not in self.data:
            self.data["order_counter"] = 1
        if "reservation_counter" not in self.data:
            self.data["reservation_counter"] = 1
        if "review_counter" not in self.data:
            self.data["review_counter"] = 1
        
        self.save_data()

    def save_data(self):
        """Save current data to file."""
        self.save_data_dict(self.data)

    def save_data_dict(self, data: Dict[str, Any]):
        """
        Save data dictionary to JSON file.
        
        Args:
            data: Data dictionary to save
        """
        Path(self.db_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ==================== MENU METHODS ====================

    def get_menu_category(self, category: str) -> List[Dict]:
        """
        Get all items in a menu category.
        
        Args:
            category: Category name (e.g., "pizza", "burgers")
            
        Returns:
            List of menu items in the category
        """
        return self.data.get("menu", {}).get(category, [])

    def get_item_by_id(self, item_id: int) -> Optional[Dict]:
        """
        Get menu item by ID.
        
        Args:
            item_id: Item ID
            
        Returns:
            Item dictionary or None if not found
        """
        for category in self.data.get("menu", {}).values():
            for item in category:
                if item.get("id") == item_id:
                    return item
        return None

    def get_all_menu_items(self) -> List[Dict]:
        """Get all menu items from all categories."""
        items = []
        for category_items in self.data.get("menu", {}).values():
            items.extend(category_items)
        return items

    # ==================== USER METHODS ====================

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get user profile data.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User data dictionary
        """
        user_str = str(user_id)
        if user_str not in self.data.get("users", {}):
            # Create default user profile
            self.data.setdefault("users", {})[user_str] = {
                "user_id": user_id,
                "loyalty_points": 0,
                "total_orders": 0,
                "addresses": [],
                "favorites": [],
                "preferences": {},
                "created_at": datetime.now().isoformat()
            }
            self.save_data()
        return self.data["users"][user_str]

    def update_user(self, user_id: int, **kwargs):
        """
        Update user profile data.
        
        Args:
            user_id: Telegram user ID
            **kwargs: Fields to update
        """
        user = self.get_user(user_id)
        user.update(kwargs)
        self.save_data()

    def add_user_address(self, user_id: int, address: Dict[str, Any]) -> int:
        """
        Add delivery address for user.
        
        Args:
            user_id: Telegram user ID
            address: Address dictionary
            
        Returns:
            Address ID
        """
        user = self.get_user(user_id)
        if "addresses" not in user:
            user["addresses"] = []
        
        # Generate address ID
        address_id = max([a.get("id", 0) for a in user["addresses"]] + [0]) + 1
        address["id"] = address_id
        
        # If this is the first address or marked as default, make it default
        if not user["addresses"] or address.get("is_default", False):
            for addr in user["addresses"]:
                addr["is_default"] = False
            address["is_default"] = True
        
        user["addresses"].append(address)
        self.save_data()
        return address_id

    def get_user_addresses(self, user_id: int) -> List[Dict]:
        """Get all delivery addresses for user."""
        user = self.get_user(user_id)
        return user.get("addresses", [])

    def add_favorite(self, user_id: int, item_id: int):
        """Add item to user's favorites."""
        user = self.get_user(user_id)
        if "favorites" not in user:
            user["favorites"] = []
        if item_id not in user["favorites"]:
            user["favorites"].append(item_id)
            self.save_data()

    def remove_favorite(self, user_id: int, item_id: int):
        """Remove item from user's favorites."""
        user = self.get_user(user_id)
        if "favorites" in user and item_id in user["favorites"]:
            user["favorites"].remove(item_id)
            self.save_data()

    def get_favorites(self, user_id: int) -> List[int]:
        """Get user's favorite item IDs."""
        user = self.get_user(user_id)
        return user.get("favorites", [])

    # ==================== CART METHODS ====================

    def get_cart(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's shopping cart.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Cart dictionary with items and total
        """
        user_str = str(user_id)
        if user_str not in self.data.get("carts", {}):
            self.data.setdefault("carts", {})[user_str] = {
                "items": {},
                "total": 0,
                "discount": 0,
                "promo_code": None,
                "created_at": datetime.now().isoformat()
            }
        return self.data["carts"][user_str]

    def add_to_cart(self, user_id: int, item_id: int, quantity: int = 1):
        """
        Add item to cart or increase quantity.
        
        Args:
            user_id: Telegram user ID
            item_id: Menu item ID
            quantity: Quantity to add
        """
        cart = self.get_cart(user_id)
        item_id_str = str(item_id)
        
        if item_id_str in cart["items"]:
            cart["items"][item_id_str] += quantity
        else:
            cart["items"][item_id_str] = quantity
        
        self.update_cart_total(user_id)
        self.save_data()

    def update_cart_item_quantity(self, user_id: int, item_id: int, quantity: int):
        """
        Update cart item quantity.
        
        Args:
            user_id: Telegram user ID
            item_id: Menu item ID
            quantity: New quantity (0 to remove)
        """
        cart = self.get_cart(user_id)
        item_id_str = str(item_id)
        
        if quantity <= 0:
            if item_id_str in cart["items"]:
                del cart["items"][item_id_str]
        else:
            cart["items"][item_id_str] = quantity
        
        self.update_cart_total(user_id)
        self.save_data()

    def remove_from_cart(self, user_id: int, item_id: int):
        """Remove item from cart."""
        self.update_cart_item_quantity(user_id, item_id, 0)

    def update_cart_total(self, user_id: int):
        """Recalculate cart total."""
        cart = self.get_cart(user_id)
        total = 0
        
        for item_id_str, quantity in cart["items"].items():
            item = self.get_item_by_id(int(item_id_str))
            if item and item.get("available", True):
                total += item["price"] * quantity
        
        cart["total"] = total
        
        # Apply discount if promo code is active
        if cart.get("promo_code"):
            promo = self.get_promo_code(cart["promo_code"])
            if promo and promo.get("is_active", True):
                discount = self._calculate_discount(total, promo)
                cart["discount"] = discount
            else:
                cart["discount"] = 0
                cart["promo_code"] = None
        else:
            cart["discount"] = 0
        
        self.save_data()

    def clear_cart(self, user_id: int):
        """Clear user's cart."""
        user_str = str(user_id)
        if user_str in self.data.get("carts", {}):
            self.data["carts"][user_str] = {
                "items": {},
                "total": 0,
                "discount": 0,
                "promo_code": None,
                "created_at": datetime.now().isoformat()
            }
            self.save_data()

    def apply_promo_code(self, user_id: int, promo_code: str) -> bool:
        """
        Apply promo code to cart.
        
        Args:
            user_id: Telegram user ID
            promo_code: Promo code string
            
        Returns:
            True if applied successfully, False otherwise
        """
        promo = self.get_promo_code(promo_code)
        if not promo or not promo.get("is_active", True):
            return False
        
        cart = self.get_cart(user_id)
        cart["promo_code"] = promo_code
        self.update_cart_total(user_id)
        return True

    # ==================== ORDER METHODS ====================

    def create_order(self, user_id: int, delivery_address: Optional[Dict] = None,
                    notes: Optional[str] = None) -> int:
        """
        Create order from user's cart.
        
        Args:
            user_id: Telegram user ID
            delivery_address: Delivery address dictionary
            notes: Order notes
            
        Returns:
            Order ID
        """
        cart = self.get_cart(user_id)
        if not cart.get("items"):
            raise ValueError("Cart is empty")
        
        order_id = self.data["order_counter"]
        self.data["order_counter"] += 1
        
        order = {
            "order_id": order_id,
            "user_id": user_id,
            "items": cart["items"].copy(),
            "total": cart["total"],
            "discount": cart.get("discount", 0),
            "delivery_fee": self.data["settings"].get("delivery_fee", 2.50),
            "promo_code": cart.get("promo_code"),
            "status": ORDER_STATUS_PENDING,
            "delivery_address": delivery_address,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.data.setdefault("orders", {})[str(order_id)] = order
        
        # Update user stats
        user = self.get_user(user_id)
        user["total_orders"] = user.get("total_orders", 0) + 1
        
        # Add loyalty points
        points_earned = int(cart["total"] * 1)  # 1 point per dollar
        user["loyalty_points"] = user.get("loyalty_points", 0) + points_earned
        
        # Clear cart
        self.clear_cart(user_id)
        
        self.save_data()
        return order_id

    def get_order(self, order_id: int) -> Optional[Dict]:
        """Get order by ID."""
        return self.data.get("orders", {}).get(str(order_id))

    def get_user_orders(self, user_id: int, limit: Optional[int] = None) -> List[Dict]:
        """
        Get user's order history.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of orders to return
            
        Returns:
            List of orders, newest first
        """
        orders = []
        for order in self.data.get("orders", {}).values():
            if order.get("user_id") == user_id:
                orders.append(order)
        
        # Sort by created_at descending
        orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        if limit:
            orders = orders[:limit]
        
        return orders

    def update_order_status(self, order_id: int, status: str):
        """
        Update order status.
        
        Args:
            order_id: Order ID
            status: New status
        """
        order = self.get_order(order_id)
        if order:
            order["status"] = status
            order["updated_at"] = datetime.now().isoformat()
            self.save_data()

    def cancel_order(self, order_id: int) -> bool:
        """
        Cancel an order (if still pending).
        
        Args:
            order_id: Order ID
            
        Returns:
            True if cancelled, False if cannot be cancelled
        """
        order = self.get_order(order_id)
        if order and order.get("status") == ORDER_STATUS_PENDING:
            order["status"] = ORDER_STATUS_CANCELLED
            order["updated_at"] = datetime.now().isoformat()
            self.save_data()
            return True
        return False

    # ==================== RESERVATION METHODS ====================

    def create_reservation(self, user_id: int, date: str, time: str,
                         party_size: int, special_requests: Optional[str] = None) -> int:
        """
        Create table reservation.
        
        Args:
            user_id: Telegram user ID
            date: Date string (YYYY-MM-DD)
            time: Time string (HH:MM)
            party_size: Number of guests
            special_requests: Special requests
            
        Returns:
            Reservation ID
        """
        reservation_id = self.data["reservation_counter"]
        self.data["reservation_counter"] += 1
        
        reservation = {
            "reservation_id": reservation_id,
            "user_id": user_id,
            "date": date,
            "time": time,
            "party_size": party_size,
            "status": "pending",
            "special_requests": special_requests,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.data.setdefault("reservations", {})[str(reservation_id)] = reservation
        self.save_data()
        return reservation_id

    def get_reservation(self, reservation_id: int) -> Optional[Dict]:
        """Get reservation by ID."""
        return self.data.get("reservations", {}).get(str(reservation_id))

    def get_user_reservations(self, user_id: int) -> List[Dict]:
        """Get user's reservations."""
        reservations = []
        for res in self.data.get("reservations", {}).values():
            if res.get("user_id") == user_id:
                reservations.append(res)
        
        reservations.sort(key=lambda x: (x.get("date", ""), x.get("time", "")), reverse=True)
        return reservations

    def update_reservation_status(self, reservation_id: int, status: str):
        """Update reservation status."""
        reservation = self.get_reservation(reservation_id)
        if reservation:
            reservation["status"] = status
            reservation["updated_at"] = datetime.now().isoformat()
            self.save_data()

    # ==================== REVIEW METHODS ====================

    def create_review(self, user_id: int, rating: int, comment: Optional[str] = None,
                     order_id: Optional[int] = None, item_id: Optional[int] = None) -> int:
        """
        Create review/rating.
        
        Args:
            user_id: Telegram user ID
            rating: Rating (1-5)
            comment: Review comment
            order_id: Associated order ID (optional)
            item_id: Associated item ID (optional)
            
        Returns:
            Review ID
        """
        review_id = self.data["review_counter"]
        self.data["review_counter"] += 1
        
        review = {
            "review_id": review_id,
            "user_id": user_id,
            "rating": rating,
            "comment": comment,
            "order_id": order_id,
            "item_id": item_id,
            "created_at": datetime.now().isoformat()
        }
        
        self.data.setdefault("reviews", {})[str(review_id)] = review
        self.save_data()
        return review_id

    def get_reviews(self, item_id: Optional[int] = None, order_id: Optional[int] = None) -> List[Dict]:
        """Get reviews, optionally filtered by item or order."""
        reviews = []
        for review in self.data.get("reviews", {}).values():
            if item_id and review.get("item_id") == item_id:
                reviews.append(review)
            elif order_id and review.get("order_id") == order_id:
                reviews.append(review)
            elif not item_id and not order_id:
                reviews.append(review)
        
        reviews.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return reviews

    # ==================== PROMO CODE METHODS ====================

    def create_promo_code(self, code: str, discount_type: str, discount_value: float,
                         min_order: float = 0.0, max_uses: Optional[int] = None,
                         valid_from: str = "", valid_until: str = "") -> bool:
        """
        Create promotional code.
        
        Args:
            code: Promo code string
            discount_type: "percentage" or "fixed"
            discount_value: Discount value
            min_order: Minimum order amount
            max_uses: Maximum number of uses (None for unlimited)
            valid_from: Start date (ISO format)
            valid_until: End date (ISO format)
            
        Returns:
            True if created successfully
        """
        if code in self.data.get("promo_codes", {}):
            return False  # Code already exists
        
        promo = {
            "code": code,
            "discount_type": discount_type,
            "discount_value": discount_value,
            "min_order": min_order,
            "max_uses": max_uses,
            "used_count": 0,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "is_active": True
        }
        
        self.data.setdefault("promo_codes", {})[code] = promo
        self.save_data()
        return True

    def get_promo_code(self, code: str) -> Optional[Dict]:
        """Get promo code by code string."""
        return self.data.get("promo_codes", {}).get(code)

    def _calculate_discount(self, total: float, promo: Dict) -> float:
        """Calculate discount amount from promo code."""
        if promo.get("discount_type") == "percentage":
            return total * (promo.get("discount_value", 0) / 100)
        else:  # fixed
            return min(promo.get("discount_value", 0), total)

    # ==================== SETTINGS METHODS ====================

    def get_settings(self) -> Dict:
        """Get bot settings."""
        return self.data.get("settings", {})

    def update_settings(self, **kwargs):
        """Update bot settings."""
        self.data.setdefault("settings", {}).update(kwargs)
        self.save_data()


# Global database instance
db = DatabaseHelper()
