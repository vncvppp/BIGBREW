#!/usr/bin/env python3
"""
BigBrew POS System - Database Initialization
Combines table definitions and seed data into a single, maintainable script.
"""

from __future__ import annotations

import sys
from typing import Callable, Iterable, Tuple

import bcrypt
import mysql.connector
from mysql.connector import Error
from mysql.connector.cursor import MySQLCursor

from app.config import DB_CONFIG
from pathlib import Path

SERVER_CONFIG = {
    "host": DB_CONFIG["host"],
    "port": DB_CONFIG["port"],
    "user": DB_CONFIG["user"],
    "password": DB_CONFIG["password"],
}

DATABASE_NAME = DB_CONFIG["database"]

CategorySeed = Tuple[int, str, str, str]
ProductSeed = Tuple[str, str, str, str, float, float]
CustomerSeed = Tuple[str, str, str, str, str, str, str, str]


def table_has_column(cursor: MySQLCursor, table_name: str, column_name: str) -> bool:
    """Check if a given column exists on a table."""
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (DATABASE_NAME, table_name, column_name),
    )
    return cursor.fetchone() is not None


def first_existing_column(cursor: MySQLCursor, table_name: str, *candidates: str) -> str:
    """Return the first column name that exists on the table from the provided candidates."""
    for column in candidates:
        if table_has_column(cursor, table_name, column):
            return column
    raise RuntimeError(f"No matching columns found on {table_name} for candidates {candidates}")


def connect_to_server():
    """Connect to MySQL without selecting a database."""
    try:
        return mysql.connector.connect(**SERVER_CONFIG)
    except Error as exc:
        print(f"[ERROR] Unable to connect to MySQL server: {exc}")
        return None


def connect_to_database():
    """Connect directly to the BigBrew database."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as exc:
        print(f"[ERROR] Unable to connect to database '{DATABASE_NAME}': {exc}")
        return None


def ensure_database():
    """Create the database if it does not already exist."""
    connection = connect_to_server()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print(f"[OK] Database '{DATABASE_NAME}' is ready.")
        return True
    except Error as exc:
        print(f"[ERROR] Unable to create database '{DATABASE_NAME}': {exc}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def create_categories_table(cursor: MySQLCursor):
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS categories (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            legacy_category_id INT UNIQUE,
        name VARCHAR(100) NOT NULL,
        category_name VARCHAR(100) NOT NULL,
        description TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )
    # Handle legacy schemas where the columns were previously named `id` and `category_id`
    try:
        # If the secondary identifier column hasn't been renamed yet, rename it first
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'categories' AND COLUMN_NAME = 'legacy_category_id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_column = cursor.fetchone() is not None
        if not has_legacy_column:
            cursor.execute(
                """
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'categories' AND COLUMN_NAME = 'category_id' AND COLUMN_KEY <> 'PRI'
                """,
                (DATABASE_NAME,),
            )
            has_old_unique_column = cursor.fetchone() is not None
            if has_old_unique_column:
                cursor.execute(
                    """
                    ALTER TABLE categories
                    CHANGE COLUMN category_id legacy_category_id INT UNIQUE
                    """
                )

        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'categories' AND COLUMN_NAME = 'id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_id = cursor.fetchone() is not None
        if has_legacy_id:
            cursor.execute(
                """
                ALTER TABLE categories
                CHANGE COLUMN id category_id INT AUTO_INCREMENT PRIMARY KEY
                """
            )
    except Error:
        pass

    print("[OK] categories table")


def create_customers_table(cursor: MySQLCursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_code VARCHAR(32) NOT NULL UNIQUE,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            customer_type ENUM('regular', 'vip', 'student') NOT NULL DEFAULT 'regular',
            phone VARCHAR(20),
            address TEXT,
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            is_verified TINYINT(1) NOT NULL DEFAULT 0,
            email_verified TINYINT(1) NOT NULL DEFAULT 0,
            loyalty_points INT NOT NULL DEFAULT 0,
            total_spent DECIMAL(12,2) NOT NULL DEFAULT 0,
            last_order_date TIMESTAMP NULL DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    cursor.execute(
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS loyalty_points INT NOT NULL DEFAULT 0"
    )
    cursor.execute(
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_spent DECIMAL(12,2) NOT NULL DEFAULT 0"
    )
    cursor.execute(
        "ALTER TABLE customers ADD COLUMN IF NOT EXISTS last_order_date TIMESTAMP NULL DEFAULT NULL"
    )
    print("[OK] customers table")


def create_users_table(cursor: MySQLCursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            user_type ENUM('admin', 'staff', 'inventory_manager') NOT NULL DEFAULT 'staff',
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            last_login TIMESTAMP NULL DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    # Align legacy schema where the primary key column might still be named 'id'
    try:
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'user_id'
            """,
            (DATABASE_NAME,),
        )
        has_user_id = cursor.fetchone() is not None
        if not has_user_id:
            cursor.execute(
                """
                ALTER TABLE users
                CHANGE COLUMN id user_id INT AUTO_INCREMENT PRIMARY KEY
                """
            )
    except Error:
        pass
    print("[OK] users table")


def create_products_table(cursor: MySQLCursor):
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            legacy_product_id INT UNIQUE,
        category_id INT,
        product_code VARCHAR(50),
        product_name VARCHAR(100) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) DEFAULT 0,
        price_regular DECIMAL(10,2) DEFAULT 0,
        price_large DECIMAL(10,2) DEFAULT 0,
        image_path VARCHAR(255),
        image_blob LONGBLOB,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )
    try:
        # Rename legacy secondary identifier first
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'products' AND COLUMN_NAME = 'legacy_product_id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_column = cursor.fetchone() is not None
        if not has_legacy_column:
            cursor.execute(
                """
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'products' AND COLUMN_NAME = 'product_id' AND COLUMN_KEY <> 'PRI'
                """,
                (DATABASE_NAME,),
            )
            has_old_unique_column = cursor.fetchone() is not None
            if has_old_unique_column:
                cursor.execute(
                    """
                    ALTER TABLE products
                    CHANGE COLUMN product_id legacy_product_id INT UNIQUE
                    """
                )

        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'products' AND COLUMN_NAME = 'id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_id = cursor.fetchone() is not None
        if has_legacy_id:
            cursor.execute(
                """
                ALTER TABLE products
                CHANGE COLUMN id product_id INT AUTO_INCREMENT PRIMARY KEY
                """
            )
        cursor.execute(
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS image_blob LONGBLOB"
        )
        try:
            cursor.execute(
                "ALTER TABLE products DROP COLUMN IF EXISTS name"
            )
        except Error:
            pass
    except Error:
        pass
    print("[OK] products table")


def create_inventory_table(cursor: MySQLCursor):
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INT AUTO_INCREMENT PRIMARY KEY,
            legacy_inventory_id INT UNIQUE,
        product_id INT NOT NULL,
        current_stock INT NOT NULL DEFAULT 0,
        minimum_stock INT NOT NULL DEFAULT 0,
        reorder_point INT NOT NULL DEFAULT 0,
        quantity INT NOT NULL DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )
    try:
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'inventory' AND COLUMN_NAME = 'legacy_inventory_id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_column = cursor.fetchone() is not None
        if not has_legacy_column:
            cursor.execute(
                """
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'inventory' AND COLUMN_NAME = 'inventory_id' AND COLUMN_KEY <> 'PRI'
                """,
                (DATABASE_NAME,),
            )
            has_old_unique = cursor.fetchone() is not None
            if has_old_unique:
                cursor.execute(
                    """
                    ALTER TABLE inventory
                    CHANGE COLUMN inventory_id legacy_inventory_id INT UNIQUE
                    """
                )

        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'inventory' AND COLUMN_NAME = 'id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_id = cursor.fetchone() is not None
        if has_legacy_id:
            cursor.execute(
                """
                ALTER TABLE inventory
                CHANGE COLUMN id inventory_id INT AUTO_INCREMENT PRIMARY KEY
                """
            )
    except Error:
        pass
    print("[OK] inventory table")


def create_purchases_table(cursor: MySQLCursor):
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS purchases (
            purchase_id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_cost DECIMAL(10,2) NOT NULL,
        total_cost DECIMAL(10,2) NOT NULL,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )
    try:
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'purchases' AND COLUMN_NAME = 'id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_id = cursor.fetchone() is not None
        if has_legacy_id:
            cursor.execute(
                """
                ALTER TABLE purchases
                CHANGE COLUMN id purchase_id INT AUTO_INCREMENT PRIMARY KEY
                """
            )
    except Error:
        pass
    print("[OK] purchases table")


def create_purchase_items_table(cursor: MySQLCursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS purchase_items (
            purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
            purchase_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )
    try:
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'purchase_items' AND COLUMN_NAME = 'id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_id = cursor.fetchone() is not None
        if has_legacy_id:
            cursor.execute(
                """
                ALTER TABLE purchase_items
                CHANGE COLUMN id purchase_item_id INT AUTO_INCREMENT PRIMARY KEY
                """
            )
    except Error:
        pass
    print("[OK] purchase_items table")


def create_sales_table(cursor: MySQLCursor):
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS sales (
            sale_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NULL,
        user_id INT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        payment_method ENUM('cash', 'card', 'gcash') DEFAULT 'cash',
        proof_of_payment_path VARCHAR(255),
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )
    try:
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'sales' AND COLUMN_NAME = 'id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_id = cursor.fetchone() is not None
        if has_legacy_id:
            cursor.execute(
                """
                ALTER TABLE sales
                CHANGE COLUMN id sale_id INT AUTO_INCREMENT PRIMARY KEY
                """
            )
    except Error:
        pass

    try:
        cursor.execute(
            """
            ALTER TABLE sales
            ADD COLUMN IF NOT EXISTS proof_of_payment_path VARCHAR(255)
            """
        )
    except Error:
        pass

    try:
        cursor.execute(
            """
            ALTER TABLE sales
            MODIFY COLUMN payment_method ENUM('cash', 'card', 'gcash') DEFAULT 'cash'
            """
        )
    except Error:
        pass
    print("[OK] sales table")


def create_sale_items_table(cursor: MySQLCursor):
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS sale_items (
            sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
        sale_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )
    try:
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'sale_items' AND COLUMN_NAME = 'id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_id = cursor.fetchone() is not None
        if has_legacy_id:
            cursor.execute(
                """
                ALTER TABLE sale_items
                CHANGE COLUMN id sale_item_id INT AUTO_INCREMENT PRIMARY KEY
                """
            )
    except Error:
        pass
    print("[OK] sale_items table")


def create_otp_verification_table(cursor: MySQLCursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS otp_verification (
            otp_id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) NOT NULL,
            otp_code VARCHAR(6) NOT NULL,
            purpose VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NULL,
            is_used TINYINT(1) NOT NULL DEFAULT 0,
            attempts INT NOT NULL DEFAULT 0
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )
    try:
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'otp_verification' AND COLUMN_NAME = 'id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_id = cursor.fetchone() is not None
        if has_legacy_id:
            cursor.execute(
                """
                ALTER TABLE otp_verification
                CHANGE COLUMN id otp_id INT AUTO_INCREMENT PRIMARY KEY
                """
            )
    except Error:
        pass
    try:
        cursor.execute(
            "ALTER TABLE otp_verification ADD COLUMN IF NOT EXISTS expires_at DATETIME NULL"
        )
        cursor.execute(
            "ALTER TABLE otp_verification ADD COLUMN IF NOT EXISTS is_used TINYINT(1) NOT NULL DEFAULT 0"
        )
        cursor.execute(
            "ALTER TABLE otp_verification ADD COLUMN IF NOT EXISTS attempts INT NOT NULL DEFAULT 0"
        )
    except Error:
        pass
    print("[OK] otp_verification table")


def create_loyalty_rewards_table(cursor: MySQLCursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS loyalty_rewards (
            loyalty_reward_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            points INT NOT NULL DEFAULT 0,
            description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    )
    try:
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'loyalty_rewards' AND COLUMN_NAME = 'id'
            """,
            (DATABASE_NAME,),
        )
        has_legacy_id = cursor.fetchone() is not None
        if has_legacy_id:
            cursor.execute(
                """
                ALTER TABLE loyalty_rewards
                CHANGE COLUMN id loyalty_reward_id INT AUTO_INCREMENT PRIMARY KEY
                """
            )
    except Error:
        pass
    print("[OK] loyalty_rewards table")


TABLE_CREATORS: Iterable[Tuple[str, Callable[[MySQLCursor], None]]] = (
    ("categories", create_categories_table),
    ("customers", create_customers_table),
    ("users", create_users_table),
    ("products", create_products_table),
    ("inventory", create_inventory_table),
    ("purchases", create_purchases_table),
    ("purchase_items", create_purchase_items_table),
    ("sales", create_sales_table),
    ("sale_items", create_sale_items_table),
    ("otp_verification", create_otp_verification_table),
    ("loyalty_rewards", create_loyalty_rewards_table),
)


CATEGORY_SEED: Tuple[CategorySeed, ...] = (
        (1, "Milk Tea", "milkTea", "Milk tea beverages"),
        (2, "Praf", "praf", "PRAF beverages"),
        (3, "Fruit Tea", "fruitTea", "Fruit tea beverages"),
        (4, "Coffee", "coffee", "Coffee beverages"),
        (5, "Brosty", "brosty", "Brosty beverages"),
        (6, "Add-ons", "add-ons", "Additional toppings and add-ons"),
)

PRODUCT_SEED: Tuple[ProductSeed, ...] = (
        # Milk Tea
        ("milkTea", "MT001", "Cookies n Cream", "Cookies and cream flavored milk tea", 25.00, 29.00),
        ("milkTea", "MT002", "Okinawa", "Okinawa-style roasted milk tea", 25.00, 29.00),
        ("milkTea", "MT003", "Dark Choco", "Dark chocolate milk tea", 25.00, 29.00),
        ("milkTea", "MT004", "Matcha", "Japanese green tea with milk", 25.00, 29.00),
        ("milkTea", "MT005", "Red Velvet", "Red velvet flavored milk tea", 25.00, 29.00),
        ("milkTea", "MT006", "Winter Melon", "Winter melon milk tea", 25.00, 29.00),
        ("milkTea", "MT007", "Cheesecake", "Cheesecake flavored milk tea", 25.00, 29.00),
        ("milkTea", "MT008", "Chocolate", "Classic chocolate milk tea", 25.00, 29.00),
        ("milkTea", "MT009", "Taro", "Taro flavored milk tea", 25.00, 29.00),
        ("milkTea", "MT010", "Salted Caramel", "Salted caramel milk tea", 25.00, 29.00),
        # Coffee
        ("coffee", "CF001", "Brusko", "Strong brewed coffee", 25.00, 29.00),
        ("coffee", "CF002", "Mocha", "Coffee with chocolate", 25.00, 29.00),
        ("coffee", "CF003", "Macchiato", "Espresso with steamed milk", 25.00, 29.00),
        ("coffee", "CF004", "Vanilla", "Coffee with vanilla flavoring", 25.00, 29.00),
        ("coffee", "CF005", "Caramel", "Coffee with caramel flavoring", 25.00, 29.00),
        ("coffee", "CF006", "Matcha", "Coffee with matcha green tea", 25.00, 29.00),
        ("coffee", "CF007", "Fudge", "Coffee with chocolate fudge", 25.00, 29.00),
        ("coffee", "CF008", "Spanish Latte", "Coffee with sweetened condensed milk", 25.00, 29.00),
)

CUSTOMER_SEED: Tuple[CustomerSeed, ...] = (
    ("CUST-000001", "john.doe", "john@example.com", "John", "Doe", "regular", "09123456789", "123 Main St"),
    ("CUST-000002", "jane.smith", "jane@example.com", "Jane", "Smith", "regular", "09123456790", "456 Oak Ave"),
)


def seed_categories(cursor: MySQLCursor):
    for cid, display_name, slug, description in CATEGORY_SEED:
        pk_column = first_existing_column(cursor, "categories", "category_id", "id")
        legacy_column = first_existing_column(cursor, "categories", "legacy_category_id", "category_id", pk_column)

        columns = [pk_column]
        values = [cid]
        if legacy_column != pk_column:
            columns.append(legacy_column)
            values.append(cid)

        columns.extend(["name", "category_name", "description"])
        values.extend([display_name, slug, description])

        placeholders = ", ".join(["%s"] * len(columns))
        column_list = ", ".join(columns)

        updates = [
            "name = VALUES(name)",
            "category_name = VALUES(category_name)",
            "description = VALUES(description)",
        ]
        if legacy_column != pk_column:
            updates.insert(0, f"{legacy_column} = VALUES({legacy_column})")

        sql = f"""
            INSERT INTO categories ({column_list})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {', '.join(updates)}
        """
        cursor.execute(sql, tuple(values))


def seed_products(cursor: MySQLCursor):
    category_lookup = {slug: cid for cid, _, slug, _ in CATEGORY_SEED}
    for index, (category_slug, code, name, description, price_regular, price_large) in enumerate(PRODUCT_SEED, start=1):
        category_id = category_lookup.get(category_slug)
        pk_column = first_existing_column(cursor, "products", "product_id", "id")
        legacy_column = first_existing_column(cursor, "products", "legacy_product_id", "product_id", pk_column)

        columns = [pk_column]
        values = [index]
        if legacy_column != pk_column:
            columns.append(legacy_column)
            values.append(index)

        columns.extend(
            [
                "category_id",
                "product_code",
                "product_name",
                "description",
                "price",
                "price_regular",
                "price_large",
                "image_path",
                "image_blob",
            ]
        )

        image_path = None
        try:
            image_filename = f"{code.lower()}.png"
            image_path = (Path(__file__).resolve().parents[2] / "resources" / "products" / image_filename)
            if image_path.exists():
                with open(image_path, "rb") as img_file:
                    image_blob = img_file.read()
            else:
                image_blob = None
                image_path = None
        except Exception:
            image_blob = None
            image_path = None

        values.extend(
            [
                category_id,
                code,
                name,
                description,
                price_regular,
                price_regular,
                price_large,
                str(image_path) if image_path else None,
                image_blob,
            ]
        )

        updates = [
            "category_id = VALUES(category_id)",
            "product_name = VALUES(product_name)",
            "description = VALUES(description)",
            "price = VALUES(price)",
            "price_regular = VALUES(price_regular)",
            "price_large = VALUES(price_large)",
            "image_path = VALUES(image_path)",
            "image_blob = VALUES(image_blob)",
        ]
        if legacy_column != pk_column:
            updates.insert(0, f"{legacy_column} = VALUES({legacy_column})")

        placeholders = ", ".join(["%s"] * len(columns))
        column_list = ", ".join(columns)

        sql = f"""
            INSERT INTO products ({column_list})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {', '.join(updates)}
        """
        cursor.execute(sql, tuple(values))


def seed_inventory(cursor: MySQLCursor):
    total_products = len(PRODUCT_SEED)
    for index in range(1, total_products + 1):
        pk_column = first_existing_column(cursor, "inventory", "inventory_id", "id")
        legacy_column = first_existing_column(cursor, "inventory", "legacy_inventory_id", "inventory_id", pk_column)

        columns = [pk_column]
        values = [index]
        if legacy_column != pk_column:
            columns.append(legacy_column)
            values.append(index)

        columns.extend(
            [
                "product_id",
                "current_stock",
                "minimum_stock",
                "reorder_point",
                "quantity",
            ]
        )
        values.extend([index, 100, 10, 20, 100])

        updates = [
            "current_stock = VALUES(current_stock)",
            "minimum_stock = VALUES(minimum_stock)",
            "reorder_point = VALUES(reorder_point)",
            "quantity = VALUES(quantity)",
        ]
        if legacy_column != pk_column:
            updates.insert(0, f"{legacy_column} = VALUES({legacy_column})")

        placeholders = ", ".join(["%s"] * len(columns))
        column_list = ", ".join(columns)

        sql = f"""
            INSERT INTO inventory ({column_list})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {', '.join(updates)}
        """
        cursor.execute(sql, tuple(values))


def seed_customers(cursor: MySQLCursor):
    default_password = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode("utf-8")
    for (
        customer_code,
        username,
        email,
        first_name,
        last_name,
        customer_type,
        phone,
        address,
    ) in CUSTOMER_SEED:
        cursor.execute(
            """
            INSERT INTO customers (
                customer_code, username, email, password_hash,
                first_name, last_name, customer_type, phone, address,
                is_active, is_verified, email_verified
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                first_name = VALUES(first_name),
                last_name = VALUES(last_name),
                customer_type = VALUES(customer_type),
                phone = VALUES(phone),
                address = VALUES(address),
                is_active = VALUES(is_active),
                is_verified = VALUES(is_verified),
                email_verified = VALUES(email_verified)
            """,
            (
                customer_code,
                username,
                email,
                default_password,
                first_name,
                last_name,
                customer_type,
                phone,
                address,
                1,
                1,
                1,
            ),
        )


def seed_admin_user(cursor: MySQLCursor):
    password_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8")
    cursor.execute(
        """
        INSERT INTO users (
            username, email, password_hash, user_type,
            first_name, last_name, is_active
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            password_hash = VALUES(password_hash),
            user_type = VALUES(user_type),
            is_active = VALUES(is_active),
            first_name = VALUES(first_name),
            last_name = VALUES(last_name)
        """,
        ("admin", "admin@bigbrew.com", password_hash, "admin", "Admin", "User", 1),
    )


def insert_initial_data(cursor: MySQLCursor):
    print("[INFO] Seeding reference data...")
    seed_admin_user(cursor)
    seed_categories(cursor)
    seed_products(cursor)
    seed_inventory(cursor)
    seed_customers(cursor)
    print("[OK] Seed data applied.")


def initialize_system_database():
    print("============================================================")
    print("BigBrew POS System - Database Initialization")
    print("============================================================")

    if not ensure_database():
        return False

    connection = connect_to_database()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        for name, creator in TABLE_CREATORS:
            creator(cursor)

        insert_initial_data(cursor)
        connection.commit()
        print("[SUCCESS] All tables created and seed data inserted.")
        return True
    except Error as exc:
        print(f"[ERROR] Database initialization failed: {exc}")
        if connection.is_connected():
            connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def main():
    if not DB_CONFIG.get("host") or not DATABASE_NAME:
        print("[ERROR] Database configuration is incomplete. Check config.py.")
        return False

    print("[INFO] Starting BigBrew POS database initialization...")
    success = initialize_system_database()

    if success:
        print("------------------------------------------------------------")
        print("Default admin credentials:")
        print("  Username: admin")
        print("  Email   : admin@bigbrew.com")
        print("  Password: admin123")
        print("Please change the admin password after first login.")
        print("------------------------------------------------------------")

    return success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
