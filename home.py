#!/usr/bin/env python3
"""
BigBrew Coffee Shop - Customer Home Page
Customer dashboard for online ordering, loyalty rewards, and account management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys
import os
from datetime import datetime

OUTPUT_PATH = Path(__file__).parent

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def relative_to_assets(path: str) -> Path:
    """Get path to assets in the customer home resources folder"""
    possible_paths = [
        resource_path(f"resources/home/{path}"),
        resource_path(f"home/resources/{path}"),
        os.path.join(OUTPUT_PATH, "resources", "home", path),
        os.path.join(OUTPUT_PATH, "home", "resources", path),
        resource_path(path),
    ]
    
    for asset_path in possible_paths:
        if os.path.exists(asset_path):
            return Path(asset_path)
    
    # If no path found, return the most likely one
    return Path(possible_paths[0])

class CustomerHome:
    def __init__(self, parent, customer_data, app):
        self.parent = parent
        self.customer_data = customer_data
        self.app = app
        self.images = []  # Keep references to images
        
        # Customer information
        self.customer_id = customer_data.get('customer_id')
        self.customer_code = customer_data.get('customer_code', 'N/A')
        self.username = customer_data.get('username', 'Customer')
        self.email = customer_data.get('email', 'N/A')
        self.first_name = customer_data.get('first_name', 'Customer')
        self.last_name = customer_data.get('last_name', 'User')
        self.customer_type = customer_data.get('customer_type', 'regular')
        self.loyalty_points = customer_data.get('loyalty_points', 0)
        self.total_spent = customer_data.get('total_spent', 0.0)
        
        self.setup_ui()
        
    def load_image(self, path: str):
        """Load image and keep reference to prevent garbage collection"""
        try:
            image_path = relative_to_assets(path)
            if not image_path.exists():
                print(f"Image not found: {image_path}")
                return None
            photo_image = tk.PhotoImage(file=image_path)
            self.images.append(photo_image)
            return photo_image
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None
    
    def setup_ui(self):
        """Setup the customer home UI"""
        # Clear any existing widgets first
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Create main frame
        self.main_frame = tk.Frame(self.parent, bg="#FFF8E7")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        self.create_header()
        
        # Main content area
        self.create_content_area()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Create the header section"""
        header_frame = tk.Frame(self.main_frame, bg="#8B4513", height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # BigBrew logo/title
        title_label = tk.Label(
            header_frame,
            text="BIGBREW COFFEE SHOP",
            font=("Inter Bold", 24),
            fg="#DAA520",
            bg="#8B4513"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Customer info
        customer_info_frame = tk.Frame(header_frame, bg="#8B4513")
        customer_info_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        welcome_label = tk.Label(
            customer_info_frame,
            text=f"Welcome, {self.first_name}!",
            font=("Inter", 14),
            fg="#FFFFFF",
            bg="#8B4513"
        )
        welcome_label.pack(anchor=tk.E)
        
        customer_type_label = tk.Label(
            customer_info_frame,
            text=f"{self.customer_type.title()} Member",
            font=("Inter", 10),
            fg="#DAA520",
            bg="#8B4513"
        )
        customer_type_label.pack(anchor=tk.E)
        
        # Logout button
        logout_btn = tk.Button(
            header_frame,
            text="Logout",
            font=("Inter", 10),
            bg="#D2691E",
            fg="#FFFFFF",
            relief=tk.FLAT,
            command=self.logout,
            cursor="hand2"
        )
        logout_btn.pack(side=tk.RIGHT, padx=10, pady=20)
    
    def create_content_area(self):
        """Create the main content area"""
        content_frame = tk.Frame(self.main_frame, bg="#FFF8E7")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left sidebar - Account info
        self.create_sidebar(content_frame)
        
        # Right main area - Features
        self.create_main_area(content_frame)
    
    def create_sidebar(self, parent):
        """Create the left sidebar with account information"""
        sidebar_frame = tk.Frame(parent, bg="#F5F5DC", width=300, relief=tk.RAISED, bd=1)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar_frame.pack_propagate(False)
        
        # Account info title
        account_title = tk.Label(
            sidebar_frame,
            text="Account Information",
            font=("Inter Bold", 16),
            fg="#8B4513",
            bg="#F5F5DC"
        )
        account_title.pack(pady=20)
        
        # Account details
        details_frame = tk.Frame(sidebar_frame, bg="#F5F5DC")
        details_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Customer code
        tk.Label(details_frame, text="Customer Code:", font=("Inter", 10), fg="#8B4513", bg="#F5F5DC").pack(anchor=tk.W)
        tk.Label(details_frame, text=self.customer_code, font=("Inter Bold", 10), fg="#000000", bg="#F5F5DC").pack(anchor=tk.W, pady=(0, 10))
        
        # Email
        tk.Label(details_frame, text="Email:", font=("Inter", 10), fg="#8B4513", bg="#F5F5DC").pack(anchor=tk.W)
        tk.Label(details_frame, text=self.email, font=("Inter Bold", 10), fg="#000000", bg="#F5F5DC").pack(anchor=tk.W, pady=(0, 10))
        
        # Customer type
        tk.Label(details_frame, text="Member Type:", font=("Inter", 10), fg="#8B4513", bg="#F5F5DC").pack(anchor=tk.W)
        tk.Label(details_frame, text=self.customer_type.title(), font=("Inter Bold", 10), fg="#000000", bg="#F5F5DC").pack(anchor=tk.W, pady=(0, 10))
        
        # Loyalty points
        tk.Label(details_frame, text="Loyalty Points:", font=("Inter", 10), fg="#8B4513", bg="#F5F5DC").pack(anchor=tk.W)
        tk.Label(details_frame, text=f"{self.loyalty_points:,}", font=("Inter Bold", 12), fg="#DAA520", bg="#F5F5DC").pack(anchor=tk.W, pady=(0, 10))
        
        # Total spent
        tk.Label(details_frame, text="Total Spent:", font=("Inter", 10), fg="#8B4513", bg="#F5F5DC").pack(anchor=tk.W)
        tk.Label(details_frame, text=f"₱{self.total_spent:.2f}", font=("Inter Bold", 12), fg="#8B4513", bg="#F5F5DC").pack(anchor=tk.W, pady=(0, 20))
        
        # Account actions
        actions_frame = tk.Frame(sidebar_frame, bg="#F5F5DC")
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(
            actions_frame,
            text="Edit Profile",
            font=("Inter", 10),
            bg="#8B4513",
            fg="#FFFFFF",
            relief=tk.FLAT,
            command=self.edit_profile,
            cursor="hand2"
        ).pack(fill=tk.X, pady=5)
        
        tk.Button(
            actions_frame,
            text="Order History",
            font=("Inter", 10),
            bg="#D2691E",
            fg="#FFFFFF",
            relief=tk.FLAT,
            command=self.view_order_history,
            cursor="hand2"
        ).pack(fill=tk.X, pady=5)
    
    def create_main_area(self, parent):
        """Create the main area with features"""
        main_area_frame = tk.Frame(parent, bg="#FFF8E7")
        main_area_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Welcome message
        welcome_frame = tk.Frame(main_area_frame, bg="#FFF8E7")
        welcome_frame.pack(fill=tk.X, pady=(0, 20))
        
        welcome_text = f"Welcome to BigBrew Coffee Shop, {self.first_name}!"
        tk.Label(
            welcome_frame,
            text=welcome_text,
            font=("Inter Bold", 18),
            fg="#8B4513",
            bg="#FFF8E7"
        ).pack(anchor=tk.W)
        
        tk.Label(
            welcome_frame,
            text="Discover our premium coffee blends and delicious pastries",
            font=("Inter", 12),
            fg="#666666",
            bg="#FFF8E7"
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Features grid
        features_frame = tk.Frame(main_area_frame, bg="#FFF8E7")
        features_frame.pack(fill=tk.BOTH, expand=True)
        
        # Feature buttons
        self.create_feature_buttons(features_frame)
    
    def create_feature_buttons(self, parent):
        """Create feature buttons in a grid layout"""
        # Online Ordering
        order_frame = tk.Frame(parent, bg="#FFFFFF", relief=tk.RAISED, bd=2)
        order_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            order_frame,
            text="☕",
            font=("Arial", 48),
            fg="#8B4513",
            bg="#FFFFFF"
        ).pack(pady=20)
        
        tk.Label(
            order_frame,
            text="Online Ordering",
            font=("Inter Bold", 16),
            fg="#8B4513",
            bg="#FFFFFF"
        ).pack()
        
        tk.Label(
            order_frame,
            text="Order your favorite coffee\nand pastries online",
            font=("Inter", 10),
            fg="#666666",
            bg="#FFFFFF"
        ).pack(pady=10)
        
        tk.Button(
            order_frame,
            text="Order Now",
            font=("Inter", 12),
            bg="#8B4513",
            fg="#FFFFFF",
            relief=tk.FLAT,
            command=self.start_online_order,
            cursor="hand2"
        ).pack(pady=20)
        
        # Loyalty Rewards
        rewards_frame = tk.Frame(parent, bg="#FFFFFF", relief=tk.RAISED, bd=2)
        rewards_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            rewards_frame,
            text="🎁",
            font=("Arial", 48),
            fg="#DAA520",
            bg="#FFFFFF"
        ).pack(pady=20)
        
        tk.Label(
            rewards_frame,
            text="Loyalty Rewards",
            font=("Inter Bold", 16),
            fg="#8B4513",
            bg="#FFFFFF"
        ).pack()
        
        tk.Label(
            rewards_frame,
            text=f"Earn points with every purchase\nCurrent points: {self.loyalty_points:,}",
            font=("Inter", 10),
            fg="#666666",
            bg="#FFFFFF"
        ).pack(pady=10)
        
        tk.Button(
            rewards_frame,
            text="View Rewards",
            font=("Inter", 12),
            bg="#DAA520",
            fg="#FFFFFF",
            relief=tk.FLAT,
            command=self.view_rewards,
            cursor="hand2"
        ).pack(pady=20)
        
        # Store Locator
        store_frame = tk.Frame(parent, bg="#FFFFFF", relief=tk.RAISED, bd=2)
        store_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            store_frame,
            text="📍",
            font=("Arial", 48),
            fg="#D2691E",
            bg="#FFFFFF"
        ).pack(pady=20)
        
        tk.Label(
            store_frame,
            text="Store Locator",
            font=("Inter Bold", 16),
            fg="#8B4513",
            bg="#FFFFFF"
        ).pack()
        
        tk.Label(
            store_frame,
            text="Find BigBrew locations\nnear you",
            font=("Inter", 10),
            fg="#666666",
            bg="#FFFFFF"
        ).pack(pady=10)
        
        tk.Button(
            store_frame,
            text="Find Stores",
            font=("Inter", 12),
            bg="#D2691E",
            fg="#FFFFFF",
            relief=tk.FLAT,
            command=self.find_stores,
            cursor="hand2"
        ).pack(pady=20)
    
    def create_footer(self):
        """Create the footer section"""
        footer_frame = tk.Frame(self.main_frame, bg="#8B4513", height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        tk.Label(
            footer_frame,
            text="© 2024 BigBrew Coffee Shop - Customer Portal",
            font=("Inter", 10),
            fg="#DAA520",
            bg="#8B4513"
        ).pack(pady=10)
    
    def start_online_order(self):
        """Start online ordering process"""
        messagebox.showinfo("Online Ordering", "Online ordering feature coming soon!\n\nYou'll be able to browse our menu and place orders for pickup or delivery.")
    
    def view_rewards(self):
        """View loyalty rewards"""
        messagebox.showinfo("Loyalty Rewards", f"Your Loyalty Points: {self.loyalty_points:,}\n\nPoints can be redeemed for:\n• Free coffee drinks\n• Discounts on orders\n• Special promotions\n\nKeep ordering to earn more points!")
    
    def find_stores(self):
        """Find nearby stores"""
        messagebox.showinfo("Store Locator", "Store locator feature coming soon!\n\nYou'll be able to find BigBrew locations near you with directions and store hours.")
    
    def edit_profile(self):
        """Edit customer profile"""
        messagebox.showinfo("Edit Profile", "Profile editing feature coming soon!\n\nYou'll be able to update your personal information, delivery addresses, and preferences.")
    
    def view_order_history(self):
        """View order history"""
        messagebox.showinfo("Order History", "Order history feature coming soon!\n\nYou'll be able to view your past orders, reorder favorites, and track current orders.")
    
    def logout(self):
        """Logout customer"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.app.logout()
    
    def destroy(self):
        """Clean up the customer home window"""
        for widget in self.parent.winfo_children():
            widget.destroy()

# For testing purposes
if __name__ == "__main__":
    # Sample customer data for testing
    sample_customer = {
        'customer_id': 1,
        'customer_code': 'CUST-20241201120000',
        'username': 'john.doe',
        'email': 'john.doe@email.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'customer_type': 'regular',
        'loyalty_points': 150,
        'total_spent': 250.75,
        'account_type': 'customer'
    }
    
    class MockApp:
        def logout(self):
            print("Mock logout called")
    
    root = tk.Tk()
    root.title("BigBrew Customer Home - Test")
    root.geometry("1000x700")
    root.configure(bg="#FFF8E7")
    
    app = MockApp()
    customer_home = CustomerHome(root, sample_customer, app)
    
    root.mainloop()
