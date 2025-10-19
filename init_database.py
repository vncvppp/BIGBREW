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
    
    # First create the database
    if not create_database_if_not_exists():
        return False
    
    # Now connect to the specific database
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print(f"✅ Connected to database: {DB_CONFIG['database']}")
        
        # Create all tables in correct order (dependencies first)
        create_users_table(cursor)
        create_categories_table(cursor)
        create_products_table(cursor)
        create_inventory_table(cursor)
        create_customers_table(cursor)
        create_suppliers_table(cursor)
        create_settings_table(cursor)
        create_audit_logs_table(cursor)
        create_otp_verification_table(cursor)
        create_customer_addresses_table(cursor)
        create_sales_table(cursor)
        create_sale_items_table(cursor)
        create_purchases_table(cursor)
        create_purchase_items_table(cursor)
        create_customer_orders_table(cursor)
        create_customer_order_items_table(cursor)
        create_loyalty_rewards_table(cursor)
        
        # Insert initial data
        insert_initial_data(cursor)
        
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

def create_users_table(cursor):
    """Create users table for authentication and user management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        user_type ENUM('admin', 'manager', 'cashier', 'barista', 'inventory_manager') DEFAULT 'cashier',
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
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_username (username),
        INDEX idx_email (email),
        INDEX idx_user_type (user_type),
        INDEX idx_is_active (is_active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Users table created")

def create_categories_table(cursor):
    """Create categories table for product categorization"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS categories (
        category_id INT AUTO_INCREMENT PRIMARY KEY,
        category_name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_category_name (category_name),
        INDEX idx_is_active (is_active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Categories table created")

def create_products_table(cursor):
    """Create products table for product management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS products (
        product_id INT AUTO_INCREMENT PRIMARY KEY,
        product_code VARCHAR(50) UNIQUE NOT NULL,
        product_name VARCHAR(200) NOT NULL,
        description TEXT,
        category_id INT,
        unit_price DECIMAL(10,2) NOT NULL,
        cost_price DECIMAL(10,2) NOT NULL,
        unit VARCHAR(20) DEFAULT 'piece',
        barcode VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
        INDEX idx_product_code (product_code),
        INDEX idx_product_name (product_name),
        INDEX idx_category_id (category_id),
        INDEX idx_is_active (is_active),
        INDEX idx_barcode (barcode)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Products table created")

def create_inventory_table(cursor):
    """Create inventory table for stock management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS inventory (
        inventory_id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        current_stock INT NOT NULL DEFAULT 0,
        minimum_stock INT NOT NULL DEFAULT 0,
        maximum_stock INT NOT NULL DEFAULT 1000,
        reorder_point INT NOT NULL DEFAULT 10,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
        UNIQUE KEY unique_product (product_id),
        INDEX idx_product_id (product_id),
        INDEX idx_current_stock (current_stock),
        INDEX idx_reorder_point (reorder_point)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Inventory table created")

def create_sales_table(cursor):
    """Create sales table for transaction records"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INT AUTO_INCREMENT PRIMARY KEY,
        sale_number VARCHAR(50) UNIQUE NOT NULL,
        customer_id INT NULL,
        user_id INT NOT NULL,
        subtotal DECIMAL(10,2) NOT NULL DEFAULT 0,
        tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
        discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
        total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
        payment_method ENUM('cash', 'card', 'digital_wallet', 'credit') DEFAULT 'cash',
        payment_status ENUM('pending', 'paid', 'refunded', 'cancelled') DEFAULT 'paid',
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT,
        INDEX idx_sale_number (sale_number),
        INDEX idx_customer_id (customer_id),
        INDEX idx_user_id (user_id),
        INDEX idx_sale_date (sale_date),
        INDEX idx_payment_status (payment_status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Sales table created")

def create_sale_items_table(cursor):
    """Create sale_items table for individual sale line items"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sale_items (
        sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
        sale_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        total_price DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
        INDEX idx_sale_id (sale_id),
        INDEX idx_product_id (product_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Sale items table created")

def create_customers_table(cursor):
    """Create customers table for customer management with account functionality"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_code VARCHAR(50) UNIQUE NOT NULL,
        username VARCHAR(50) UNIQUE,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255),
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        middle_name VARCHAR(50) DEFAULT '',
        phone VARCHAR(20),
        address TEXT,
        birth_date DATE,
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
        INDEX idx_email (email),
        INDEX idx_phone (phone),
        INDEX idx_customer_type (customer_type),
        INDEX idx_loyalty_points (loyalty_points),
        INDEX idx_is_active (is_active),
        INDEX idx_is_verified (is_verified)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Customers table created")

def create_suppliers_table(cursor):
    """Create suppliers table for supplier management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id INT AUTO_INCREMENT PRIMARY KEY,
        supplier_code VARCHAR(50) UNIQUE NOT NULL,
        company_name VARCHAR(200) NOT NULL,
        contact_person VARCHAR(100),
        email VARCHAR(100),
        phone VARCHAR(20),
        address TEXT,
        payment_terms VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_supplier_code (supplier_code),
        INDEX idx_company_name (company_name),
        INDEX idx_is_active (is_active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Suppliers table created")

def create_purchases_table(cursor):
    """Create purchases table for purchase order management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS purchases (
        purchase_id INT AUTO_INCREMENT PRIMARY KEY,
        purchase_number VARCHAR(50) UNIQUE NOT NULL,
        supplier_id INT NOT NULL,
        user_id INT NOT NULL,
        subtotal DECIMAL(10,2) NOT NULL DEFAULT 0,
        tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
        total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status ENUM('pending', 'received', 'cancelled') DEFAULT 'pending',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT,
        INDEX idx_purchase_number (purchase_number),
        INDEX idx_supplier_id (supplier_id),
        INDEX idx_user_id (user_id),
        INDEX idx_purchase_date (purchase_date),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Purchases table created")

def create_purchase_items_table(cursor):
    """Create purchase_items table for individual purchase line items"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS purchase_items (
        purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
        purchase_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_cost DECIMAL(10,2) NOT NULL,
        total_cost DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
        INDEX idx_purchase_id (purchase_id),
        INDEX idx_product_id (product_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Purchase items table created")

def create_settings_table(cursor):
    """Create settings table for system configuration"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS settings (
        setting_id INT AUTO_INCREMENT PRIMARY KEY,
        setting_key VARCHAR(100) UNIQUE NOT NULL,
        setting_value TEXT,
        setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_setting_key (setting_key),
        INDEX idx_is_active (is_active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Settings table created")

def create_audit_logs_table(cursor):
    """Create audit_logs table for system activity tracking"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        action VARCHAR(100) NOT NULL,
        table_name VARCHAR(100),
        record_id INT,
        old_values JSON,
        new_values JSON,
        ip_address VARCHAR(45),
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
        INDEX idx_user_id (user_id),
        INDEX idx_action (action),
        INDEX idx_table_name (table_name),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Audit logs table created")

def create_otp_verification_table(cursor):
    """Create otp_verification table for OTP management"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS otp_verification (
        otp_id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(100) NOT NULL,
        otp_code VARCHAR(10) NOT NULL,
        purpose ENUM('signup', 'password_reset', 'email_verification') DEFAULT 'signup',
        expires_at TIMESTAMP NOT NULL,
        is_used BOOLEAN DEFAULT FALSE,
        attempts INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_email (email),
        INDEX idx_otp_code (otp_code),
        INDEX idx_expires_at (expires_at),
        INDEX idx_is_used (is_used)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ OTP verification table created")

def create_customer_orders_table(cursor):
    """Create customer_orders table for customer online orders"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS customer_orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        order_number VARCHAR(50) UNIQUE NOT NULL,
        customer_id INT NOT NULL,
        order_type ENUM('pickup', 'delivery', 'dine_in') DEFAULT 'pickup',
        order_status ENUM('pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled') DEFAULT 'pending',
        subtotal DECIMAL(10,2) NOT NULL DEFAULT 0,
        tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
        delivery_fee DECIMAL(10,2) DEFAULT 0,
        discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
        total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
        payment_method ENUM('cash', 'card', 'digital_wallet', 'loyalty_points') DEFAULT 'cash',
        payment_status ENUM('pending', 'paid', 'refunded', 'cancelled') DEFAULT 'pending',
        special_instructions TEXT,
        estimated_ready_time TIMESTAMP NULL,
        actual_ready_time TIMESTAMP NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
        INDEX idx_order_number (order_number),
        INDEX idx_customer_id (customer_id),
        INDEX idx_order_status (order_status),
        INDEX idx_order_type (order_type),
        INDEX idx_order_date (order_date),
        INDEX idx_payment_status (payment_status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Customer orders table created")

def create_customer_order_items_table(cursor):
    """Create customer_order_items table for individual order line items"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS customer_order_items (
        order_item_id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        total_price DECIMAL(10,2) NOT NULL,
        special_instructions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES customer_orders(order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
        INDEX idx_order_id (order_id),
        INDEX idx_product_id (product_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Customer order items table created")

def create_loyalty_rewards_table(cursor):
    """Create loyalty_rewards table for customer loyalty program"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS loyalty_rewards (
        reward_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        points_earned INT NOT NULL DEFAULT 0,
        points_redeemed INT NOT NULL DEFAULT 0,
        points_balance INT NOT NULL DEFAULT 0,
        transaction_type ENUM('earned', 'redeemed', 'expired', 'bonus') NOT NULL,
        transaction_reference VARCHAR(100),
        description TEXT,
        expiry_date TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
        INDEX idx_customer_id (customer_id),
        INDEX idx_transaction_type (transaction_type),
        INDEX idx_created_at (created_at),
        INDEX idx_expiry_date (expiry_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Loyalty rewards table created")

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
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
        INDEX idx_customer_id (customer_id),
        INDEX idx_address_type (address_type),
        INDEX idx_is_default (is_default),
        INDEX idx_is_active (is_active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Customer addresses table created")

def insert_initial_data(cursor):
    """Insert initial data into the database"""
    print("\n📝 Inserting initial data...")
    
    # Insert default admin user
    admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("""
        INSERT IGNORE INTO users (username, email, password_hash, user_type, first_name, last_name, is_active, is_verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, ('admin', 'admin@bigbrew.com', admin_password, 'admin', 'System', 'Administrator', True, True))
    
    # Insert default categories
    categories = [
        ('Coffee', 'Coffee and coffee-based beverages'),
        ('Tea', 'Tea and tea-based beverages'),
        ('Pastries', 'Baked goods and pastries'),
        ('Sandwiches', 'Sandwiches and wraps'),
        ('Snacks', 'Chips, cookies, and other snacks'),
        ('Beverages', 'Soft drinks, juices, and other beverages'),
        ('Accessories', 'Cups, mugs, and other accessories')
    ]
    
    for category_name, description in categories:
        cursor.execute("""
            INSERT IGNORE INTO categories (category_name, description)
            VALUES (%s, %s)
        """, (category_name, description))
    
    # Insert default products
    products = [
        ('COFFEE-001', 'Espresso', 'Single shot of espresso', 1, 2.50, 0.80, 'shot'),
        ('COFFEE-002', 'Americano', 'Espresso with hot water', 1, 3.00, 1.00, 'cup'),
        ('COFFEE-003', 'Cappuccino', 'Espresso with steamed milk and foam', 1, 4.50, 1.50, 'cup'),
        ('COFFEE-004', 'Latte', 'Espresso with steamed milk', 1, 4.00, 1.30, 'cup'),
        ('COFFEE-005', 'Mocha', 'Espresso with chocolate and steamed milk', 1, 5.00, 1.80, 'cup'),
        ('TEA-001', 'Green Tea', 'Premium green tea', 2, 2.00, 0.50, 'cup'),
        ('TEA-002', 'Black Tea', 'Classic black tea', 2, 2.00, 0.50, 'cup'),
        ('PASTRY-001', 'Croissant', 'Buttery croissant', 3, 3.50, 1.20, 'piece'),
        ('PASTRY-002', 'Muffin', 'Blueberry muffin', 3, 3.00, 1.00, 'piece'),
        ('SANDWICH-001', 'Ham & Cheese', 'Ham and cheese sandwich', 4, 6.50, 2.50, 'piece'),
        ('SANDWICH-002', 'Turkey Club', 'Turkey club sandwich', 4, 7.50, 3.00, 'piece')
    ]
    
    for product_code, product_name, description, category_id, unit_price, cost_price, unit in products:
        cursor.execute("""
            INSERT IGNORE INTO products (product_code, product_name, description, category_id, unit_price, cost_price, unit)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (product_code, product_name, description, category_id, unit_price, cost_price, unit))
    
    # Insert inventory data
    cursor.execute("""
        INSERT IGNORE INTO inventory (product_id, current_stock, minimum_stock, maximum_stock, reorder_point)
        SELECT product_id, 100, 10, 500, 20 FROM products
    """)
    
    # Insert sample customer data
    sample_customers = [
        ('CUST-001', 'john.doe', 'john.doe@email.com', 'John', 'Doe', 'Regular', '09123456789'),
        ('CUST-002', 'jane.smith', 'jane.smith@email.com', 'Jane', 'Smith', 'VIP', '09123456790'),
        ('CUST-003', 'mike.wilson', 'mike.wilson@email.com', 'Mike', 'Wilson', 'Premium', '09123456791')
    ]
    
    for customer_code, username, email, first_name, last_name, customer_type, phone in sample_customers:
        cursor.execute("""
            INSERT IGNORE INTO customers (customer_code, username, email, first_name, last_name, customer_type, phone, is_active, is_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (customer_code, username, email, first_name, last_name, customer_type, phone, True, True))
    
    # Insert default settings
    settings = [
        ('store_name', 'BigBrew Coffee Shop', 'string', 'Name of the coffee shop'),
        ('store_address', '123 Coffee Street, City, State 12345', 'string', 'Store address'),
        ('store_phone', '(555) 123-4567', 'string', 'Store phone number'),
        ('store_email', 'info@bigbrew.com', 'string', 'Store email address'),
        ('tax_rate', '0.08', 'number', 'Sales tax rate (8%)'),
        ('currency_symbol', '$', 'string', 'Currency symbol'),
        ('receipt_footer', 'Thank you for choosing BigBrew!', 'string', 'Receipt footer message'),
        ('low_stock_threshold', '20', 'number', 'Low stock alert threshold'),
        ('auto_backup', 'true', 'boolean', 'Enable automatic database backup'),
        ('backup_frequency', 'daily', 'string', 'Backup frequency (daily, weekly, monthly)'),
        ('loyalty_points_rate', '1', 'number', 'Points earned per peso spent'),
        ('loyalty_points_value', '0.01', 'number', 'Peso value per loyalty point'),
        ('min_points_redemption', '100', 'number', 'Minimum points required for redemption'),
        ('delivery_fee', '50.00', 'number', 'Standard delivery fee'),
        ('free_delivery_threshold', '500.00', 'number', 'Minimum order for free delivery'),
        ('order_prep_time', '15', 'number', 'Average order preparation time in minutes'),
        ('customer_registration_enabled', 'true', 'boolean', 'Allow customer account registration'),
        ('loyalty_program_enabled', 'true', 'boolean', 'Enable loyalty points program'),
        ('online_ordering_enabled', 'true', 'boolean', 'Enable online ordering for customers')
    ]
    
    for setting_key, setting_value, setting_type, description in settings:
        cursor.execute("""
            INSERT IGNORE INTO settings (setting_key, setting_value, setting_type, description)
            VALUES (%s, %s, %s, %s)
        """, (setting_key, setting_value, setting_type, description))
    
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
