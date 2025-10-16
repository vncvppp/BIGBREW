#!/usr/bin/env python3
"""
BigBrew POS System - Main Entry Point
Provides seamless navigation between login and signup modules
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from db_config import db
from login import LoginWindow
from signup import SignupWindow


class BigBrewApp:
    """Main application class that manages navigation between modules"""
    
    def __init__(self):
        self.current_module = None
        self.root = tk.Tk()
        self.root.title("BigBrew POS System")
        self.root.configure(bg='#f0f0f0')
        
        # Set window size for login/signup
        self.login_size = (800, 440)
        self.center_window(*self.login_size)
        self.root.resizable(False, False)
        
    def center_window(self, width, height):
        """Center the window on the screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def start(self):
        """Start the application with login screen"""
        try:
            # Test database connection first
            if not db.test_connection():
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
        """Show the login module"""
        try:
            # Clean up previous module if exists
            self.cleanup_current_module()
            
            # Create and show login module
            self.current_module = LoginWindow(self.root, self)
            self.current_module.run()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Login: {str(e)}")
    
    def show_signup(self):
        """Show the signup module"""
        try:
            # Clean up previous module if exists
            self.cleanup_current_module()
            
            # Create and show signup module
            self.current_module = SignupWindow(self.root, self)
            self.current_module.run()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Sign Up: {str(e)}")
    
    def show_dashboard(self, user_data):
        """Show dashboard after successful login"""
        try:
            from dashboard import DashboardManager
            self.cleanup_current_module()
            DashboardManager(user_data, self.root).show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Dashboard: {str(e)}")
    
    def cleanup_current_module(self):
        """Clean up the current module"""
        if self.current_module:
            try:
                if hasattr(self.current_module, 'destroy'):
                    self.current_module.destroy()
            except Exception:
                pass
            self.current_module = None
    
    def exit_app(self):
        """Exit the application"""
        self.cleanup_current_module()
        self.root.quit()
        sys.exit(0)

    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = BigBrewApp()
        app.start()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        messagebox.showerror("Fatal Error", f"The application encountered a critical error:\n\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()