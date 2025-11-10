"""
Repository helpers for product data access.
"""

from typing import List, Optional

import mysql.connector
from mysql.connector import Error

from app.db.connection import get_db_connection


class ProductRepository:
    @staticmethod
    def get_all_products() -> List[dict]:
        """Get all products from the database."""
        products = []
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            query = """
            SELECT
                p.product_id,
                p.category_id,
                p.product_code,
                p.product_name,
                p.product_name AS name,
                p.description,
                p.price,
                p.price_regular,
                p.price_large,
                p.image_path,
                p.image_blob,
                c.name AS category_name,
                c.category_name AS categories_category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            """
            cursor.execute(query)
            products = cursor.fetchall()

        except Error as exc:
            print(f"Error: {exc}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

        return products

    @staticmethod
    def get_products_by_category(category_id: int) -> List[dict]:
        """Get products by category ID."""
        products = []
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            query = """
            SELECT
                p.product_id,
                p.category_id,
                p.product_code,
                p.product_name,
                p.product_name AS name,
                p.description,
                p.price,
                p.price_regular,
                p.price_large,
                p.image_path,
                p.image_blob,
                c.name AS category_name,
                c.category_name AS categories_category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.category_id = %s
            """
            cursor.execute(query, (category_id,))
            products = cursor.fetchall()

        except Error as exc:
            print(f"Error: {exc}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

        return products

    @staticmethod
    def add_product(
        category_id: Optional[int],
        name: str,
        description: str,
        price_regular: float,
        price_large: float,
        image_path: Optional[str] = None,
        image_blob: Optional[bytes] = None,
        product_code: Optional[str] = None,
    ) -> Optional[int]:
        """Add a new product.

        Returns the new product_id on success, otherwise None.
        """
        new_id: Optional[int] = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            query = """
            INSERT INTO products (
                category_id,
                product_name,
                description,
                price,
                price_regular,
                price_large,
                image_path,
                image_blob,
                product_code
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                image_blob,
                    product_code,
                ),
            )
            connection.commit()

            new_id = cursor.lastrowid

        except Error as exc:
            print(f"Error: {exc}")
            new_id = None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

        return new_id

    @staticmethod
    def update_product(
        product_id: int,
        category_id: Optional[int] = None,
        name: Optional[str] = None,
        product_name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        price_regular: Optional[float] = None,
        price_large: Optional[float] = None,
        image_path: Optional[str] = None,
        product_code: Optional[str] = None,
        image_blob: Optional[bytes] = None,
    ) -> bool:
        """Update an existing product."""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Build update query dynamically based on provided fields
            update_fields = []
            params = []

            if category_id is not None:
                update_fields.append("category_id = %s")
                params.append(category_id)
            effective_name = product_name if product_name is not None else name
            if effective_name is not None:
                update_fields.append("product_name = %s")
                params.append(effective_name)
            if product_code is not None:
                update_fields.append("product_code = %s")
                params.append(product_code)
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
            if image_blob is not None:
                update_fields.append("image_blob = %s")
                params.append(image_blob)

            if not update_fields:
                return False

            query = f"""
            UPDATE products
            SET {", ".join(update_fields)}
            WHERE product_id = %s
            """
            params.append(product_id)

            cursor.execute(query, tuple(params))
            connection.commit()

            success = cursor.rowcount > 0

        except Error as exc:
            print(f"Error: {exc}")
            success = False
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

        return success

    @staticmethod
    def delete_product(product_id: int) -> bool:
        """Delete a product."""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            query = "DELETE FROM products WHERE product_id = %s"
            cursor.execute(query, (product_id,))
            connection.commit()

            success = cursor.rowcount > 0

        except Error as exc:
            print(f"Error: {exc}")
            success = False
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

        return success

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[dict]:
        """Get a product by ID."""
        product = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            query = """
            SELECT
                p.product_id,
                p.category_id,
                p.product_code,
                p.product_name,
                p.product_name AS name,
                p.description,
                p.price,
                p.price_regular,
                p.price_large,
                p.image_path,
                p.image_blob,
                c.name AS category_name,
                c.category_name AS categories_category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.product_id = %s
            """
            cursor.execute(query, (product_id,))
            product = cursor.fetchone()

        except Error as exc:
            print(f"Error: {exc}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

        return product


