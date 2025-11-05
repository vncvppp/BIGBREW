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
        create_suppliers_table(cursor)
        create_purchases_table(cursor)
        create_sales_table(cursor)
        create_sale_items_table(cursor)
        create_users_table(cursor)
        
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
    """Create categories table for product categorization"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
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
        category_id INT,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
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
        product_id INT NOT NULL,
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
        supplier_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_cost DECIMAL(10,2) NOT NULL,
        total_cost DECIMAL(10,2) NOT NULL,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE RESTRICT,
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
        total_amount DECIMAL(10,2) NOT NULL,
        payment_method ENUM('cash', 'card') DEFAULT 'cash',
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
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

def create_suppliers_table(cursor):
    """Create suppliers table"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS suppliers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        contact_person VARCHAR(100),
        email VARCHAR(100),
        phone VARCHAR(20),
        address TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Suppliers table created")

def create_users_table(cursor):
    """Create users table for staff accounts"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        password VARCHAR(255) NOT NULL,
        role ENUM('admin', 'staff') NOT NULL DEFAULT 'staff'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Users table created")
    print("\n📝 Inserting initial data...")
    
    # Insert default admin user
    from hashlib import sha256
    admin_password = sha256("admin123".encode()).hexdigest()
    cursor.execute("""
        INSERT IGNORE INTO users (username, email, password, role)
        VALUES (%s, %s, %s, %s)
    """, ('admin', 'admin@bigbrew.com', admin_password, 'admin'))
    
    # Insert default categories
    categories = [
        ('Coffee', 'Hot and iced coffee beverages'),
        ('Milk Tea', 'Fresh milk tea varieties'),
        ('Fruit Tea', 'Refreshing fruit-based teas'),
        ('Praf', 'Premium beverages'),
        ('Brosty', 'Blended and frozen drinks'),
        ('Add-ons', 'Additional toppings and customizations')
    ]
    
    for name, description in categories:
        cursor.execute("""
            INSERT INTO categories (name, description)
            VALUES (%s, %s)
        """, (name, description))
    
    # Insert default products
    
    # Coffee products
    coffee_products = [
        ('Americano', 'Classic American-style coffee', 1, 99.00),
        ('Spanish Latte', 'Rich Spanish-style latte', 1, 119.00),
        ('Caramel Macchiato', 'Sweet caramel coffee', 1, 129.00),
        ('White Mocha', 'White chocolate mocha', 1, 139.00),
        ('Vanilla Bean', 'Smooth vanilla flavored coffee', 1, 139.00),
        ('Dark Mocha', 'Rich dark chocolate mocha', 1, 139.00),
        ('Salted Caramel', 'Sweet and salty caramel coffee', 1, 139.00),
        ('Vietnamese Latte', 'Traditional Vietnamese coffee', 1, 119.00)
    ]
    
    for name, desc, cat_id, price in coffee_products:
        cursor.execute("""
            INSERT INTO products (name, description, category_id, price)
            VALUES (%s, %s, %s, %s)
        """, (name, desc, cat_id, price))

    # Milk Tea products
    milk_tea_products = [
        ('Okinawa', 'Japanese-inspired milk tea', 2, 110.00),
        ('Winter Melon', 'Refreshing melon milk tea', 2, 110.00),
        ('Hokkaido', 'Rich Japanese-style milk tea', 2, 110.00),
        ('Taro', 'Purple yam flavored milk tea', 2, 110.00),
        ('Thailand', 'Thai-style milk tea', 2, 110.00),
        ('Matcha', 'Green tea milk tea', 2, 110.00),
        ('Cheesecake', 'Creamy cheesecake milk tea', 2, 110.00),
        ('Chocolate', 'Rich chocolate milk tea', 2, 110.00),
        ('Dark Chocolate', 'Premium dark chocolate milk tea', 2, 110.00),
        ('Salted Caramel', 'Sweet and salty caramel milk tea', 2, 110.00)
    ]

    for name, desc, cat_id, price in milk_tea_products:
        cursor.execute("""
            INSERT INTO products (name, description, category_id, price)
            VALUES (%s, %s, %s, %s)
        """, (name, desc, cat_id, price))

    # Initialize inventory for all products
    cursor.execute("""
        INSERT INTO inventory (product_id, quantity)
        SELECT id, 100 FROM products
    """)
    
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
        
    # Insert sample supplier
    cursor.execute("""
        INSERT INTO suppliers (name, contact_person, email, phone, address)
        VALUES ('Coffee Bean Supply Co.', 'James Brown', 'james@supplierco.com', '09876543210', '789 Supply Street')
    """)
    
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
