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
        create_inventory_table(cursor)
        create_otp_verification_table(cursor)
        create_products_table(cursor)
        create_sales_table(cursor)
        create_sale_items_table(cursor)
        create_users_table(cursor)
        create_purchases_table(cursor)
        
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
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ Categories table created")

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
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(100) NOT NULL,
        otp VARCHAR(6) NOT NULL,
        purpose VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(create_table_sql)
    print("✅ OTP verification table created")

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

def insert_initial_data(cursor):
    """Insert initial data into the database"""
    print("\n📝 Inserting initial data...")
    
    # Insert categories
    categories = [
        ('Hot Coffee', 'Hot coffee beverages'),
        ('Cold Coffee', 'Cold coffee beverages'),
        ('Tea', 'Tea beverages'),
        ('Pastries', 'Baked goods'),
        ('Snacks', 'Light snacks')
    ]
    
    for name, description in categories:
        cursor.execute("""
            INSERT IGNORE INTO categories (name, description)
            VALUES (%s, %s)
        """, (name, description))

    # Insert default admin user
    admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("""
        INSERT IGNORE INTO users (
            username, email, password, role
        )
        VALUES (%s, %s, %s, %s)
    """, ('admin', 'admin@bigbrew.com', admin_password, 'admin'))

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