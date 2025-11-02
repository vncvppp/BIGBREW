# BigBrew Coffee Shop POS System

A comprehensive Tkinter-based Point of Sale (POS) system for BigBrew coffee shop with MySQL database integration, user authentication, OTP verification, and role-based access control.

## 🚀 Features

### Authentication & Security
- **Secure Login System**: Bcrypt password hashing and verification
- **User Registration**: Email-based signup with OTP verification
- **Password Reset**: Forgot password functionality with email verification
- **OTP Verification**: 6-digit OTP system for email verification
- **Role-Based Access**: Support for Admin, Manager, Cashier, Barista, and Inventory Manager roles
- **Account Security**: Active/inactive account status checking

### User Interface
- **Modern Coffee Shop Theme**: Brown and gold color scheme with coffee-themed graphics
- **Responsive Design**: Clean, intuitive interface with proper tab navigation
- **Password Visibility Toggle**: Eye icon to show/hide passwords
- **Back Navigation**: Back buttons on all forms for easy navigation
- **Form Validation**: Real-time validation with user-friendly error messages
- **Keyboard Navigation**: Full keyboard support with Tab and Enter key handling

### Database Integration
- **MySQL Connectivity**: Robust database connection with error handling
- **Customer Management**: Complete customer registration and management system
- **OTP Tracking**: Database-stored OTP verification with expiration
- **Transaction Safety**: Proper database transaction handling

## 📋 Quick Start

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- SMTP email account (for OTP verification)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd BIGBREW-1
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up MySQL database**
```sql
CREATE DATABASE bigbrewpos;
USE bigbrewpos;
```

4. **Initialize database tables**
```bash
python init_database.py
```

5. **Configure email settings** (for OTP verification)
Create a `.env` file in the project root:
```env
# BigBrew — Coffee Shop POS (Tkinter + MySQL)

A lightweight Point of Sale desktop app (Tkinter) used for managing orders, users and OTP-based authentication. This README gives quick setup and run steps for local development on Windows (PowerShell).

## Quick start (Windows PowerShell)

Prerequisites
- Python 3.8+
- MySQL Server
- An SMTP account if you want OTP/email features

Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Database setup

1. Start MySQL server and create a database (example name used below):

```sql
CREATE DATABASE bigbrewpos;
```

2. Update `db_config.py` with your DB credentials and database name.

Initialize tables

```powershell
python init_database.py
```

Configure email (optional)

Create a `.env` file in the project root (used by the OTP/email utilities):

```ini
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASS=your-app-password
SMTP_FROM=your-email@example.com
SMTP_USE_TLS=true
```

Run the app

```powershell
python main.py
```

## Project layout (top-level files)

- `main.py` — application entry
- `login.py`, `signup.py`, `forgotpass.py`, `resetpass.py`, `otp.py` — auth flows
- `admin_dashboard.py`, `home.py`, `order.py`, `menu_items.py`, `menu_coffee.py` — UI screens
- `db_config.py`, `init_database.py`, `init_database_new.py` — DB wiring and init scripts
- `utils.py`, `config.py` — helpers and configuration
- `resources/` — images and UI assets
- `requirements.txt` — Python dependencies

Note: There is a nested copy of the project under `New folder/BIGBREW/`. Use the root folder (`C:\Users\Admin\Desktop\BIGBREW`) when running commands.

## Tips & troubleshooting

- If you see database connection errors, confirm MySQL is running and credentials in `db_config.py` are correct.
- If OTP emails don't send, verify `.env` SMTP credentials and allow less-secure or app passwords as needed (provider dependent).
- For UI issues, ensure the `resources/` subfolders contain the expected image files referenced by the code.

## Development notes

- The app uses parameterized queries to reduce SQL injection risk and bcrypt for password hashing where implemented.
- Main UI is built with Tkinter — standard desktop app behavior applies (no web server required).

## Contributing

Feel free to open issues or PRs. Prefer small, focused changes (one feature or bugfix per PR).

---

Happy brewing ☕

