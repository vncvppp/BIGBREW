#!/usr/bin/env python3
"""Initialize product data for BigBrew POS"""

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def init_products():
    """Initialize products and categories"""
    try:
        # Connect to database
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Read and execute the SQL file
        with open('db_init_products.sql', 'r') as file:
            sql_commands = file.read()
            
            # Split into individual commands and execute
            for command in sql_commands.split(';'):
                if command.strip():
                    cursor.execute(command)
        
        # Commit the changes
        connection.commit()
        print("✅ Products initialized successfully")
        
    except Error as e:
        print(f"❌ Error: {e}")
        if connection.is_connected():
            connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    init_products()