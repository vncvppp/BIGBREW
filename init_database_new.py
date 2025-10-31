#!/usr/bin/env python3
"""
BigBrew POS System - Database Initialization Script
Creates all necessary tables and initial data for the BigBrew POS system
"""

import mysql.connector
from mysql.connector import Error
import bcrypt
import os
import sys
from pathlib import Path
from datetime import datetime, date
from config import DB_CONFIG, APP_CONFIG

def get_database_connection():
    """Get database connection without specifying database name"""
    try:
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
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{DB_CONFIG['database']}' created/verified successfully")
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
    
    if not create_database_if_not_exists():
        return False
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print(f"✅ Connected to database: {DB_CONFIG['database']}")
        
        # Create all tables in correct order (dependencies first)
        create_categories_table(cursor)
        create_customers_table(cursor)
        create_customer_addresses_table(cursor)
        create_customer_orders_table(cursor)
        create_inventory_table(cursor)
        create_loyalty_rewards_table(cursor)
        create_otp_verification_table(cursor)
        create_products_table(cursor)
        create_purchases_table(cursor)
        create_purchase_items_table(cursor)
        create_sales_table(cursor)
        create_sale_items_table(cursor)
        create_settings_table(cursor)
        create_suppliers_table(cursor)
        create_users_table(cursor)
        
        # Insert initial data
        insert_initial_data(cursor)
        
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
        category_id INT AUTO_INCREMENT PRIMARY KEY,
        category_name ENUM('milkTea', 'coffee', 'fruitTea', 'praf', 'brosty', 'add-ons') NOT NULL,
        description TEXT,
        is_available BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_category_name (category_name),
        INDEX idx_is_available (is_available)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Categories table created")

def create_customers_table(cursor):
    """Create customers table for customer management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_code VARCHAR(50) UNIQUE NOT NULL,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        middle_name VARCHAR(50) DEFAULT '',
        phone VARCHAR(20),
        address TEXT,
        birthdate DATE,
        customer_type ENUM('regular', 'vip', 'wholesale', 'premium') DEFAULT 'regular',
        loyalty_points INT DEFAULT 0,
        total_spent DECIMAL(10,2) DEFAULT 0,
        last_order_date TIMESTAMP NULL,
        is_active BOOLEAN DEFAULT TRUE,
        is_verified BOOLEAN DEFAULT FALSE,
        email_verified BOOLEAN DEFAULT FALSE,
        phone_verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_customer_code (customer_code),
        INDEX idx_username (username),
        INDEX idx_email (email)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Customers table created")

def create_customer_addresses_table(cursor):
    """Create customer_addresses table for multiple delivery addresses"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS customer_addresses (
        address_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        address_type ENUM('home', 'work', 'other') DEFAULT 'home',
        address_line1 VARCHAR(200) NOT NULL,
        address_line2 VARCHAR(200),
        city VARCHAR(100) NOT NULL,
        state VARCHAR(100) NOT NULL,
        postal_code VARCHAR(20) NOT NULL,
        country VARCHAR(100) DEFAULT 'Philippines',
        is_default BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Customer addresses table created")

def create_customer_orders_table(cursor):
    """Create customer_orders table for online orders"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS customer_orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        order_number VARCHAR(50) UNIQUE NOT NULL,
        customer_id INT NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Customer orders table created")

def create_inventory_table(cursor):
    """Create inventory table for stock management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS inventory (
        inventory_id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        current_stock INT NOT NULL DEFAULT 0,
        minimum_stock INT NOT NULL DEFAULT 0,
        reorder_point INT NOT NULL DEFAULT 10,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Inventory table created")

def create_loyalty_rewards_table(cursor):
    """Create loyalty_rewards table for customer rewards"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS loyalty_rewards (
        reward_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        points INT NOT NULL DEFAULT 0,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Loyalty rewards table created")

def create_otp_verification_table(cursor):
    """Create otp_verification table for OTP management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS otp_verification (
        otp_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        otp_code VARCHAR(6) NOT NULL,
        expiry_time TIMESTAMP NOT NULL,
        is_used BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ OTP verification table created")

def create_products_table(cursor):
    """Create products table for product management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS products (
        product_id INT AUTO_INCREMENT PRIMARY KEY,
        product_code VARCHAR(50) UNIQUE NOT NULL,
        product_name VARCHAR(100) NOT NULL,
        description TEXT,
        category_id INT,
        cost_price DECIMAL(10,2) NOT NULL,
        unit VARCHAR(20) DEFAULT 'piece',
        barcode VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Products table created")

def create_purchases_table(cursor):
    """Create purchases table for inventory purchases"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS purchases (
        purchase_id INT AUTO_INCREMENT PRIMARY KEY,
        supplier_id INT NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        purchase_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Purchases table created")

def create_purchase_items_table(cursor):
    """Create purchase_items table for purchase line items"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS purchase_items (
        item_id INT AUTO_INCREMENT PRIMARY KEY,
        purchase_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Purchase items table created")

def create_sales_table(cursor):
    """Create sales table for transactions"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        total_amount DECIMAL(10,2) NOT NULL,
        sale_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Sales table created")

def create_sale_items_table(cursor):
    """Create sale_items table for sale line items"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sale_items (
        item_id INT AUTO_INCREMENT PRIMARY KEY,
        sale_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Sale items table created")

def create_settings_table(cursor):
    """Create settings table for system configuration"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS settings (
        setting_id INT AUTO_INCREMENT PRIMARY KEY,
        setting_key ENUM(
            'store_name',
            'store_address',
            'store_phone',
            'store_email',
            'tax_rate',
            'currency_symbol',
            'receipt_footer',
            'low_stock_threshold',
            'auto_backup',
            'backup_frequency',
            'loyalty_points_rate',
            'loyalty_points_value',
            'min_points_value',
            'delivery_fee',
            'free_delivery_threshold',
            'order_prep_time',
            'customer_registration_enable',
            'loyalty_program_enable',
            'online_ordering_enable'
        ) NOT NULL,
        setting_value TEXT NOT NULL,
        setting_type ENUM('string', 'number', 'boolean', 'json') NOT NULL,
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Settings table created")

def create_suppliers_table(cursor):
    """Create suppliers table"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        contact_person VARCHAR(100),
        email VARCHAR(100),
        phone VARCHAR(20),
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Suppliers table created")

def create_users_table(cursor):
    """Create users table for staff accounts"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        user_type ENUM('admin', 'staff') NOT NULL DEFAULT 'staff',
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        middle_name VARCHAR(50) DEFAULT '',
        contact_number VARCHAR(20),
        address TEXT,
        hire_date DATE,
        salary DECIMAL(10,2),
        is_active BOOLEAN DEFAULT TRUE,
        is_verified BOOLEAN DEFAULT FALSE,
        last_login TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Users table created")

def insert_initial_data(cursor):
    """Insert initial data into the database"""
    print("\n📝 Inserting initial data...")
    
    # Insert categories
    categories = [
        ('milkTea', 'Milk tea beverages'),
        ('coffee', 'Coffee beverages'),
        ('fruitTea', 'Fruit tea beverages'),
        ('praf', 'PRAF beverages'),
        ('brosty', 'Brosty beverages'),
        ('add-ons', 'Additional toppings and add-ons')
    ]
    
    for category_name, description in categories:
        cursor.execute("""
            INSERT IGNORE INTO categories (category_name, description)
            VALUES (%s, %s)
        """, (category_name, description))

    # Insert default admin user
    admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("""
        INSERT IGNORE INTO users (
            username, email, password_hash, user_type, first_name, last_name,
            is_active, is_verified
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, ('admin', 'admin@bigbrew.com', admin_password, 'admin', 'System', 
          'Administrator', True, True))

    print("✅ Initial data inserted successfully")

def main():
    """Main function to run database initialization"""
    print("🚀 Starting BigBrew POS Database Initialization...")
    
    if not DB_CONFIG['host']:
        print("❌ Database configuration not found. Please check your config.py file.")
        return False
    
    try:
        success = initialize_system_database()
        if success:
            print("\n" + "=" * 60)
            print("🎉 Database initialization completed successfully!")
            print("=" * 60)
            print("Default admin credentials:")
            print("Username: admin")
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