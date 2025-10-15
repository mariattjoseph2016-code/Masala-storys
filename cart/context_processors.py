from typing import Dict

SESSION_KEY = 'cart_items'
WISHLIST_KEY = 'wishlist_items'


def cart_summary(request) -> Dict[str, int]:
    cart = request.session.get(SESSION_KEY, {}) or {}
    count = sum(int(qty) for qty in cart.values())
    return {
        'cart_item_count': count,
        'wishlist_item_count': len(request.session.get(WISHLIST_KEY, {}) or {}),
    }


