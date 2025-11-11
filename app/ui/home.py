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
from decimal import Decimal
import re
import bcrypt

from app.db.connection import db
from app.services.shared_state import clear_cart, set_current_customer

OUTPUT_PATH = Path(__file__).resolve().parent
PROJECT_ROOT = OUTPUT_PATH.parent.parent


def _parse_customer_id(argv):
    """Return customer_id from CLI args if provided."""
    if not argv:
        return None
    for idx, arg in enumerate(argv):
        if arg.startswith("--customer-id="):
            value = arg.split("=", 1)[1]
        elif arg == "--customer-id" and idx + 1 < len(argv):
            value = argv[idx + 1]
        else:
            continue
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _coerce_int(value, default=0):
    if value in (None, ""):
        return default
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return default


def _coerce_float(value, default=0.0):
    if value in (None, ""):
        return default
    try:
        if isinstance(value, Decimal):
            return float(value)
        return float(value)
    except Exception:
        return default


def _load_customer_from_db(customer_id):
    """Fetch customer details from the database for the given id."""
    try:
        rows = db.execute_query(
            """
            SELECT customer_id, customer_code, username, email,
                   first_name, last_name, customer_type,
                   loyalty_points, total_spent, phone, address
            FROM customers
            WHERE customer_id = %s
            """,
            (customer_id,),
            fetch=True,
        )
    except Exception as exc:
        print(f"Failed to load customer {customer_id}: {exc}")
        return None

    if not rows:
        return None

    row = rows[0]
    return {
        "customer_id": _coerce_int(row.get("customer_id"), default=customer_id),
        "customer_code": row.get("customer_code") or "N/A",
        "username": row.get("username") or "customer",
        "email": row.get("email") or "N/A",
        "first_name": (row.get("first_name") or "").strip() or "Customer",
        "last_name": (row.get("last_name") or "").strip(),
        "customer_type": (row.get("customer_type") or "regular").lower(),
        "loyalty_points": _coerce_int(row.get("loyalty_points"), default=0),
        "total_spent": _coerce_float(row.get("total_spent"), default=0.0),
        "phone": (row.get("phone") or "").strip(),
        "address": (row.get("address") or "").strip(),
    }

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
        self.customer_data = dict(customer_data or {})
        self.app = app
        self.images = []  # Keep references to images
        
        # Default values
        self.customer_id = None
        self.customer_code = 'N/A'
        self.username = 'Customer'
        self.email = 'N/A'
        self.first_name = 'Customer'
        self.last_name = 'User'
        self.customer_type = 'regular'
        self.loyalty_points = 0
        self.total_spent = 0.0
        self.phone = ''
        self.address = ''

        self._apply_customer_updates(self.customer_data)
        
        self.setup_ui()

    def _apply_customer_updates(self, data):
        if not data:
            return

        # Update backing dictionary (ignoring None values)
        for key, value in data.items():
            if value is not None:
                self.customer_data[key] = value

        self.customer_id = self.customer_data.get('customer_id', self.customer_id)
        self.customer_code = self.customer_data.get('customer_code', self.customer_code)
        self.username = self.customer_data.get('username', self.username)
        self.email = self.customer_data.get('email', self.email)

        first_name = (self.customer_data.get('first_name') or '').strip()
        last_name = (self.customer_data.get('last_name') or '').strip()
        if first_name:
            self.first_name = first_name
        else:
            self.first_name = 'Customer'
        self.last_name = last_name or 'User'

        self.customer_type = self.customer_data.get('customer_type', self.customer_type)
        self.loyalty_points = self.customer_data.get('loyalty_points', self.loyalty_points)
        self.total_spent = self.customer_data.get('total_spent', self.total_spent)
        self.phone = self.customer_data.get('phone', self.phone)
        self.address = self.customer_data.get('address', self.address)
        
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
            args = [sys.executable, "-m", "app.ui.order"]
            if self.customer_id:
                args.append(f"--customer-id={self.customer_id}")
            subprocess.Popen(args, cwd=str(PROJECT_ROOT))
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
        """Open dialog to edit customer profile."""
        if not self.customer_id:
            messagebox.showinfo("Edit Profile", "No customer information available.")
            return

        latest = _load_customer_from_db(self.customer_id)
        if latest:
            self._apply_customer_updates(latest)

        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Profile")
        dialog.configure(bg="#FFF8E7")
        dialog.resizable(False, False)

        try:
            dialog.transient(self.parent)
            dialog.grab_set()
        except Exception:
            pass

        try:
            dialog.update_idletasks()
            width, height = 420, 530
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()
            px = self.parent.winfo_rootx()
            py = self.parent.winfo_rooty()
            x = int(px + (pw - width) / 2)
            y = int(py + (ph - height) / 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            dialog.geometry("420x530")

        header = tk.Label(
            dialog,
            text="Update Profile",
            font=("Poppins", 16, "bold"),
            bg="#FFF8E7",
            fg="#3A280F",
        )
        header.pack(pady=(20, 10))

        form_frame = tk.Frame(dialog, bg="#FFF8E7")
        form_frame.pack(fill="both", expand=True, padx=30)

        def add_row(row, label_text, widget):
            label = tk.Label(
                form_frame,
                text=label_text,
                font=("Poppins", 10, "bold"),
                anchor="w",
                bg="#FFF8E7",
                fg="#3A280F",
            )
            label.grid(row=row, column=0, sticky="w")
            widget.grid(row=row + 1, column=0, sticky="ew", pady=(0, 12))

        form_frame.columnconfigure(0, weight=1)

        entry_style = {"font": ("Poppins", 10), "bg": "#FFFFFF", "fg": "#000000", "relief": "solid", "borderwidth": 1}

        first_name_var = tk.StringVar(value=self.first_name)
        first_entry = tk.Entry(form_frame, textvariable=first_name_var, **entry_style)
        add_row(0, "First Name", first_entry)

        last_name_var = tk.StringVar(value=self.last_name)
        last_entry = tk.Entry(form_frame, textvariable=last_name_var, **entry_style)
        add_row(2, "Last Name", last_entry)

        email_var = tk.StringVar(value=self.email)
        email_entry = tk.Entry(form_frame, textvariable=email_var, **entry_style)
        add_row(4, "Email Address", email_entry)

        phone_var = tk.StringVar(value=self.phone or "")
        phone_entry = tk.Entry(form_frame, textvariable=phone_var, **entry_style)
        add_row(6, "Phone Number", phone_entry)

        address_text = tk.Text(form_frame, height=2, wrap="word", font=("Poppins", 10), bg="#FFFFFF", fg="#000000", relief="solid", borderwidth=1)
        address_text.insert("1.0", self.address or "")
        add_row(8, "Address", address_text)

        password_var = tk.StringVar()
        password_entry = tk.Entry(form_frame, textvariable=password_var, show="●", **entry_style)
        add_row(10, "New Password (optional)", password_entry)

        confirm_var = tk.StringVar()
        confirm_entry = tk.Entry(form_frame, textvariable=confirm_var, show="●", **entry_style)
        add_row(12, "Confirm Password", confirm_entry)

        info_label = tk.Label(
            form_frame,
            text="Leave password fields blank to keep your current password.",
            font=("Poppins", 9),
            bg="#FFF8E7",
            fg="#6C6C6C",
            wraplength=340,
            justify="left",
        )
        info_label.grid(row=14, column=0, sticky="w", pady=(0, 8))

        button_frame = tk.Frame(dialog, bg="#FFF8E7")
        button_frame.pack(pady=(0, 20))

        def close_dialog():
            try:
                dialog.destroy()
            except Exception:
                pass

        def save_profile():
            first_name = first_name_var.get().strip()
            last_name = last_name_var.get().strip()
            email = email_var.get().strip()
            phone = phone_var.get().strip()
            address = address_text.get("1.0", "end").strip()
            new_password = password_var.get()
            confirm_password = confirm_var.get()

            if not first_name:
                messagebox.showerror("Edit Profile", "First name cannot be empty.")
                return
            if not email:
                messagebox.showerror("Edit Profile", "Email address cannot be empty.")
                return
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                messagebox.showerror("Edit Profile", "Please enter a valid email address.")
                return

            if new_password or confirm_password:
                if len(new_password) < 6:
                    messagebox.showerror("Edit Profile", "Password must be at least 6 characters long.")
                    return
                if new_password != confirm_password:
                    messagebox.showerror("Edit Profile", "New password and confirmation do not match.")
                    return

            duplicates = db.execute_query(
                "SELECT customer_id FROM customers WHERE email = %s AND customer_id <> %s",
                (email, self.customer_id),
                fetch=True,
            )
            if duplicates:
                messagebox.showerror("Edit Profile", "That email address is already registered to another account.")
                return

            try:
                result = db.update_customer_profile(
                    self.customer_id,
                    first_name,
                    last_name,
                    email,
                    phone,
                    address,
                )
                if result is None:
                    messagebox.showerror("Edit Profile", "Failed to update profile. Please try again.")
                    return
            except Exception as exc:
                messagebox.showerror("Edit Profile", f"Failed to update profile: {exc}")
                return

            if new_password:
                try:
                    hash_value = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    db.update_customer_password_hash(self.customer_id, hash_value)
                except Exception as exc:
                    messagebox.showerror("Edit Profile", f"Profile updated, but failed to update password: {exc}")
                    # do not return; still refresh data

            updated_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "address": address,
            }
            self._apply_customer_updates(updated_data)
            messagebox.showinfo("Edit Profile", "Profile updated successfully.")
            close_dialog()
            self.setup_ui()

        save_btn = tk.Button(
            button_frame,
            text="Save Changes",
            font=("Poppins", 11, "bold"),
            bg="#28A745",
            fg="white",
            activebackground="#218838",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=save_profile,
        )
        save_btn.pack(side="left", padx=10)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Poppins", 11),
            bg="#6C757D",
            fg="white",
            activebackground="#5a6268",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=close_dialog,
        )
        cancel_btn.pack(side="left", padx=10)
    
    def view_order_history(self):
        """View order history"""
        if not self.customer_id:
            messagebox.showinfo("Order History", "No customer information available.")
            return

        orders = db.fetch_customer_orders(self.customer_id)
        if not orders:
            messagebox.showinfo("Order History", "You have no recorded orders yet.\nPlace an order to see it listed here.")
            return

        history_win = tk.Toplevel(self.parent)
        history_win.title("Order History")
        history_win.geometry("720x420")
        history_win.configure(bg="#FFF8E7")

        try:
            history_win.transient(self.parent)
            history_win.grab_set()
        except Exception:
            pass

        try:
            history_win.update_idletasks()
            w, h = 720, 420
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()
            px = self.parent.winfo_rootx()
            py = self.parent.winfo_rooty()
            x = int(px + (pw - w) / 2)
            y = int(py + (ph - h) / 2)
            history_win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

        columns = ("order_id", "total", "payment", "status", "date", "items")
        tree = ttk.Treeview(
            history_win,
            columns=columns,
            show="headings",
            height=12,
        )
        tree.heading("order_id", text="Order ID")
        tree.heading("total", text="Total Amount")
        tree.heading("payment", text="Payment Method")
        tree.heading("status", text="Status")
        tree.heading("date", text="Date")
        tree.heading("items", text="Items")

        tree.column("order_id", width=80, anchor="center")
        tree.column("total", width=120, anchor="center")
        tree.column("payment", width=160, anchor="center")
        tree.column("status", width=120, anchor="center")
        tree.column("date", width=200, anchor="center")
        tree.column("items", width=420, anchor="w")

        for order in orders:
            sale_id = order.get("sale_id")
            items_description = ""
            if sale_id:
                try:
                    sale_items = db.fetch_sale_items(sale_id)
                    if sale_items:
                        formatted = [
                            f"{item.get('name') or 'Item'} x{item.get('quantity', 0)} @ ₱{float(item.get('price') or 0.0):.2f}"
                            for item in sale_items
                        ]
                        items_description = "; ".join(formatted)
                except Exception:
                    items_description = ""

            tree.insert(
                "",
                "end",
                values=(
                    order.get("sale_id"),
                    f"₱{float(order.get('total_amount') or 0.0):,.2f}",
                    order.get("payment_method", "").title(),
                    order.get("status", "pending").title(),
                    str(order.get("sale_date") or ""),
                    items_description,
                ),
            )

        x_scroll = ttk.Scrollbar(history_win, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=x_scroll.set)
        tree.pack(fill="both", expand=True, padx=20, pady=(20, 0))
        x_scroll.pack(fill="x", padx=20, pady=(0, 20))

        def close_history():
            history_win.destroy()

        close_btn = tk.Button(
            history_win,
            text="Close",
            font=("Poppins", 11, "bold"),
            bg="#B96708",
            fg="white",
            relief="flat",
            width=12,
            command=close_history,
        )
        close_btn.pack(pady=(0, 20))

        history_win.resizable(False, False)
    
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
    cli_customer_id = _parse_customer_id(sys.argv[1:])
    customer_data = None

    if cli_customer_id:
        customer_data = _load_customer_from_db(cli_customer_id)

    if not customer_data:
        # Fallback sample profile for manual testing
        customer_data = {
            'customer_id': cli_customer_id or 1,
        'customer_code': 'CUST-20241201120000',
        'username': 'john.doe',
        'email': 'john.doe@email.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'customer_type': 'regular',
        'loyalty_points': 150,
        'total_spent': 250.75,
            'account_type': 'customer',
            'phone': '+63 912-345-6789',
            'address': '123 Coffee Street, Brew City',
    }
    
    class MockApp:
        def __init__(self, window):
            self.window = window

        def logout(self):
            try:
                clear_cart()
            except Exception:
                pass

            try:
                set_current_customer(None)
            except Exception:
                pass

            try:
                for widget in self.window.winfo_children():
                    widget.destroy()
            except Exception:
                pass

            try:
                self.window.destroy()
            except Exception:
                pass

            try:
                subprocess.Popen([sys.executable, "-m", "main"], cwd=str(PROJECT_ROOT))
            except Exception:
                pass

            try:
                sys.exit(0)
            except SystemExit:
                raise
            except Exception:
                pass
    
    root = tk.Tk()
    root.title("BigBrew Customer Home")
    root.geometry("1035x534")
    root.configure(bg="#FFFFFF")
    
    app = MockApp(root)
    customer_home = CustomerHome(root, customer_data, app)
    
    root.mainloop()
