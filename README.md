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
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_USE_TLS=true
```

6. **Run the application**
```bash
python main.py
```

## 🗂️ Project Structure

```
BIGBREW-1/
├── main.py                 # Main application entry point
├── login.py               # Login interface
├── signup.py              # User registration with OTP
├── forgotpass.py          # Password reset request
├── otp.py                 # OTP verification window
├── resetpass.py           # Password reset form
├── admin_dashboard.py    # Admin dashboard
├── home.py               # Home/dashboard interface
├── utils.py              # Utility functions and email service
├── db_config.py          # Database configuration
├── config.py             # Application configuration
├── init_database.py      # Database initialization
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── resources/           # UI assets and images
    ├── login/
    ├── signup/
    ├── forgotpass/
    ├── otp/
    └── resetpass/
```

## 🔐 User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management, system settings |
| **Manager** | Staff management, sales reports, inventory overview |
| **Cashier** | Point of sale, daily sales, customer management |
| **Barista** | Order queue, recipe book, ingredient inventory |
| **Inventory Manager** | Inventory management, stock alerts, supplier management |

## 🛠️ Key Components

### Authentication Flow
1. **Login**: Username/email and password authentication
2. **Signup**: Email registration with OTP verification
3. **Forgot Password**: Email-based password reset with OTP
4. **OTP Verification**: 6-digit code verification system

### Database Schema
- **customers**: Customer information and authentication
- **otp_verification**: OTP codes and verification tracking
- **users**: Staff user accounts (if implemented)

### Security Features
- **Password Hashing**: Bcrypt encryption for all passwords
- **SQL Injection Prevention**: Parameterized queries throughout
- **OTP Expiration**: Time-limited verification codes
- **Account Status**: Active/inactive account management
- **Email Verification**: Required for account activation

## 🎨 UI Features

### Navigation
- **Tab Order**: Proper keyboard navigation between form fields
- **Enter Key**: Quick form submission and field navigation
- **Back Buttons**: Easy navigation back to previous screens
- **Focus Management**: Automatic focus on appropriate fields

### Form Validation
- **Email Validation**: Real-time email format checking
- **Password Strength**: Minimum requirements with complexity rules
- **OTP Validation**: 6-digit numeric input with auto-advance
- **Error Handling**: User-friendly error messages

## 🔧 Configuration

### Database Settings (`db_config.py`)
```python
HOST = "localhost"
PORT = 3306
DATABASE = "bigbrewpos"
USER = "root"
PASSWORD = ""
```

### Email Settings (`.env` file)
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_USE_TLS=true
```

## 🧪 Testing

### Manual Testing
1. **Registration Flow**: Test email signup with OTP verification
2. **Login Flow**: Test authentication with different user types
3. **Password Reset**: Test forgot password functionality
4. **Navigation**: Test all back buttons and form navigation
5. **Validation**: Test form validation and error handling

### Database Testing
```bash
python init_database.py  # Initialize database
python main.py          # Run application
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MySQL server is running
   - Check database credentials in `db_config.py`
   - Verify database exists

2. **Email Not Sending**
   - Check SMTP settings in `.env` file
   - Verify email credentials
   - Check firewall/network settings

3. **OTP Not Working**
   - Check database connection
   - Verify email configuration
   - Check OTP expiration (3 minutes)

4. **UI Issues**
   - Ensure all image files exist in `resources/` folders
   - Check Python version compatibility
   - Verify tkinter installation

## 🚀 Future Enhancements

- [ ] **Dashboard Implementation**: Complete role-specific dashboards
- [ ] **Session Management**: Persistent login sessions
- [ ] **Audit Logging**: User activity tracking
- [ ] **Two-Factor Authentication**: Enhanced security
- [ ] **Remember Me**: Persistent login option
- [ ] **Multi-language Support**: Internationalization
- [ ] **Dark Mode**: Theme switching
- [ ] **Mobile Responsive**: Touch-friendly interface
- [ ] **Offline Mode**: Local data synchronization
- [ ] **Reporting System**: Sales and analytics reports

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For support and questions, please contact the development team or create an issue in the repository.

---

**BigBrew Coffee Shop POS System** - Brewing great coffee, managing great business! ☕
