"""
Shared cart state and database interactions for BigBrew POS.
"""

import base64
import json
import os

import mysql.connector

from app.config import DB_CONFIG

# In-memory cart state
_state = {
    "cart_items": [],  # List of item dicts
    "add_on_total_amount": 0.0,  # Total of all add-on items
    "customer_id": None,  # Currently associated customer (if any)
}


def _normalize_item(item: dict) -> dict:
    """Return a normalized cart item dict with numeric qty/price."""
    if not isinstance(item, dict):
        return {
            "name": "",
            "size": "Regular",
            "price": 0.0,
            "qty": 1,
            "is_add_on": False,
        }
    name = str(item.get("name", ""))
    size = item.get("size", "Regular") or "Regular"
    try:
        qty = int(item.get("qty", 1) or 1)
    except Exception:
        qty = 1
    qty = max(1, qty)
    try:
        price = float(item.get("price", 0.0) or 0.0)
    except Exception:
        price = 0.0
    is_add_on = bool(item.get("is_add_on", False))
    return {
        "product_id": item.get("product_id"),
        "name": name,
        "size": size,
        "price": price,
        "qty": qty,
        "is_add_on": is_add_on,
        "image_path": item.get("image_path"),
        "image_data": item.get("image_data"),
        "product_code": item.get("product_code"),
    }


def _clone_item(item: dict) -> dict:
    norm = _normalize_item(item)
    return {
        "product_id": norm.get("product_id"),
        "name": norm["name"],
        "size": norm["size"],
        "price": float(norm["price"]),
        "qty": int(norm["qty"]),
        "is_add_on": bool(norm["is_add_on"]),
        "image_path": norm.get("image_path"),
        "image_data": norm.get("image_data"),
        "product_code": norm.get("product_code"),
    }


def get_state():
    """Get a copy of the current cart state."""
    return {
        "cart_items": [_clone_item(item) for item in _state["cart_items"]],
        "add_on_total_amount": float(_state["add_on_total_amount"]),
        "customer_id": _state.get("customer_id"),
    }


def add_item(item):
    """Add an item to the cart."""
    normalized = _normalize_item(item)
    if normalized["is_add_on"]:
        _state["add_on_total_amount"] += normalized["price"] * normalized["qty"]
        return
    _state["cart_items"].append(normalized)


def change_item_qty(index, delta):
    """Change quantity of an item at given index."""
    try:
        if not (0 <= index < len(_state["cart_items"])):
            return

        item = _state["cart_items"][index]
        new_qty = max(0, int(item.get("qty", 1)) + delta)

        if new_qty == 0:
            # Remove item if quantity reaches 0
            _state["cart_items"].pop(index)
        else:
            item["qty"] = new_qty
    except (IndexError, ValueError, TypeError):
        pass


def clear_cart():
    """Clear all items from cart."""
    _state["cart_items"].clear()
    _state["add_on_total_amount"] = 0.0


def export_for_checkout():
    """Export current cart state for checkout."""
    if not _state["cart_items"]:
        return None

    return {
        "items": [_clone_item(item) for item in _state["cart_items"]],
        "add_on_total": float(_state["add_on_total_amount"]),
        "customer_id": _state.get("customer_id"),
    }


def set_current_customer(customer_id):
    """Set the currently associated customer for the cart."""
    if customer_id is None:
        _state["customer_id"] = None
        return None
    try:
        cid = int(customer_id)
    except (TypeError, ValueError):
        _state["customer_id"] = None
        return None
    _state["customer_id"] = cid
    return cid


def get_current_customer():
    """Return the currently associated customer_id or None."""
    return _state.get("customer_id")


def save_purchase_to_db(
    customer_id,
    total_amount,
    payment_method,
    items,
    user_id=None,
    proof_of_payment_path=None,
    proof_of_payment_blob=None,
):
    """Save a purchase to the database.

    Ensures an existing `user_id` is provided to satisfy the sales -> users
    foreign key. If none is provided the function will try to pick an
    administrator (or any) user from the `users` table. If no user exists
    it will create a minimal system user and use its id.
    """

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Ensure we have a valid user_id to satisfy foreign key constraints
        if not user_id:
            # Find users table primary key column name (best-effort)
            pk = None
            try:
                cursor.execute(
                    """
                    SELECT COLUMN_NAME
                    FROM information_schema.key_column_usage
                    WHERE table_schema=%s AND table_name='users' AND constraint_name='PRIMARY'
                    """,
                    (DB_CONFIG["database"],),
                )
                pk_row = cursor.fetchone()
                if pk_row and pk_row.get("COLUMN_NAME"):
                    pk = pk_row["COLUMN_NAME"]
            except Exception:
                pk = None

            # Fallback to common names
            if not pk:
                try:
                    cursor.execute(
                        """
                        SELECT COLUMN_NAME
                        FROM information_schema.columns
                        WHERE table_schema=%s AND table_name='users'
                        """,
                        (DB_CONFIG["database"],),
                    )
                    tmp_cols = [r["COLUMN_NAME"] for r in cursor.fetchall()]
                    if "user_id" in tmp_cols:
                        pk = "user_id"
                    elif "id" in tmp_cols:
                        pk = "id"
                except Exception:
                    pk = None

            # Try to find an admin user using the detected pk
            try:
                if pk:
                    cursor.execute(
                        f"SELECT {pk} as pk FROM users WHERE user_type IN ('admin','administrator','manager') LIMIT 1"
                    )
                    row = cursor.fetchone()
                    if row and row.get("pk"):
                        user_id = row["pk"]
                    else:
                        cursor.execute(f"SELECT {pk} as pk FROM users LIMIT 1")
                        row = cursor.fetchone()
                        if row and row.get("pk"):
                            user_id = row["pk"]
                else:
                    # Try common column name
                    cursor.execute(
                        "SELECT user_id FROM users WHERE user_type IN ('admin','administrator','manager') LIMIT 1"
                    )
                    row = cursor.fetchone()
                    if row and row.get("user_id"):
                        user_id = row["user_id"]
                    else:
                        cursor.execute("SELECT user_id FROM users LIMIT 1")
                        row = cursor.fetchone()
                        if row and row.get("user_id"):
                            user_id = row["user_id"]
            except Exception:
                user_id = None

            # Validate that the found user_id actually exists
            if user_id and pk:
                try:
                    cursor.execute(f"SELECT COUNT(1) AS c FROM users WHERE {pk}=%s", (user_id,))
                    r = cursor.fetchone()
                    if not r or r.get("c", 0) == 0:
                        user_id = None
                except Exception:
                    user_id = None

        # If still no user_id, create a minimal system user using whatever
        # columns are available on the users table (best-effort).
        if not user_id:
            # Inspect users table columns
            cursor.execute(
                """
                SELECT COLUMN_NAME
                FROM information_schema.columns
                WHERE table_schema=%s AND table_name='users'
                """,
                (DB_CONFIG["database"],),
            )
            cols = [r["COLUMN_NAME"] for r in cursor.fetchall()] if cursor.rowcount else []

            # Build a minimal insert using columns that are likely present
            insert_cols = []
            insert_vals = []
            if "username" in cols:
                insert_cols.append("username")
                insert_vals.append("system")
            if "email" in cols:
                insert_cols.append("email")
                insert_vals.append("system@local")
            if "password_hash" in cols:
                insert_cols.append("password_hash")
                insert_vals.append("")
            elif "password" in cols:
                insert_cols.append("password")
                insert_vals.append("")
            if "user_type" in cols:
                insert_cols.append("user_type")
                insert_vals.append("system")
            if "first_name" in cols:
                insert_cols.append("first_name")
                insert_vals.append("System")
            if "last_name" in cols:
                insert_cols.append("last_name")
                insert_vals.append("User")
            if "is_active" in cols:
                insert_cols.append("is_active")
                insert_vals.append(True)

            if insert_cols:
                placeholders = ",".join(["%s"] * len(insert_vals))
                col_list = ",".join(insert_cols)
                sql = f"INSERT INTO users ({col_list}) VALUES ({placeholders})"
                try:
                    cursor.execute(sql, tuple(insert_vals))
                    user_id = cursor.lastrowid
                except Exception:
                    user_id = None
            else:
                # Try some common single-column inserts if available
                tried = False
                try_cols = ["username", "user_type", "email"]
                for column in try_cols:
                    if column in cols:
                        try:
                            cursor.execute(
                                f"INSERT INTO users ({column}) VALUES (%s)", ("system",)
                            )
                            user_id = cursor.lastrowid
                            tried = True
                            break
                        except Exception:
                            continue

                if not tried:
                    # Last resort: attempt empty-value insert (works if table has defaults)
                    try:
                        cursor.execute("INSERT INTO users () VALUES ()")
                        user_id = cursor.lastrowid
                    except Exception:
                        user_id = None

            # Validate created user
            if user_id and pk:
                try:
                    cursor.execute(f"SELECT COUNT(1) AS c FROM users WHERE {pk}=%s", (user_id,))
                    r = cursor.fetchone()
                    if not r or r.get("c", 0) == 0:
                        user_id = None
                except Exception:
                    user_id = None

        if not user_id:
            raise RuntimeError("No valid user found or created to associate with sale")

        # Insert main sale record including user_id to satisfy FK
        cursor.execute(
            """
            INSERT INTO sales (
                customer_id,
                user_id,
                total_amount,
                payment_method,
                proof_of_payment_path,
                proof_of_payment_blob
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                customer_id,
                user_id,
                total_amount,
                payment_method,
                proof_of_payment_path,
                proof_of_payment_blob,
            ),
        )
        sale_id = cursor.lastrowid

        # Insert each sale item
        for item in items:
            product_id = item.get("product_id") or item.get("id") or None
            qty = int(item.get("qty", 1))
            price = float(item.get("price", 0.0))

            cursor.execute(
                """
                INSERT INTO sale_items (sale_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
                """,
                (sale_id, product_id, qty, price),
            )

        conn.commit()

        return sale_id

    except Exception as exc:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        print(f"Failed to save purchase: {exc}")
        return None
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_product_info(product_name):
    """Get product information from database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                product_id,
                COALESCE(NULLIF(product_name, ''), NULLIF(product_code, '')) AS product_name,
                price,
                price_regular,
                price_large,
                category_id,
                product_code,
                image_path,
                image_blob
            FROM products
            WHERE product_name = %s OR product_code = %s
            LIMIT 1
            """,
            (product_name, product_name),
        )

        row = cursor.fetchone()
        if row:
            normalized_name = row.get("product_name") or product_name
            row["name"] = normalized_name
        return row
    except Exception as exc:
        print(f"Failed to get product info: {exc}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def add_item_from_db(product_name, size="Regular", qty=1):
    """Add an item to cart using database product information."""
    product = get_product_info(product_name)
    if not product:
        return False

    size_value = size or "Regular"
    price_regular = product.get("price_regular") or product.get("price")
    price_large = product.get("price_large") or price_regular
    price_to_use = price_large if str(size_value).lower() == "large" else price_regular

    image_data = None
    blob = product.get("image_blob")
    if blob:
        try:
            image_data = "base64," + base64.b64encode(blob).decode("ascii")
        except Exception:
            image_data = None

    add_item(
        {
            "product_id": product["product_id"],
            "name": product["name"],
            "price": price_to_use,
            "size": size_value,
            "qty": qty,
            "product_code": product.get("product_code"),
            "image_path": product.get("image_path"),
            "image_data": image_data,
        }
    )
    return True


# Initialize by loading saved state if it exists
_state_file = "shared_cart.json"
if os.path.exists(_state_file):
    try:
        with open(_state_file, "r", encoding="utf-8") as file:
            saved_state = json.load(file)
            _state.update(saved_state)
    except Exception:
        pass


