"""
Shared state manager for shopping cart functionality.
Maintains cart items and related state that needs to be shared between
different parts of the application.
"""

import json
import os
from datetime import datetime

# Global state dictionary
_state = {
    "cart_items": [],  # List of items in cart
    "add_on_total_amount": 0.0,  # Total amount for add-ons
}

def get_state():
    """Get the current state dictionary"""
    return _state

def add_item(item):
    """Add an item to the cart"""
    if not isinstance(item, dict):
        raise ValueError("Item must be a dictionary")
        
    required_fields = ['name', 'price', 'qty']
    for field in required_fields:
        if field not in item:
            raise ValueError(f"Item missing required field: {field}")
    
    # Convert price to float and qty to int
    try:
        item['price'] = float(item['price'])
        item['qty'] = int(item['qty'])
    except (ValueError, TypeError):
        raise ValueError("Invalid price or quantity format")
    
    if item['qty'] < 1:
        raise ValueError("Quantity must be positive")
        
    # If it's an add-on item, update the add-on total
    if item.get('is_add_on'):
        _state['add_on_total_amount'] += item['price'] * item['qty']
    
    _state['cart_items'].append(item)
    _save_state()

def change_item_qty(index, delta):
    """Change quantity of item at index by delta amount"""
    if not isinstance(index, int):
        raise ValueError("Index must be an integer")
    if index < 0 or index >= len(_state['cart_items']):
        raise IndexError("Invalid item index")
        
    item = _state['cart_items'][index]
    new_qty = item['qty'] + delta
    
    if new_qty < 1:
        # Remove item if quantity becomes 0
        _state['cart_items'].pop(index)
        if item.get('is_add_on'):
            _state['add_on_total_amount'] -= item['price'] * item['qty']
    else:
        # Update quantity
        if item.get('is_add_on'):
            _state['add_on_total_amount'] += item['price'] * delta
        item['qty'] = new_qty
        
    _save_state()

def clear_cart():
    """Remove all items from cart"""
    _state['cart_items'].clear()
    _state['add_on_total_amount'] = 0.0
    _save_state()

def export_for_checkout():
    """Export cart items in format needed for checkout"""
    if not _state['cart_items']:
        return None
        
    # Calculate totals
    subtotal = sum(item['price'] * item['qty'] for item in _state['cart_items'] 
                  if not item.get('is_add_on'))
    add_on_total = _state['add_on_total_amount']
    total = subtotal + add_on_total
    
    export_data = {
        'items': _state['cart_items'],
        'subtotal': subtotal,
        'add_on_total': add_on_total,
        'total': total,
        'exported_at': datetime.now().isoformat()
    }
    
    return export_data

def _save_state():
    """Save current state to shared cart file"""
    try:
        with open('shared_cart.json', 'w') as f:
            json.dump(_state, f)
    except Exception:
        # Fail silently - state saving is best-effort
        pass

def _load_state():
    """Load state from shared cart file if it exists"""
    try:
        if os.path.exists('shared_cart.json'):
            with open('shared_cart.json', 'r') as f:
                loaded_state = json.load(f)
                _state.update(loaded_state)
    except Exception:
        # Fail silently - state loading is best-effort
        pass

# Load saved state on module import
_load_state()
