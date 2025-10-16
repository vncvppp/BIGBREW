# BigBrew Coffee Shop Management System

A comprehensive Tkinter-based POS system for BigBrew coffee shop with MySQL database integration, user authentication, and role-based access control.

## Features

- **Seamless Navigation**: Integrated main.py for smooth switching between login and signup
- **Secure Authentication**: Bcrypt password hashing and verification
- **Email Verification**: OTP-based email verification for new user registration
- **Role-Based Access**: Support for Admin, Manager, Cashier, Barista, and Inventory Manager roles
- **Modern UI**: Coffee shop themed interface with brown and gold color scheme
- **Database Integration**: MySQL database connectivity with error handling
- **Password Visibility Toggle**: Eye icon to show/hide password
- **Role-Specific Dashboards**: Different dashboard interfaces for each user type

## Quick Start

### Main Application (Recommended)
Run the integrated application with seamless navigation:
```bash
python main.py
```

### Individual Modules
You can still run modules individually:
```bash
python login.py    # Login interface only
python signup.py   # Signup interface only
```

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up email configuration (for signup verification):
Create a `.env` file in the project root:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_USE_TLS=true
```

3. Ensure MySQL server is running and create the `bigbrewpos` database:
```sql
CREATE DATABASE bigbrewpos;
USE bigbrewpos;

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

4. Create a test admin user:
```python
import bcrypt

# Hash a password
password = "admin123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Insert into database
INSERT INTO users (username, email, password_hash, user_type, first_name, last_name) 
VALUES ('admin', 'admin@bigbrew.com', 'hashed_password_here', 'admin', 'Admin', 'User');
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

- `main.py` - Main application entry point with seamless navigation
- `login.py` - LoginWindow class for authentication interface
- `signup.py` - SignupWindow class for user registration with email verification
- `dashboard.py` - Role-specific dashboard implementations
- `db_config.py` - Database configuration and connection management
- `requirements.txt` - Python dependencies
- `test_integration.py` - Integration test script
- `resources/` - UI assets and images

## Error Handling

The system includes comprehensive error handling for:
- Database connection failures
- Invalid credentials
- Inactive accounts
- Role mismatches
- Network connectivity issues

## Navigation Features

The main.py application provides seamless navigation between modules:

- **Centralized Management**: Single entry point for the entire application
- **Smooth Transitions**: No window flickering when switching between login and signup
- **Backward Compatibility**: Individual modules can still be run standalone
- **Error Handling**: Graceful handling of module switching errors
- **Resource Management**: Proper cleanup of windows and resources

## Testing

Run the integration test to verify everything works correctly:
```bash
python test_integration.py
```

## Future Enhancements

- Password reset functionality
- Session management
- Audit logging
- Two-factor authentication
- Remember me functionality
- Multi-language support
- Dark mode theme
