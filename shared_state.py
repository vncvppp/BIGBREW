from pathlib import Path
import json
import tempfile
import os

# File-backed shared cart state used across subprocess windows.
# Keeps a JSON file `shared_cart.json` in the project root.

CART_PATH = Path(__file__).parent / "shared_cart.json"

def _default_state():
    return {"cart_items": [], "add_on_total_amount": 0.0}

def load_state():
    try:
        if CART_PATH.exists():
            with CART_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return _default_state()

def save_state(state: dict):
    try:
        # atomic write
        dirp = CART_PATH.parent
        fd, tmppath = tempfile.mkstemp(dir=dirp)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f)
        # move into place
        os.replace(tmppath, CART_PATH)
    except Exception:
        # best-effort; ignore to avoid crashing UIs
        try:
            with CART_PATH.open("w", encoding="utf-8") as f:
                json.dump(state, f)
        except Exception:
            pass

def get_state():
    return load_state()

def add_item(item: dict):
    s = load_state()
    if item.get("is_add_on"):
        try:
            s["add_on_total_amount"] = float(s.get("add_on_total_amount", 0.0)) + float(item.get("price", 0)) * int(item.get("qty", 1))
        except Exception:
            pass
        save_state(s)
        return s

    # merge by name+size+price
    for existing in s.get("cart_items", []):
        try:
            if (
                existing.get("name") == item.get("name") and
                existing.get("size", "Regular") == item.get("size", "Regular") and
                float(existing.get("price", 0)) == float(item.get("price", 0))
            ):
                existing["qty"] = int(existing.get("qty", 1)) + int(item.get("qty", 1))
                break
        except Exception:
            continue
    else:
        s.setdefault("cart_items", []).append({
            "name": item.get("name"),
            "size": item.get("size", "Regular"),
            "price": float(item.get("price", 0)),
            "qty": int(item.get("qty", 1)),
            "is_add_on": item.get("is_add_on", False)
        })
    save_state(s)
    return s

def change_item_qty(index: int, delta: int):
    s = load_state()
    items = s.get("cart_items", [])
    if 0 <= index < len(items):
        items[index]["qty"] = max(0, int(items[index].get("qty", 1)) + int(delta))
        if items[index]["qty"] == 0:
            del items[index]
    save_state(s)
    return s

def clear_cart():
    s = _default_state()
    save_state(s)
    return s

def export_for_checkout():
    s = load_state()
    items = list(s.get("cart_items", []))
    add_on = float(s.get("add_on_total_amount", 0.0))
    if add_on and add_on > 0:
        items.append({
            "name": "Add-On",
            "size": "-",
            "price": float(add_on),
            "qty": 1,
            "is_add_on": True,
        })
    return items
