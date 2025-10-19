import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from tkinter import Canvas, Entry, Button, PhotoImage
import hashlib
import bcrypt
from db_config import db
import sys
import os

OUTPUT_PATH = Path(__file__).parent

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def relative_to_assets(path: str) -> Path:
    """Get path to assets in the login resources folder"""
    possible_paths = [
        resource_path(f"resources/login/{path}"),
        resource_path(f"login/resources/{path}"),
        os.path.join(OUTPUT_PATH, "resources", "login", path),
        os.path.join(OUTPUT_PATH, "login", "resources", path),
        resource_path(path),
    ]
    
    for asset_path in possible_paths:
        if os.path.exists(asset_path):
            return Path(asset_path)
    
    # If no path found, return the most likely one
    return Path(possible_paths[0])

class LoginWindow:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.images = []  # Keep references to images
        
    def load_image(self, path: str):
        """Load image and keep reference to prevent garbage collection"""
        try:
            image_path = relative_to_assets(path)
            if not image_path.exists():
                print(f"Image not found: {image_path}")
                return None
            photo_image = PhotoImage(file=image_path)
            self.images.append(photo_image)
            return photo_image
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None
        
    def setup_ui(self):
        """Setup the login UI"""
        # Clear any existing widgets first
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Create canvas
        self.canvas = Canvas(
            self.parent,
            bg="#FFFFFF",
            height=440,
            width=800,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        # Load background image
        image_image_1 = self.load_image("image_1.png")
        if image_image_1:
            self.canvas.create_image(400.0, 220.0, image=image_image_1)

        # Username/Email entry (Tab Index 1)
        entry_image_username = self.load_image("entry_username.png")
        if entry_image_username:
            self.canvas.create_image(176.5, 188.0, image=entry_image_username)
            
        self.username_entry = Entry(
            bd=0,
            bg="#FFF8E7",
            fg="#000716",
            highlightthickness=0,
            font=("Inter", 12)
        )
        self.username_entry.place(x=62.0, y=168.0, width=229.0, height=38.0)
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        
        # Add placeholder text for username/email field
        self.username_entry.insert(0, "Username or Email")
        self.username_entry.config(fg="#666666")
        self.username_entry.bind('<FocusIn>', self.clear_username_placeholder)
        self.username_entry.bind('<FocusOut>', self.restore_username_placeholder)

        # Password entry (Tab Index 2)
        entry_image_pass = self.load_image("entry_pass.png")
        if entry_image_pass:
            self.canvas.create_image(177.5, 240.0, image=entry_image_pass)
            
        self.password_entry = Entry(
            bd=0,
            bg="#FFF8E7",
            fg="#000716",
            highlightthickness=0,
            show="●",
            font=("Inter", 12)
        )
        self.password_entry.place(x=63.0, y=220.0, width=229.0, height=38.0)
        self.password_entry.bind('<Return>', lambda e: self.handle_login())

        # Login button (Tab Index 3)
        button_image_login = self.load_image("button_login.png")
        if button_image_login:
            self.button_login = Button(
                image=button_image_login,
                borderwidth=0,
                highlightthickness=0,
                command=self.handle_login,
                relief="flat",
                cursor="hand2"
            )
        else:
            self.button_login = Button(
                text="Login",
                borderwidth=0,
                highlightthickness=0,
                command=self.handle_login,
                relief="flat",
                bg="#D2691E",
                fg="#FFFFFF",
                cursor="hand2"
            )
        self.button_login.place(x=54.0, y=323.0, width=245.0, height=42.0)

        # Eye toggle button
        self.show_password = False
        button_image_eye = self.load_image("button_eye.png")
        if button_image_eye:
            self.button_eye = Button(
                image=button_image_eye,
                borderwidth=0,
                highlightthickness=0,
                command=self.toggle_password_visibility,
                relief="flat",
                cursor="hand2"
            )
        else:
            self.button_eye = Button(
                text="👁",
                borderwidth=0,
                highlightthickness=0,
                command=self.toggle_password_visibility,
                relief="flat",
                cursor="hand2"
            )
        self.button_eye.place(x=272.0, y=230.0, width=20.0, height=19.0)

        # Forgot password button
        button_image_forgot = self.load_image("button_forgotpass.png")
        if button_image_forgot:
            Button(
                image=button_image_forgot,
                borderwidth=0,
                highlightthickness=0,
                command=self.on_forgot_password,
                relief="flat",
                cursor="hand2"
            ).place(x=194.0, y=272.0, width=106.0, height=15.0)

        # Signup button
        button_image_signup = self.load_image("button_signup.png")
        if button_image_signup:
            Button(
                image=button_image_signup,
                borderwidth=0,
                highlightthickness=0,
                command=self.on_signup,
                relief="flat",
                cursor="hand2"
            ).place(x=100.0, y=377.0, width=158.0, height=18.0)

        # Set explicit tab order for proper keyboard navigation
        self.username_entry.lift()  # Ensure username entry is on top
        self.password_entry.lift()
        self.button_login.lift()
        
        # Ensure eye button is visible
        self.button_eye.lift()
        
        # Configure tab order explicitly
        self.username_entry.tk_focusNext = lambda: self.password_entry
        self.password_entry.tk_focusNext = lambda: self.button_login
        self.button_login.tk_focusNext = lambda: self.username_entry
        
        # Set focus to username entry
        self.username_entry.focus()

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        self.show_password = not self.show_password
        self.password_entry.config(show="" if self.show_password else "●")

    def clear_username_placeholder(self, event):
        """Clear username placeholder when focused"""
        if self.username_entry.get() == "Username or Email":
            self.username_entry.delete(0, 'end')
            self.username_entry.config(fg="#000716")

    def restore_username_placeholder(self, event):
        """Restore username placeholder when not focused and empty"""
        if self.username_entry.get().strip() == "":
            self.username_entry.insert(0, "Username or Email")
            self.username_entry.config(fg="#666666")

    def on_forgot_password(self):
        """Handle forgot password - redirect to forgot password window"""
        from forgotpass import ForgotPasswordWindow
        self.destroy()
        ForgotPasswordWindow(
            self.parent,
            self.app.show_login,
            self.app.get_db_connection
        )

    def on_signup(self):
        """Navigate to signup"""
        self.app.show_signup()

    def handle_login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        # Remove placeholder text if present
        if username == "Username or Email":
            username = ""

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username/email and password")
            return

        user = self.authenticate_user(username, password)
        if user:
            # Update last login based on account type
            if user.get('account_type') == 'staff':
                db.update_last_login(user['user_id'])
            elif user.get('account_type') == 'customer':
                db.update_customer_last_login(user['customer_id'])
            
            self.app.show_dashboard(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username/email or password, or account inactive")

    def authenticate_user(self, username, password):
        """Authenticate user credentials - checks both users and customers tables"""
        try:
            # First try to authenticate as staff (users table)
            user = self.authenticate_staff(username, password)
            if user:
                return user
            
            # If not found in users table, try customers table
            customer = self.authenticate_customer(username, password)
            if customer:
                return customer
            
            return None
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Unable to connect to database: {str(e)}")
            return None

    def authenticate_staff(self, username, password):
        """Authenticate staff user from users table"""
        try:
            user = db.get_user_by_username(username)
            if not user:
                return None
            if not user['is_active']:
                messagebox.showerror("Account Inactive", "Your staff account has been deactivated")
                return None

            entered_bytes = password.encode('utf-8')
            stored = (user['password_hash'] or '').strip()

            # Determine if the stored hash is bcrypt
            is_bcrypt = stored.startswith("$2a$") or stored.startswith("$2b$") or stored.startswith("$2y$")

            if is_bcrypt:
                try:
                    if bcrypt.checkpw(entered_bytes, stored.encode('utf-8')):
                        # Add user type for staff
                        user['account_type'] = 'staff'
                        return user
                    return None
                except ValueError as e:
                    messagebox.showerror("Database Error", f"Stored password hash is invalid: {str(e)}")
                    return None
            else:
                # Non-bcrypt path: support legacy SHA2(256) hex or plaintext
                sha256_hex = hashlib.sha256(entered_bytes).hexdigest()

                if stored.lower() == sha256_hex.lower() or stored == password:
                    # Auto-upgrade to bcrypt
                    try:
                        new_hash = bcrypt.hashpw(entered_bytes, bcrypt.gensalt()).decode('utf-8')
                        db.update_password_hash(user['user_id'], new_hash)
                    except Exception:
                        pass
                    user['account_type'] = 'staff'
                    return user
                return None
        except Exception as e:
            return None

    def authenticate_customer(self, username, password):
        """Authenticate customer from customers table"""
        try:
            # Try username first, then email
            customer = db.get_customer_by_username(username)
            if not customer:
                # If not found by username, try email
                customer = db.get_customer_by_email(username)
            if not customer:
                return None
            if not customer['is_active']:
                messagebox.showerror("Account Inactive", "Your customer account has been deactivated")
                return None
            if not customer['is_verified']:
                messagebox.showerror("Account Not Verified", "Please verify your email address before logging in")
                return None

            entered_bytes = password.encode('utf-8')
            stored = (customer['password_hash'] or '').strip()

            # Determine if the stored hash is bcrypt
            is_bcrypt = stored.startswith("$2a$") or stored.startswith("$2b$") or stored.startswith("$2y$")

            if is_bcrypt:
                try:
                    if bcrypt.checkpw(entered_bytes, stored.encode('utf-8')):
                        # Add account type for customer
                        customer['account_type'] = 'customer'
                        return customer
                    return None
                except ValueError as e:
                    messagebox.showerror("Database Error", f"Stored password hash is invalid: {str(e)}")
                    return None
            else:
                # Non-bcrypt path: support legacy SHA2(256) hex or plaintext
                sha256_hex = hashlib.sha256(entered_bytes).hexdigest()

                if stored.lower() == sha256_hex.lower() or stored == password:
                    # Auto-upgrade to bcrypt
                    try:
                        new_hash = bcrypt.hashpw(entered_bytes, bcrypt.gensalt()).decode('utf-8')
                        db.update_customer_password_hash(customer['customer_id'], new_hash)
                    except Exception:
                        pass
                    customer['account_type'] = 'customer'
                    return customer
                return None
        except Exception as e:
            return None

    def run(self):
        """Run the login module"""
        if not db.test_connection():
            messagebox.showerror("Database Error", "Unable to connect to database. Please check your MySQL server.")
            return
        self.setup_ui()

    def destroy(self):
        """Clean up the window"""
        for widget in self.parent.winfo_children():
            widget.destroy()