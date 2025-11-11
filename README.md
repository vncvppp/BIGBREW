# BigBrew Coffee Shop POS System

Tkinter-based point of sale application used by BigBrew coffee shops. The system ships with role-aware dashboards (admin, staff, inventory manager, cashier, barista, and customer), OTP-backed account flows, and a MySQL persistence layer.

## Highlights
- Authentication with bcrypt password hashing, account status validation, OTP verification, and password reset flow
- Separate dashboards for staff and customers, including inventory, product, ordering, checkout, and reporting modules
- MySQL-backed repository layer with schema initialization script and seed data helpers
- Configurable through `.env` (database, email/SMTP, and runtime switches) or OS environment variables
- Packaged assets under `resources/` to keep the coffee-themed UI consistent

## Project Layout
- `main.py` – desktop application bootstrapper, handles window routing and DB connection lifecycle
- `app/config/` – environment-driven configuration (`DB_CONFIG`, `APP_CONFIG`, `EMAIL_CONFIG`, OTP/session settings)
- `app/db/` – MySQL connection helpers and schema initializer (`python -m app.db.initialize`)
- `app/repositories/` – database access abstractions for users, customers, orders, and reports
- `app/services/` – shared state management and service utilities (cart, formatting, helpers)
- `app/ui/` – Tkinter windows for login/signup, OTP, dashboards, ordering, checkout, and reports
- `app/utils/` – supporting helpers (email, validation, formatting)
- `resources/` – UI imagery and icon assets
- `tests/` – pytest-based regression tests (currently focused on shared state helpers)

## Prerequisites
- Python 3.8 or newer (3.10+ recommended)
- MySQL Server (local or remote instance accessible from the workstation)
- SMTP-capable email account for OTP delivery (optional for non-email flows)
- Windows PowerShell or macOS/Linux shell for running the provided commands

## Setup

1. **Clone & enter the repository**
   ```powershell
   git clone <repository-url>
   cd BIGBREW-1
   ```

2. **Create and activate a virtual environment (recommended)**
   ```powershell
   python -m venv .venv
   .\\.venv\\Scripts\\Activate.ps1
   ```
   (On macOS/Linux: `source .venv/bin/activate`)

3. **Install dependencies**
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pip install python-dotenv  # required for loading .env files
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root (same folder as `main.py`) and update the values to match your environment:
   ```ini
   # Application
   APP_DEBUG=True
   APP_SECRET_KEY=change-me

   # Database
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your-password
   DB_NAME=bigbrewpos

   # OTP / Session
   OTP_EXPIRY_MINUTES=10
   MAX_LOGIN_ATTEMPTS=3
   SESSION_TIMEOUT_MINUTES=30

   # Email (optional but required for OTP emails)
   EMAIL_ADDRESS=your-email@example.com
   EMAIL_PASSWORD=your-app-password
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

5. **Prepare the database**
   - Ensure your MySQL server is running.
   - Create the database (matching the `DB_NAME` value in `.env`):
     ```sql
     CREATE DATABASE bigbrewpos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     ```
   - Initialize/upgrade the schema and seed data:
     ```powershell
     python -m app.db.initialize
     ```

6. **Run the application**
   ```powershell
   python main.py
   ```

The launcher handles login/signup, customer and staff routes, and gracefully reports configuration or connectivity issues. Debug logging is enabled via `APP_DEBUG=True`.

## Testing
Install development dependencies as needed (pytest is bundled with Python 3.11+, otherwise install manually) and run:
```powershell
pytest
```

## Troubleshooting
- **Cannot connect to MySQL:** Verify the server is reachable and credentials in `.env` match your database. The initializer can create/upgrade the schema if prompted from the app.
- **OTP email not sending:** Ensure SMTP credentials are valid, TLS/ports are correct, and the provider allows SMTP/IMAP (for Gmail use an app password).
- **Missing assets or UI errors:** Confirm the `resources/` folder stays beside `main.py`; PyInstaller bundles use the same structure via `resource_path`.
- **Shared cart issues:** Delete `shared_cart.json` in the project root to reset cached cart state.

## Contributing
Submit issues or pull requests with focused changes (features, bug fixes, or documentation updates). Keep styling consistent and include tests when adding behavior.

Happy brewing ☕