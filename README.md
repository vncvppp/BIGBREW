# BigBrew Coffee Shop Management System - Login Module

A Tkinter-based login system for the BigBrew coffee shop management system with MySQL database integration and role-based authentication.

## Features

- **Secure Authentication**: Bcrypt password hashing and verification
- **Role-Based Access**: Support for Admin, Manager, Cashier, Barista, and Inventory Manager roles
- **Modern UI**: Coffee shop themed interface with brown and gold color scheme
- **Database Integration**: MySQL database connectivity with error handling
- **Password Visibility Toggle**: Eye icon to show/hide password
- **Role-Specific Dashboards**: Different dashboard interfaces for each user type

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure MySQL server is running and create the `bigbrew` database with the users table:
```sql
CREATE DATABASE bigbrew;
USE bigbrew;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('admin', 'manager', 'cashier', 'barista', 'inventory_manager') DEFAULT 'cashier',
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    contact_number VARCHAR(20),
    address TEXT,
    hire_date DATE,
    salary DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

3. Create a test user with hashed password:
```python
import bcrypt

# Hash a password
password = "admin123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Insert into database
INSERT INTO users (username, email, password_hash, user_type, first_name, last_name) 
VALUES ('admin', 'admin@bigbrew.com', 'hashed_password_here', 'admin', 'Admin', 'User');
```

## Usage

Run the login module:
```bash
python login.py
```

## Database Configuration

The system connects to MySQL with the following default settings:
- Host: localhost
- Port: 3306
- Database: bigbrew
- User: root
- Password: (empty)

To modify these settings, edit the `DatabaseConfig` class in `db_config.py`.

## User Roles

- **Admin**: Full system access, user management, system settings
- **Manager**: Staff management, sales reports, inventory overview, scheduling
- **Cashier**: Point of sale, daily sales, customer management, receipts
- **Barista**: Order queue, recipe book, ingredient inventory, time tracking
- **Inventory Manager**: Inventory management, stock alerts, supplier management, purchase orders

## Security Features

- Passwords are hashed using bcrypt
- SQL injection prevention with parameterized queries
- Account status checking (active/inactive)
- Role-based access control
- Secure database connection handling

## File Structure

- `login.py` - Main login interface and authentication logic
- `dashboard.py` - Role-specific dashboard implementations
- `db_config.py` - Database configuration and connection management
- `requirements.txt` - Python dependencies

## Error Handling

The system includes comprehensive error handling for:
- Database connection failures
- Invalid credentials
- Inactive accounts
- Role mismatches
- Network connectivity issues

## Future Enhancements

- Password reset functionality
- Session management
- Audit logging
- Two-factor authentication
- Remember me functionality
