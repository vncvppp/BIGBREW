from typing import List, Optional
import mysql.connector
from mysql.connector import Error
from db_config import get_db_connection

class ProductRepository:
    @staticmethod
    def get_all_products() -> List[dict]:
        """Get all products from the database"""
        products = []
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT p.*, c.name as category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            """
            cursor.execute(query)
            products = cursor.fetchall()
            
        except Error as e:
            print(f"Error: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
        return products

    @staticmethod
    def get_products_by_category(category_id: int) -> List[dict]:
        """Get products by category ID"""
        products = []
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = %s
            """
            cursor.execute(query, (category_id,))
            products = cursor.fetchall()
            
        except Error as e:
            print(f"Error: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
        return products

    @staticmethod
    def add_product(category_id: int, name: str, description: str,
                   price_regular: float, price_large: float,
                   image_path: Optional[str] = None) -> bool:
        """Add a new product"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            query = """
            INSERT INTO products (category_id, name, description, price, price_regular, price_large, image_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    category_id,
                    name,
                    description,
                    price_regular,
                    price_regular,
                    price_large,
                    image_path,
                )
            )
            connection.commit()
            
            success = True
            
        except Error as e:
            print(f"Error: {e}")
            success = False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
        return success

    @staticmethod
    def update_product(product_id: int, category_id: Optional[int] = None, 
                      name: Optional[str] = None, description: Optional[str] = None,
                      price: Optional[float] = None, price_regular: Optional[float] = None,
                      price_large: Optional[float] = None,
                      image_path: Optional[str] = None) -> bool:
        """Update an existing product"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Build update query dynamically based on provided fields
            update_fields = []
            params = []
            
            if category_id is not None:
                update_fields.append("category_id = %s")
                params.append(category_id)
            if name is not None:
                update_fields.append("name = %s")
                params.append(name)
            if description is not None:
                update_fields.append("description = %s")
                params.append(description)
            if price is not None:
                update_fields.append("price = %s")
                params.append(price)
            if price_regular is not None:
                update_fields.append("price_regular = %s")
                params.append(price_regular)
                if price is None:
                    update_fields.append("price = %s")
                    params.append(price_regular)
            if price_large is not None:
                update_fields.append("price_large = %s")
                params.append(price_large)
            if image_path is not None:
                update_fields.append("image_path = %s")
                params.append(image_path)
                
            if not update_fields:
                return False
                
            query = f"""
            UPDATE products 
            SET {", ".join(update_fields)}
            WHERE id = %s
            """
            params.append(product_id)
            
            cursor.execute(query, tuple(params))
            connection.commit()
            
            success = cursor.rowcount > 0
            
        except Error as e:
            print(f"Error: {e}")
            success = False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
        return success

    @staticmethod
    def delete_product(product_id: int) -> bool:
        """Delete a product"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            query = "DELETE FROM products WHERE id = %s"
            cursor.execute(query, (product_id,))
            connection.commit()
            
            success = cursor.rowcount > 0
            
        except Error as e:
            print(f"Error: {e}")
            success = False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
        return success

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[dict]:
        """Get a product by ID"""
        product = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
            """
            cursor.execute(query, (product_id,))
            product = cursor.fetchone()
            
        except Error as e:
            print(f"Error: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
        return product