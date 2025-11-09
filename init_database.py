#!/usr/bin/env python3
"""
BigBrew POS System - Database Initialization Script
Creates all necessary tables and initial data for the BigBrew POS system
"""

import mysql.connector
from mysql.connector import Error
import os
import sys
from config import DB_CONFIG

def get_database_connection():
    """Get database connection without specifying database name"""
    try:
        # Connect without database first
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL server: {e}")
        return None

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    connection = get_database_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{DB_CONFIG['database']}' created successfully")
        return True
    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def initialize_system_database():
    """Initialize the complete database schema for BigBrew POS System"""
    print("=" * 60)
    print("BigBrew POS System - Database Initialization")
    print("=" * 60)
    
    # First create the database
    if not create_database_if_not_exists():
        return False
    
    # Now connect to the specific database
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print(f"✅ Connected to database: {DB_CONFIG['database']}")
        
        # Create all tables in correct order (dependencies first)
        create_categories_table(cursor)
        create_products_table(cursor)
        create_customers_table(cursor)
        create_inventory_table(cursor)
        create_otp_verification_table(cursor)
        create_purchases_table(cursor)
        create_users_table(cursor)
        create_sales_table(cursor)
        create_sale_items_table(cursor)
        
    # Remove this section as we now have the data insertion directly in this file
        
        # Commit all changes
        connection.commit()
        print("✅ All tables created and initial data inserted successfully")
        
        return True
        
    except Error as e:
        print(f"❌ Database initialization failed: {e}")
        if connection.is_connected():
            connection.rollback()
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_categories_table(cursor):
    """Create categories table with legacy-compatible structure"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category_id INT UNIQUE,
        name VARCHAR(100) NOT NULL,
        category_name VARCHAR(100) NOT NULL,
        description TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Categories table created")

def create_products_table(cursor):
    """Create products table for product management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT UNIQUE,
        category_id INT,
        product_code VARCHAR(50),
        name VARCHAR(100) NOT NULL,
        product_name VARCHAR(100),
        description TEXT,
        cost_price DECIMAL(10,2) DEFAULT 0,
        unit_price DECIMAL(10,2) DEFAULT 0,
        price DECIMAL(10,2) DEFAULT 0,
        price_regular DECIMAL(10,2) DEFAULT 0,
        price_large DECIMAL(10,2) DEFAULT 0,
        image_path VARCHAR(255),
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Products table created")

def create_customers_table(cursor):
    """Create customers table for customer management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        phone VARCHAR(20),
        address TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Customers table created")

def create_inventory_table(cursor):
    """Create inventory table for stock management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS inventory (
        id INT AUTO_INCREMENT PRIMARY KEY,
        inventory_id INT UNIQUE,
        product_id INT NOT NULL,
        current_stock INT NOT NULL DEFAULT 0,
        minimum_stock INT NOT NULL DEFAULT 0,
        reorder_point INT NOT NULL DEFAULT 0,
        quantity INT NOT NULL DEFAULT 0,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Inventory table created")

def create_otp_verification_table(cursor):
    """Create otp_verification table for OTP management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS otp_verification (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(100) NOT NULL,
        otp VARCHAR(6) NOT NULL,
        purpose VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ OTP verification table created")

def create_purchases_table(cursor):
    """Create purchases table for inventory purchases"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS purchases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_cost DECIMAL(10,2) NOT NULL,
        total_cost DECIMAL(10,2) NOT NULL,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Purchases table created")

def create_sales_table(cursor):
    """Create sales table for transactions"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sales (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NULL,
        user_id INT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        payment_method ENUM('cash', 'card') DEFAULT 'cash',
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Sales table created")

def create_sale_items_table(cursor):
    """Create sale_items table for sale line items"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sale_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sale_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Sale items table created")

def create_users_table(cursor):
    """Create users table for staff accounts"""
    create_table_sql = """
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
    cursor.execute(create_table_sql)
    print("✅ Users table created")
    print("\n📝 Inserting initial data...")
    
    # Insert default admin user
    from hashlib import sha256
    admin_password = sha256("admin123".encode()).hexdigest()
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, user_type, first_name, last_name, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            password_hash = VALUES(password_hash),
            user_type = VALUES(user_type),
            is_active = VALUES(is_active)
    """, ('admin', 'admin@bigbrew.com', admin_password, 'admin', 'Admin', 'User', 1))
    
    # Insert default categories (matching db_init_products.sql)
    categories = [
        (1, "Milk Tea", "milkTea", "Milk tea beverages"),
        (2, "Praf", "praf", "PRAF beverages"),
        (3, "Fruit Tea", "fruitTea", "Fruit tea beverages"),
        (4, "Coffee", "coffee", "Coffee beverages"),
        (5, "Brosty", "brosty", "Brosty beverages"),
        (6, "Add-ons", "add-ons", "Additional toppings and add-ons"),
    ]

    for cid, display_name, slug, description in categories:
        cursor.execute(
            """
            INSERT INTO categories (id, category_id, name, category_name, description)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                category_name = VALUES(category_name),
                description = VALUES(description)
            """,
            (cid, cid, display_name, slug, description),
        )

    category_map = {slug: cid for cid, _, slug, _ in categories}

    # Insert default products (matching db_init_products.sql content)
    products = [
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
    ]

    for idx, (category_slug, code, name, desc, cost_price, unit_price) in enumerate(products, start=1):
        category_id = category_map.get(category_slug)
        cursor.execute(
            """
            INSERT INTO products (
                id, product_id, category_id, product_code,
                name, product_name, description,
                cost_price, unit_price, price, price_regular, price_large
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                category_id = VALUES(category_id),
                name = VALUES(name),
                product_name = VALUES(product_name),
                description = VALUES(description),
                cost_price = VALUES(cost_price),
                unit_price = VALUES(unit_price),
                price = VALUES(price),
                price_regular = VALUES(price_regular),
                price_large = VALUES(price_large)
            """,
            (
                idx,
                idx,
                category_id,
                code,
                name,
                name,
                desc,
                cost_price,
                unit_price,
                unit_price,
                unit_price,
                unit_price,
            ),
        )

    # Initialize inventory for all products with default stock levels
    for idx in range(1, len(products) + 1):
        cursor.execute(
            """
            INSERT INTO inventory (id, inventory_id, product_id, current_stock, minimum_stock, reorder_point, quantity)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                current_stock = VALUES(current_stock),
                minimum_stock = VALUES(minimum_stock),
                reorder_point = VALUES(reorder_point),
                quantity = VALUES(quantity)
            """,
            (idx, idx, idx, 100, 10, 20, 100),
        )
    
    # Insert sample customers
    customers = [
        ('John Doe', 'john@example.com', '09123456789', '123 Main St'),
        ('Jane Smith', 'jane@example.com', '09123456790', '456 Oak Ave')
    ]
    
    for name, email, phone, address in customers:
        cursor.execute("""
            INSERT INTO customers (name, email, phone, address)
            VALUES (%s, %s, %s, %s)
        """, (name, email, phone, address))
        
    print("✅ Initial data inserted successfully")

def main():
    """Main function to run database initialization"""
    print("🚀 Starting BigBrew POS Database Initialization...")
    
    if not DB_CONFIG['host']:
        print("❌ Database configuration not found. Please check your .env file.")
        return False
    
    try:
        success = initialize_system_database()
        if success:
            print("\n" + "=" * 60)
            print("🎉 Database initialization completed successfully!")
            print("=" * 60)
            print("Default admin credentials:")
            print("Username: admin")
            print("Email: admin@bigbrew.com")
            print("Password: admin123")
            print("\n⚠️  Please change the admin password after first login!")
            print("=" * 60)
            return True
        else:
            print("\n❌ Database initialization failed!")
            return False
    except Exception as e:
        print(f"\n💥 Unexpected error during initialization: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
