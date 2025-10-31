#!/usr/bin/env python3
"""
BigBrew POS System - Main Entry Point
Provides seamless navigation between login and signup modules
"""

import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from login import LoginWindow
from signup import SignupWindow
from forgotpass import ForgotPasswordWindow
from resetpass import PasswordResetWindow
from config import DB_CONFIG, APP_CONFIG
import os, sys
import time
from pathlib import Path

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def relative_to_assets(path: str) -> Path:
    return Path(resource_path(f"resources/login/{path}"))

class BigBrewApp:
    """Main application class that manages navigation between modules"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BigBrew POS System")
        self.root.configure(bg='#f0f0f0')

        # Set application icon if exists
        try:
            icon_path = relative_to_assets("PDMICON.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
            else:
                if APP_CONFIG['debug']:
                    print(f"⚠️ Icon not found: {icon_path}")
        except Exception as e:
            if APP_CONFIG['debug']:
                print(f"⚠️ Icon loading failed: {e}")

        # Set initial window size for login
        self.login_size = (800, 440)
        self.home_size = (1270, 790)
        self.current_size = self.login_size

        self.center_window(*self.login_size)
        self.root.resizable(False, False)

        self.current_user = None
        self.user_type = None
        self.db_connection = None

        # Check if database configuration is available
        if not DB_CONFIG['host']:
            messagebox.showerror(
                "Configuration Error",
                "Database configuration not found. Please check your .env file."
            )
            self.root.quit()
            return

        self.setup_database()
        self.show_login()
        
    def center_window(self, width, height):
        """Center the window on the screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.current_size = (width, height)

    def resize_window(self, width, height):
        """Resize the window to new dimensions"""
        print(f"Resizing window to: {width}x{height}")  # Debug
        self.center_window(width, height)

    def setup_database(self):
        """Initialize database connection"""
        try:
            self.db_connection = mysql.connector.connect(**DB_CONFIG)
            if self.db_connection.is_connected():
                print("✓ Database connection established successfully")

                # Test if database exists
                try:
                    cursor = self.db_connection.cursor()
                    cursor.execute("USE {}".format(DB_CONFIG['database']))
                    cursor.close()
                except Error as e:
                    if e.errno == 1049:  # Database doesn't exist
                        response = messagebox.askyesno(
                            "Database Setup",
                            "Database not found. Would you like to initialize the database now?"
                        )
                        if response:
                            self.initialize_database()
                        else:
                            messagebox.showinfo(
                                "Information",
                                "Please run init_database.py manually to set up the database."
                            )
                            self.root.quit()
                    else:
                        raise e

        except Error as e:
            error_msg = f"Failed to connect to database: {str(e)}"
            if APP_CONFIG['debug']:
                error_msg += f"\n\nDebug info: {e}"

            messagebox.showerror("Database Error", error_msg)
            self.root.quit()

    def initialize_database(self):
        """Initialize the database schema"""
        try:
            from init_database import initialize_system_database
            if initialize_system_database():
                messagebox.showinfo("Success", "Database initialized successfully!")
                # Reconnect to the new database
                if self.db_connection and self.db_connection.is_connected():
                    self.db_connection.close()
                self.db_connection = mysql.connector.connect(**DB_CONFIG)
            else:
                messagebox.showerror("Error", "Failed to initialize database.")
                self.root.quit()
        except ImportError as e:
            messagebox.showerror("Error", f"Cannot import database initializer: {e}")
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Database initialization failed: {e}")
            self.root.quit()

    def get_db_connection(self):
        """Get database connection with reconnection handling"""
        try:
            if self.db_connection is None or not self.db_connection.is_connected():
                self.db_connection = mysql.connector.connect(**DB_CONFIG)
                # Set autocommit to True to avoid transaction conflicts
                self.db_connection.autocommit = True
            return self.db_connection
        except Error as e:
            error_msg = f"Database connection failed: {str(e)}"
            if APP_CONFIG['debug']:
                error_msg += f"\n\nDebug info: {e}"

            messagebox.showerror("Database Error", error_msg)
            return None

    def start(self):
        """Start the application with login screen"""
        try:
            # Test database connection first
            if not self.get_db_connection():
                messagebox.showerror(
                    "Database Error", 
                    "Unable to connect to database. Please check your MySQL server."
                )
                return
            
            # Start with login screen
            self.show_login()
            
        except Exception as e:
            messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")
    
    def show_login(self):
        """Show login window and resize to login size"""
        print("Showing login window...")  # Debug
        self.clear_window()

        # First ensure window is in normal mode (not maximized/minimized)
        self.root.state('normal')  # Ensure window is in normal state

        # Ensure window is not in fullscreen
        self.root.attributes('-fullscreen', False)

        # Now resize the window to login size
        self.root.geometry("800x440")
        self.center_window(800, 440)
        self.root.minsize(800, 440)
        self.root.resizable(False, False)  # Allow resizing

        # Give time for window to resize and update
        self.root.update_idletasks()
        self.root.update()

        # Create login window
        self.current_module = LoginWindow(self.root, self)
        self.current_module.run()

    def show_signup(self):
        """Show signup window (same size as login)"""
        self.clear_window()
        self.resize_window(*self.login_size)
        self.current_module = SignupWindow(self.root, self.show_login, self.get_db_connection)
        self.current_module.setup_ui()

    def show_forgot_password(self):
        """Show forgot password flow (same size as login)"""
        self.clear_window()
        self.resize_window(*self.login_size)
        ForgotPasswordWindow(self.root, self.show_login, self.get_db_connection)

    def show_reset_password(self, user_email):
        """Show password reset window"""
        self.clear_window()
        self.resize_window(*self.login_size)
        PasswordResetWindow(self.root, user_email, self.show_login, self.get_db_connection)

    def show_dashboard(self, user_data):
        """Show appropriate dashboard based on account type"""
        try:
            # Check if this is a customer account
            if user_data.get('account_type') == 'customer':
                self.show_customer_home(user_data)
            else:
                # Staff account - show admin dashboard
                from admin_dashboard import DashboardFactory
                self.cleanup_current_module()
                dashboard = DashboardFactory(user_data, self)
                dashboard.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Dashboard: {str(e)}")

    def show_customer_home(self, customer_data):
        """Show customer home page"""
        print("Showing customer home...")  # Debug
        self.clear_window()

        # Resize window for customer home
        self.root.geometry("1035x534")
        self.center_window(1035, 534)
        self.root.minsize(1035, 534)
        self.root.resizable(False, False)

        # Give time for window to resize
        self.root.update_idletasks()
        self.root.update()

        # Create customer home
        try:
            from home import CustomerHome
            self.current_module = CustomerHome(self.root, customer_data, self)
        except ImportError as e:
            messagebox.showerror("Error", f"Customer home module not available: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Customer Home: {str(e)}")

    def login_success_callback(self, user_data, user_type):
        """Callback after successful login - redirect based on user type"""
        self.current_user = user_data
        self.user_type = user_type

        # Log login activity
        if APP_CONFIG['debug']:
            print(f"✓ User logged in: {user_data['email']} ({user_type})")

        # Redirect based on user type
        if user_type == 'admin':
            self.show_admin_dashboard()
        else:
            self.show_dashboard(user_data)

    def show_admin_dashboard(self):
        """Show admin dashboard"""
        print("Showing admin dashboard...")  # Debug
        self.clear_window()

        # Resize window for admin dashboard
        self.root.geometry("1270x790")
        self.center_window(1270, 790)
        self.root.minsize(1270, 790)
        self.root.resizable(False, False)

        # Give time for window to resize
        self.root.update_idletasks()
        self.root.update()

        # Create admin dashboard
        try:
            from admin_dashboard import AdminDashboard
            dashboard = AdminDashboard(self.current_user, self)
            dashboard.show()
        except ImportError:
            messagebox.showinfo("Info", "Admin dashboard module not available")
            self.show_dashboard(self.current_user)

    def logout(self):
        """Logout user and return to login - resize to login size"""
        print("Logging out user...")  # Debug
        if self.current_user and APP_CONFIG['debug']:
            print(f"✓ User logged out: {self.current_user['email']}")

        self.current_user = None
        self.user_type = None

        # Clear any pending operations
        self.root.after_cancel('all')

        self.root.state('normal')
        self.root.attributes('-fullscreen', False)

        # Force window update
        self.root.update_idletasks()

        # Show login screen
        self.show_login()

    def cleanup_current_module(self):
        """Clean up the current module"""
        if self.current_module:
            try:
                if hasattr(self.current_module, 'destroy'):
                    self.current_module.destroy()
            except Exception:
                pass
            self.current_module = None

    def clear_window(self):
        """Clear all widgets from the window"""
        print("Clearing window...")  # Debug
        for widget in self.root.winfo_children():
            try:
                widget.destroy()
            except Exception as e:
                print(f"Error destroying widget: {e}")

        # Force garbage collection
        self.root.update_idletasks()

    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            if self.db_connection and self.db_connection.is_connected():
                self.db_connection.close()
                print("✓ Database connection closed")
            self.root.destroy()

    def exit_app(self):
        """Exit the application"""
        self.cleanup_current_module()
        self.root.quit()
        sys.exit(0)

    def run(self):
        """Run the application"""
        try:
            # Set closing protocol
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Start the main loop
            self.root.mainloop()

        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            if APP_CONFIG['debug']:
                error_msg += f"\n\nTechnical details: {e}"

            messagebox.showerror("Application Error", error_msg)

        finally:
            # Ensure database connection is closed
            if self.db_connection and self.db_connection.is_connected():
                self.db_connection.close()
                print("✓ Database connection closed on exit")


def main():
    """Main entry point for the application"""
    print("=" * 60)
    print("BigBrew POS System")
    print("=" * 60)

    if APP_CONFIG['debug']:
        print("🚀 Starting application in DEBUG mode")
        print(f"📊 Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
        print("=" * 60)

    try:
        app = BigBrewApp()
        app.run()
    except KeyboardInterrupt:
        print("\n⚠️  Application interrupted by user")
    except Exception as e:
        print(f"💥 Critical error: {e}")
        messagebox.showerror("Fatal Error", f"The application encountered a critical error:\n\n{str(e)}")


if __name__ == "__main__":
    main()