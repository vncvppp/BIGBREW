# shared_state.py
# This file keeps track of the shared cart state across windows

cart_state = {}

def add_item(item_id, item_name, price, quantity=1):
    """Add an item to the cart or increase its quantity."""
    if item_id in cart_state:
        cart_state[item_id]["quantity"] += quantity
    else:
        cart_state[item_id] = {
            "name": item_name,
            "price": price,
            "quantity": quantity
        }

def change_item_qty(item_id, new_qty):
    """Change the quantity of an item."""
    if item_id in cart_state:
        cart_state[item_id]["quantity"] = new_qty
        if new_qty <= 0:
            del cart_state[item_id]

def get_state():
    """Return the current cart state."""
    return cart_state

def clear_cart():
    """Remove all items from the cart."""
    cart_state.clear()

def export_for_checkout():
    """Export cart data for checkout."""
    return [
        {
            "id": item_id,
            "name": data["name"],
            "price": data["price"],
            "quantity": data["quantity"],
            "total": data["price"] * data["quantity"]
        }
        for item_id, data in cart_state.items()
    ]
