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
import subprocess
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
        os.path.join(OUTPUT_PATH, "resources", "home", path),
        os.path.join(OUTPUT_PATH, "home", "resources", path),
        resource_path(f"resources/home/{path}"),
        resource_path(f"home/resources/{path}"),
        os.path.join(OUTPUT_PATH, path),
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
        
    def center_parent(self, width: int = 1035, height: int = 534):
        """Center the parent window on the screen for the given size."""
        try:
            self.parent.update_idletasks()
            screen_w = self.parent.winfo_screenwidth()
            screen_h = self.parent.winfo_screenheight()
            x = int((screen_w - width) / 2)
            y = int((screen_h - height) / 2)
            self.parent.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            # Fallback to default geometry if centering fails
            self.parent.geometry(f"{width}x{height}")

    def load_image(self, path: str):
        """Load image and keep reference to prevent garbage collection"""
        try:
            image_path = relative_to_assets(path)
            if not image_path.exists():
                print(f"Image not found: {image_path}")
                return None
            photo_image = tk.PhotoImage(file=str(image_path))
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
        
        # Configure parent window
        self.parent.configure(bg="#FFFFFF")
        self.parent.geometry("1035x534")
        # Lock exact window size to avoid extra whitespace and layout drift
        try:
            self.parent.resizable(False, False)
            self.parent.minsize(1035, 534)
            self.parent.maxsize(1035, 534)
        except Exception:
            # If running in an environment that does not support these, ignore
            pass
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.parent,
            bg="#FFFFFF",
            height=534,
            width=1035,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        # Draw the UI elements
        self.draw_background()
        self.draw_header()
        self.draw_account_info()
        self.draw_feature_cards()
        self.draw_buttons()
        # Center window after layout
        self.center_parent(1035, 534)
    
    def draw_background(self):
        """Draw background elements"""
        # Background image (optional - can be removed if image doesn't exist)
        try:
            bg_image = self.load_image("image_1.png")
            if bg_image:
                self.canvas.create_image(517.0, 267.0, image=bg_image)
        except:
            pass
        
        # Header background
        self.canvas.create_rectangle(
            0.0, 0.0, 1035.0, 58.0,
            fill="#B96708",
            outline=""
        )
        
        # Logo
        try:
            logo_image = self.load_image("logo.png")
            if logo_image:
                self.canvas.create_image(85.0, 29.0, image=logo_image)
        except:
            pass
        
        # Main content background
        self.canvas.create_rectangle(
            0.0, 58.0, 1035.0, 534.0,
            fill="#EFE8D8",
            outline=""
        )
    
    def draw_header(self):
        """Draw header elements"""
        # Welcome text
        self.canvas.create_text(
            716.0, 8.0,
            anchor="nw",
            text=f"Welcome, {self.first_name}!",
            fill="#FFFFFF",
            font=("Poppins SemiBold", 16 * -1)
        )
        
        # Member type
        member_type_text = f"{self.customer_type.title()} Member"
        self.canvas.create_text(
            780.0, 31.0,
            anchor="nw",
            text=member_type_text,
            fill="#EFE8D8",
            font=("Poppins Regular", 13 * -1)
        )
        
    def draw_account_info(self):
        """Draw account information sidebar"""
        # Account info box
        self.canvas.create_rectangle(
            27.0, 88.0, 312.0, 512.0,
            fill="#FFF8E7",
            outline=""
        )
        
        # Account Information title
        self.canvas.create_text(
            72.8, 108.1,
            anchor="nw",
            text="Account Information",
            fill="#3A280F",
            font=("Poppins ExtraBold", 16 * -1)
        )
        
        # Customer code
        self.canvas.create_text(
            58.6, 157.9,
            anchor="nw",
            text="Customer Code:",
            fill="#B96708",
            font=("Poppins Regular", 11 * -1)
        )
        self.canvas.create_text(
            58.6, 175.1,
            anchor="nw",
            text=self.customer_code,
            fill="#000000",
            font=("Poppins Regular", 13 * -1)
        )
        
        # Email
        self.canvas.create_text(
            58.6, 216.3,
            anchor="nw",
            text="Email Address:",
            fill="#B96708",
            font=("Poppins Regular", 11 * -1)
        )
        self.canvas.create_text(
            58.6, 237.3,
            anchor="nw",
            text=self.email,
            fill="#000000",
            font=("Poppins Regular", 13 * -1)
        )
        
        # Member type
        self.canvas.create_text(
            57.5, 272.7,
            anchor="nw",
            text="Member Type:",
            fill="#B96708",
            font=("Poppins Regular", 11 * -1)
        )
        self.canvas.create_text(
            57.5, 290.0,
            anchor="nw",
            text=self.customer_type.upper(),
            fill="#000000",
            font=("Poppins Regular", 13 * -1)
        )
        
        # Total points
        self.canvas.create_text(
            57.5, 331.1,
            anchor="nw",
            text="Total Points:",
            fill="#B96708",
            font=("Poppins Regular", 11 * -1)
        )
        self.canvas.create_text(
            57.5, 348.3,
            anchor="nw",
            text=f"{self.loyalty_points:,}",
            fill="#000000",
            font=("Poppins Regular", 13 * -1)
        )
        
        # Total spent
        self.canvas.create_text(
            57.5, 381.8,
            anchor="nw",
            text="Total Spent:",
            fill="#B96708",
            font=("Poppins Regular", 11 * -1)
        )
        self.canvas.create_text(
            57.5, 399.1,
            anchor="nw",
            text=f"₱{self.total_spent:.2f}",
            fill="#B45309",
            font=("Inter", 13 * -1)
        )
    
    def draw_feature_cards(self):
        """Draw feature cards"""
        # Main title
        self.canvas.create_text(
            349.0, 80.0,
            anchor="nw",
            text="READY TO SIP INTO YOUR FUTURE?",
            fill="#3A280F",
            font=("Poppins ExtraBold", 24 * -1)
        )
        
        self.canvas.create_text(
            349.0, 113.0,
            anchor="nw",
            text="Brew Success with Big Brew.",
            fill="#000000",
            font=("Poppins Regular", 13 * -1)
        )
        
        # Card 1 - Online Ordering
        self.canvas.create_rectangle(
            349.0, 143.0, 541.0, 512.0,
            fill="#FFF8E7",
            outline=""
        )
        
        try:
            coffee_img = self.load_image("coffee.png")
            if coffee_img:
                self.canvas.create_image(445.0, 232.0, image=coffee_img)
        except:
            pass
        
        self.canvas.create_text(
            366.0, 263.0,
            anchor="nw",
            text="Online Ordering",
            fill="#000000",
            font=("Poppins SemiBold", 20 * -1)
        )
        
        self.canvas.create_text(
            364.0, 305.0,
            anchor="nw",
            text="Order Your Favorite Milk ",
            fill="#999999",
            font=("Poppins Regular", 13 * -1)
        )
        
        self.canvas.create_text(
            364.0, 330.0,
            anchor="nw",
            text="Tea, Praf, Coffee, Fruit ",
            fill="#999999",
            font=("Poppins Regular", 13 * -1)
        )
        
        self.canvas.create_text(
            364.0, 355.0,
            anchor="nw",
            text="Tea or Brosty Online.",
            fill="#999999",
            font=("Poppins Regular", 13 * -1)
        )
        
        # Card 2 - Loyalty Rewards
        self.canvas.create_rectangle(
            576.0, 143.0, 768.0, 512.0,
            fill="#FFF8E7",
            outline=""
        )
        
        try:
            gift_img = self.load_image("gift.png")
            if gift_img:
                self.canvas.create_image(672.0, 233.0, image=gift_img)
        except:
            pass
        
        self.canvas.create_text(
            591.0, 264.0,
            anchor="nw",
            text="Loyalty Rewards",
            fill="#000000",
            font=("Poppins SemiBold", 20 * -1)
        )
        
        self.canvas.create_text(
            594.0, 301.0,
            anchor="nw",
            text="Earn points with every ",
            fill="#999999",
            font=("Poppins Regular", 13 * -1)
        )
        
        self.canvas.create_text(
            594.0, 325.0,
            anchor="nw",
            text="purchase.",
            fill="#999999",
            font=("Poppins Regular", 13 * -1)
        )
        
        # Card 3 - Store Locator
        self.canvas.create_rectangle(
            796.0, 143.0, 988.0, 512.0,
            fill="#FFF8E7",
            outline=""
        )
        
        try:
            loc_img = self.load_image("loc.png")
            if loc_img:
                self.canvas.create_image(892.0, 235.0, image=loc_img)
        except:
            pass
        
        self.canvas.create_text(
            824.0, 265.0,
            anchor="nw",
            text="Store Locator",
            fill="#000000",
            font=("Poppins SemiBold", 20 * -1)
        )
        
        self.canvas.create_text(
            810.0, 300.0,
            anchor="nw",
            text="Find Big Brew locations ",
            fill="#999999",
            font=("Poppins Regular", 13 * -1)
        )
        
        self.canvas.create_text(
            810.0, 325.0,
            anchor="nw",
            text="near you.",
            fill="#999999",
            font=("Poppins Regular", 13 * -1)
        )
    
    def draw_buttons(self):
        """Draw buttons"""
        # Order Now button
        try:
            order_btn_img = self.load_image("button_order_now.png")
            if order_btn_img:
                self.order_btn = tk.Button(
                    image=order_btn_img,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.start_online_order,
                    relief="flat"
                )
                self.order_btn.place(x=379.0, y=450.0, width=131.0, height=40.0)
            else:
                # Fallback to text button
                self.order_btn = tk.Button(
                    self.parent,
                    text="Order Now",
                    font=("Poppins", 12),
                    bg="#B96708",
                    fg="#FFFFFF",
                    relief="flat",
                    command=self.start_online_order,
                    cursor="hand2"
                )
                self.order_btn.place(x=379.0, y=450.0, width=131.0, height=40.0)
        except:
            # Fallback to text button
            self.order_btn = tk.Button(
                self.parent,
                text="Order Now",
                font=("Poppins", 12),
                bg="#B96708",
                fg="#FFFFFF",
                relief="flat",
                command=self.start_online_order,
                cursor="hand2"
            )
            self.order_btn.place(x=379.0, y=450.0, width=131.0, height=40.0)
        
        # View Rewards button
        try:
            rewards_btn_img = self.load_image("button_vw_rewards.png")
            if rewards_btn_img:
                self.rewards_btn = tk.Button(
                    image=rewards_btn_img,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.view_rewards,
                    relief="flat"
                )
                self.rewards_btn.place(x=603.0, y=450.0, width=138.0, height=40.0)
            else:
                self.rewards_btn = tk.Button(
                    self.parent,
                    text="View Rewards",
                    font=("Poppins", 12),
                    bg="#B96708",
                    fg="#FFFFFF",
                    relief="flat",
                    command=self.view_rewards,
                    cursor="hand2"
                )
                self.rewards_btn.place(x=603.0, y=450.0, width=138.0, height=40.0)
        except:
            self.rewards_btn = tk.Button(
                self.parent,
                text="View Rewards",
                font=("Poppins", 12),
                bg="#B96708",
                fg="#FFFFFF",
                relief="flat",
                command=self.view_rewards,
                cursor="hand2"
            )
            self.rewards_btn.place(x=603.0, y=450.0, width=138.0, height=40.0)
        
        # Store Locator button
        try:
            store_btn_img = self.load_image("button_store_loc.png")
            if store_btn_img:
                self.store_btn = tk.Button(
                    image=store_btn_img,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.find_stores,
                    relief="flat"
                )
                self.store_btn.place(x=830.0, y=450.0, width=131.0, height=40.0)
            else:
                self.store_btn = tk.Button(
                    self.parent,
                    text="Find Stores",
                    font=("Poppins", 12),
                    bg="#B96708",
                    fg="#FFFFFF",
                    relief="flat",
                    command=self.find_stores,
                    cursor="hand2"
                )
                self.store_btn.place(x=830.0, y=450.0, width=131.0, height=40.0)
        except:
            self.store_btn = tk.Button(
                self.parent,
                text="Find Stores",
                font=("Poppins", 12),
                bg="#B96708",
                fg="#FFFFFF",
                relief="flat",
                command=self.find_stores,
                cursor="hand2"
            )
            self.store_btn.place(x=830.0, y=450.0, width=131.0, height=40.0)
        
        # Edit Profile button
        try:
            edit_btn_img = self.load_image("button_edit_prof.png")
            if edit_btn_img:
                self.edit_btn = tk.Button(
                    image=edit_btn_img,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.edit_profile,
                    relief="flat"
                )
                self.edit_btn.place(x=58.6, y=428.7, width=231.1, height=30.6)
            else:
                self.edit_btn = tk.Button(
                    self.parent,
                    text="Edit Profile",
                    font=("Poppins", 10),
                    bg="#B96708",
                    fg="#FFFFFF",
                    relief="flat",
                    command=self.edit_profile,
                    cursor="hand2"
                )
                self.edit_btn.place(x=58.6, y=428.7, width=231.1, height=30.6)
        except:
            self.edit_btn = tk.Button(
                self.parent,
                text="Edit Profile",
                font=("Poppins", 10),
                bg="#B96708",
                fg="#FFFFFF",
                relief="flat",
                command=self.edit_profile,
                cursor="hand2"
            )
            self.edit_btn.place(x=58.6, y=428.7, width=231.1, height=30.6)
        
        # Order History button
        try:
            # Try both possible filenames
            history_btn_img = self.load_image("button_order_history.png")
            if not history_btn_img:
                history_btn_img = self.load_image("button_order_historypng")
            if history_btn_img:
                self.history_btn = tk.Button(
                    image=history_btn_img,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.view_order_history,
                    relief="flat"
                )
                self.history_btn.place(x=58.6, y=468.0, width=231.1, height=29.7)
            else:
                self.history_btn = tk.Button(
                    self.parent,
                    text="Order History",
                    font=("Poppins", 10),
                    bg="#B96708",
                    fg="#FFFFFF",
                    relief="flat",
                    command=self.view_order_history,
                    cursor="hand2"
                )
                self.history_btn.place(x=58.6, y=468.0, width=231.1, height=29.7)
        except:
            self.history_btn = tk.Button(
                self.parent,
                text="Order History",
                font=("Poppins", 10),
                bg="#B96708",
                fg="#FFFFFF",
                relief="flat",
                command=self.view_order_history,
                cursor="hand2"
            )
            self.history_btn.place(x=58.6, y=468.0, width=231.1, height=29.7)
        
        # Logout button
        try:
            logout_btn_img = self.load_image("button_logout.png")
            if logout_btn_img:
                self.logout_btn = tk.Button(
                    image=logout_btn_img,
                    borderwidth=0,
                    highlightthickness=0,
                    command=self.logout,
                    relief="flat"
                )
                self.logout_btn.place(x=909.0, y=14.0, width=85.0, height=30.0)
            else:
                self.logout_btn = tk.Button(
                    self.parent,
                    text="Logout",
                    font=("Poppins", 10),
                    bg="#D2691E",
                    fg="#FFFFFF",
                    relief="flat",
                    command=self.logout,
                    cursor="hand2"
                )
                self.logout_btn.place(x=909.0, y=14.0, width=85.0, height=30.0)
        except:
            self.logout_btn = tk.Button(
                self.parent,
                text="Logout",
                font=("Poppins", 10),
                bg="#D2691E",
                fg="#FFFFFF",
                relief="flat",
                command=self.logout,
                cursor="hand2"
            )
            self.logout_btn.place(x=909.0, y=14.0, width=85.0, height=30.0)
    
    def start_online_order(self):
        """Start online ordering process by launching order.py in a new process"""
        try:
            order_script = os.path.join(OUTPUT_PATH, "order.py")
            if not os.path.exists(order_script):
                messagebox.showerror("Error", "order.py not found in the application directory.")
                return

            # Launch as a separate Python process to avoid multiple Tk roots
            subprocess.Popen([sys.executable, order_script], cwd=str(OUTPUT_PATH))
            # Close the home window when order window opens
            self.parent.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Order window.\n\n{e}")
    
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
    root.geometry("1035x534")
    root.configure(bg="#FFFFFF")
    
    app = MockApp()
    customer_home = CustomerHome(root, sample_customer, app)
    
    root.mainloop()
