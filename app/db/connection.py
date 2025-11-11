"""
Database connection utilities.
"""

import logging
import mysql.connector
from mysql.connector import Error

from app.config import DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Wrapper that handles creation of MySQL connections and common helpers.
    """

    def __init__(self):
        self.host = DB_CONFIG["host"]
        self.port = DB_CONFIG["port"]
        self.database = DB_CONFIG["database"]
        self.user = DB_CONFIG["user"]
        self.password = DB_CONFIG["password"]

    def get_connection(self):
        """Create and return a MySQL database connection."""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            if connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                return connection
        except Error as exc:
            logger.error("Error connecting to MySQL: %s", exc)
        return None

    def test_connection(self):
        """Test database connection."""
        connection = self.get_connection()
        if connection:
            connection.close()
            return True
        return False

    def execute_query(self, query, params=None, fetch=False):
        """
        Execute a database query with error handling.

        :param query: SQL statement to execute.
        :param params: Optional query parameters.
        :param fetch: When True, return fetched rows.
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch:
                return cursor.fetchall()

            connection.commit()
            return cursor.rowcount

        except Error as exc:
            logger.error("Database error: %s", exc)
            if connection:
                connection.rollback()
            return None

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def get_user_by_username(self, username):
        """Get user information by username."""
        query = """
        SELECT user_id, username, email, password_hash, user_type,
               first_name, last_name, is_active, last_login
        FROM users
        WHERE username = %s
        """
        result = self.execute_query(query, (username,), fetch=True)
        return result[0] if result else None

    def update_last_login(self, user_id):
        """Update last_login timestamp for user."""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s"
        return self.execute_query(query, (user_id,))

    def update_password_hash(self, user_id, password_hash):
        """Persist a new bcrypt password hash for the given user."""
        query = (
            "UPDATE users SET password_hash = %s, updated_at = CURRENT_TIMESTAMP "
            "WHERE user_id = %s"
        )
        return self.execute_query(query, (password_hash, user_id))

    def get_customer_by_username(self, username):
        """Get customer information by username."""
        query = """
        SELECT customer_id, customer_code, username, email, password_hash, customer_type,
               first_name, last_name, is_active, is_verified, email_verified,
               loyalty_points, total_spent
        FROM customers
        WHERE username = %s
        """
        result = self.execute_query(query, (username,), fetch=True)
        return result[0] if result else None

    def get_customer_by_email(self, email):
        """Get customer information by email."""
        query = """
        SELECT customer_id, customer_code, username, email, password_hash, customer_type,
               first_name, last_name, is_active, is_verified, email_verified,
               loyalty_points, total_spent
        FROM customers
        WHERE email = %s
        """
        result = self.execute_query(query, (email,), fetch=True)
        return result[0] if result else None

    def update_customer_last_login(self, customer_id):
        """Update last_order_date timestamp for customer (using as last login)."""
        query = "UPDATE customers SET last_order_date = CURRENT_TIMESTAMP WHERE customer_id = %s"
        return self.execute_query(query, (customer_id,))

    def update_customer_password_hash(self, customer_id, password_hash):
        """Persist a new bcrypt password hash for the given customer."""
        query = (
            "UPDATE customers SET password_hash = %s, updated_at = CURRENT_TIMESTAMP "
            "WHERE customer_id = %s"
        )
        return self.execute_query(query, (password_hash, customer_id))

    def update_customer_profile(self, customer_id, first_name, last_name, email, phone=None, address=None):
        """Update editable customer profile fields."""
        query = (
            "UPDATE customers SET first_name=%s, last_name=%s, email=%s, phone=%s, address=%s, "
            "updated_at = CURRENT_TIMESTAMP WHERE customer_id=%s"
        )
        return self.execute_query(
            query,
            (first_name or None, last_name or None, email, phone or None, address or None, customer_id),
        )

    def fetch_customer_orders(self, customer_id):
        """Fetch orders for a specific customer."""
        query = """
        SELECT
            s.sale_id,
            s.total_amount,
            s.payment_method,
            s.sale_date,
            s.proof_of_payment_path
        FROM sales s
        WHERE s.customer_id = %s
        ORDER BY s.sale_date DESC
        """
        return self.execute_query(query, (customer_id,), fetch=True)

    def fetch_sale_items(self, sale_id):
        """Fetch sale items for a given sale."""
        query = """
        SELECT
            si.sale_item_id,
            si.quantity,
            si.price,
            p.product_name AS name
        FROM sale_items si
        LEFT JOIN products p ON si.product_id = p.product_id
        WHERE si.sale_id = %s
        ORDER BY si.sale_item_id
        """
        return self.execute_query(query, (sale_id,), fetch=True)


# Global database instance
db = DatabaseConfig()


def get_db_connection():
    """Get database connection using global db instance."""
    return db.get_connection()


