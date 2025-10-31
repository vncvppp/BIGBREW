import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import json
try:
    import keyring
    KEYRING_AVAILABLE = True
except Exception:
    KEYRING_AVAILABLE = False
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False
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
        # Remember-me storage
        self.CRED_FILE = Path.home() / '.bigbrew_saved.json'
        self.KEYRING_SERVICE = 'BIGBREW_APP'
        # Local encryption key file for encrypted fallback
        self.CRED_KEY_FILE = Path.home() / '.bigbrew_key'
        self.remember_var = tk.BooleanVar(value=False)
        
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

        # Remember me checkbox
        try:
            self.remember_check = tk.Checkbutton(
                self.parent,
                text="Remember me",
                variable=self.remember_var,
                bg="#3A280F",
                fg="#FFFFFF",
                activebackground="#3A280F",
                activeforeground="#FFFFFF",
                selectcolor="#3A280F",
                cursor="hand2",
                borderwidth=0,
                highlightthickness=0,
                relief="flat"
            )
            # Left-align under the password textbox and align vertically with 'Forgot Password?'
            # 'Forgot Password?' is at y=272.0 in this layout, keep checkbox left-aligned but same line
            self.remember_check.place(x=63.0, y=272.0)
        except Exception:
            pass

        # Clear saved credentials button
        try:
            self.clear_saved_btn = Button(
                text="Clear saved",
                borderwidth=0,
                highlightthickness=0,
                command=self.clear_saved_credentials,
                relief="flat",
                bg="#3A280F",
                fg="#FFFFFF",
                activebackground="#3A280F",
                activeforeground="#FFFFFF",
                cursor="hand2"
            )
            # Place clear saved below the checkbox and left-aligned
            self.clear_saved_btn.place(x=63.0, y=295.0)
        except Exception:
            pass

        # Try to load saved credentials (if any)
        self.load_saved_credentials()

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
            # Save or clear credentials depending on Remember me
            try:
                self.save_credentials(username, password)
            except Exception:
                pass
            # Update last login based on account type
            if user.get('account_type') == 'staff':
                db.update_last_login(user['user_id'])
            elif user.get('account_type') == 'customer':
                db.update_customer_last_login(user['customer_id'])
            
            self.app.show_dashboard(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username/email or password, or account inactive")

    def load_saved_credentials(self):
        """Load saved credentials (if any) from keyring + small file tracking last username"""
        try:
            if self.CRED_FILE.exists():
                data = json.loads(self.CRED_FILE.read_text())
                saved_username = data.get('username')
                if saved_username:
                    saved_password = None
                    if KEYRING_AVAILABLE:
                        try:
                            saved_password = keyring.get_password(self.KEYRING_SERVICE, saved_username)
                        except Exception:
                            saved_password = None
                    # Encrypted-file fallback
                    if not saved_password and data.get('password_enc') and CRYPTO_AVAILABLE:
                        try:
                            # ensure key exists
                            if self.CRED_KEY_FILE.exists():
                                key = self.CRED_KEY_FILE.read_bytes()
                                f = Fernet(key)
                                saved_password = f.decrypt(data.get('password_enc').encode('utf-8')).decode('utf-8')
                        except Exception:
                            saved_password = None
                    # Legacy/plaintext fallback (insecure)
                    if not saved_password and data.get('password'):
                        saved_password = data.get('password')

                if saved_username:
                    # populate fields
                    self.username_entry.delete(0, 'end')
                    self.username_entry.insert(0, saved_username)
                    self.username_entry.config(fg="#000716")
                if saved_password:
                    self.password_entry.delete(0, 'end')
                    self.password_entry.insert(0, saved_password)
                    self.remember_var.set(True)
        except Exception as e:
            print("Error loading saved credentials:", e)

    def save_credentials(self, username, password):
        """Save or clear credentials depending on Remember me checkbox"""
        try:
            if self.remember_var.get():
                if KEYRING_AVAILABLE:
                    try:
                        keyring.set_password(self.KEYRING_SERVICE, username, password)
                        # write last username to file
                        self.CRED_FILE.write_text(json.dumps({'username': username}))
                    except Exception as e:
                        print("Keyring save failed:", e)
                        # fallback to encrypted file if available
                        if CRYPTO_AVAILABLE:
                            try:
                                if not self.CRED_KEY_FILE.exists():
                                    key = Fernet.generate_key()
                                    self.CRED_KEY_FILE.write_bytes(key)
                                else:
                                    key = self.CRED_KEY_FILE.read_bytes()
                                f = Fernet(key)
                                token = f.encrypt(password.encode('utf-8')).decode('utf-8')
                                self.CRED_FILE.write_text(json.dumps({'username': username, 'password_enc': token}))
                            except Exception as ee:
                                print('Encrypted fallback failed:', ee)
                                self.CRED_FILE.write_text(json.dumps({'username': username, 'password': password}))
                        else:
                            # fallback: write username & password (insecure)
                            self.CRED_FILE.write_text(json.dumps({'username': username, 'password': password}))
                else:
                    # No keyring available: try encrypted local file
                    if CRYPTO_AVAILABLE:
                        try:
                            if not self.CRED_KEY_FILE.exists():
                                key = Fernet.generate_key()
                                self.CRED_KEY_FILE.write_bytes(key)
                            else:
                                key = self.CRED_KEY_FILE.read_bytes()
                            f = Fernet(key)
                            token = f.encrypt(password.encode('utf-8')).decode('utf-8')
                            self.CRED_FILE.write_text(json.dumps({'username': username, 'password_enc': token}))
                        except Exception as e:
                            print('Encrypted save failed:', e)
                            # Last-resort plaintext fallback
                            self.CRED_FILE.write_text(json.dumps({'username': username, 'password': password}))
                    else:
                        # No crypto available: store plaintext (insecure)
                        self.CRED_FILE.write_text(json.dumps({'username': username, 'password': password}))
            else:
                # clear saved credentials
                try:
                    if KEYRING_AVAILABLE:
                        try:
                            keyring.delete_password(self.KEYRING_SERVICE, username)
                        except Exception:
                            pass
                finally:
                    if self.CRED_FILE.exists():
                        try:
                            self.CRED_FILE.unlink()
                        except Exception:
                            pass
        except Exception as e:
            print("Error saving credentials:", e)

    def clear_saved_credentials(self):
        """Manual clear of saved credentials and file"""
        try:
            # Try to remove from keyring using username in file
            if self.CRED_FILE.exists():
                try:
                    data = json.loads(self.CRED_FILE.read_text())
                    uname = data.get('username')
                    if uname and KEYRING_AVAILABLE:
                        try:
                            keyring.delete_password(self.KEYRING_SERVICE, uname)
                        except Exception:
                            pass
                except Exception:
                    pass
                try:
                    self.CRED_FILE.unlink()
                except Exception:
                    pass
            # Optionally remove encryption key file (keep for reuse) - we'll keep it to avoid losing access
            # Clear UI fields
            self.username_entry.delete(0, 'end')
            self.username_entry.insert(0, 'Username or Email')
            self.username_entry.config(fg="#666666")
            self.password_entry.delete(0, 'end')
            self.remember_var.set(False)
            messagebox.showinfo('Saved credentials', 'Saved credentials cleared')
        except Exception as e:
            print('Error clearing saved credentials:', e)

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