import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class DashboardManager:
    def __init__(self, user_data, login_window):
        self.user_data = user_data
        self.login_window = login_window
        self.dashboard_window = None
        
    def show_dashboard(self):
        """Show the appropriate dashboard based on user role"""
        role = self.user_data['user_type']
        
        if role == 'admin':
            self.dashboard_window = AdminDashboard(self.user_data, self.login_window)
        elif role == 'manager':
            self.dashboard_window = ManagerDashboard(self.user_data, self.login_window)
        elif role == 'cashier':
            self.dashboard_window = CashierDashboard(self.user_data, self.login_window)
        elif role == 'barista':
            self.dashboard_window = BaristaDashboard(self.user_data, self.login_window)
        elif role == 'inventory_manager':
            self.dashboard_window = InventoryManagerDashboard(self.user_data, self.login_window)
        else:
            messagebox.showerror("Error", "Unknown user role")
            return
            
        self.dashboard_window.show()

class BaseDashboard:
    def __init__(self, user_data, login_window):
        self.user_data = user_data
        self.login_window = login_window
        self.window = tk.Toplevel()
        self.window.title(f"BigBrew - {self.get_role_title()}")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Color scheme
        self.bg_color = "#4A3728"
        self.accent_color = "#FFD700"
        self.card_bg = "#F5F5DC"
        self.text_color = "#FFFFFF"
        self.button_color = "#D2691E"
        
        self.window.configure(bg=self.bg_color)
        self.setup_ui()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def get_role_title(self):
        """Get formatted role title"""
        role_titles = {
            'admin': 'Administrator Dashboard',
            'manager': 'Manager Dashboard',
            'cashier': 'Cashier Dashboard',
            'barista': 'Barista Dashboard',
            'inventory_manager': 'Inventory Manager Dashboard'
        }
        return role_titles.get(self.user_data['user_type'], 'Dashboard')
        
    def setup_ui(self):
        """Setup the dashboard UI"""
        # Header
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Create dashboard header"""
        header_frame = tk.Frame(self.window, bg=self.bg_color, height=80)
        header_frame.pack(fill='x', padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg=self.bg_color)
        title_frame.pack(side='left', fill='y')
        
        logo_label = tk.Label(
            title_frame,
            text="☕ BIGBREW",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        logo_label.pack(anchor='w')
        
        role_label = tk.Label(
            title_frame,
            text=self.get_role_title(),
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.text_color
        )
        role_label.pack(anchor='w')
        
        # User info and logout
        user_frame = tk.Frame(header_frame, bg=self.bg_color)
        user_frame.pack(side='right', fill='y')
        
        user_info = f"{self.user_data['first_name']} {self.user_data['last_name']}"
        user_label = tk.Label(
            user_frame,
            text=f"Welcome, {user_info}",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.text_color
        )
        user_label.pack(anchor='e')
        
        logout_btn = tk.Button(
            user_frame,
            text="Logout",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.logout,
            width=10
        )
        logout_btn.pack(anchor='e', pady=(5, 0))
        
    def create_main_content(self):
        """Create main content area - to be overridden by subclasses"""
        content_frame = tk.Frame(self.window, bg=self.bg_color)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Default content
        default_label = tk.Label(
            content_frame,
            text="Dashboard content will be implemented based on role",
            font=("Arial", 16),
            bg=self.bg_color,
            fg=self.text_color
        )
        default_label.pack(expand=True)
        
    def create_footer(self):
        """Create dashboard footer"""
        footer_frame = tk.Frame(self.window, bg=self.bg_color, height=40)
        footer_frame.pack(fill='x', padx=20, pady=5)
        footer_frame.pack_propagate(False)
        
        # Last login info
        last_login = self.user_data.get('last_login', 'Never')
        if last_login and last_login != 'Never':
            try:
                last_login = last_login.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
                
        footer_label = tk.Label(
            footer_frame,
            text=f"Last login: {last_login} | BigBrew Coffee Management System",
            font=("Arial", 9),
            bg=self.bg_color,
            fg=self.accent_color
        )
        footer_label.pack(side='left')
        
    def logout(self):
        """Handle logout"""
        self.window.destroy()
        self.login_window.deiconify()
        
    def on_closing(self):
        """Handle window close"""
        self.logout()
        
    def show(self):
        """Show the dashboard window"""
        self.window.mainloop()

class AdminDashboard(BaseDashboard):
    def create_main_content(self):
        """Create admin-specific content"""
        content_frame = tk.Frame(self.window, bg=self.bg_color)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Admin controls grid
        controls_frame = tk.Frame(content_frame, bg=self.bg_color)
        controls_frame.pack(fill='both', expand=True)
        
        # User Management
        user_card = self.create_card(controls_frame, "User Management", 0, 0)
        user_btn = tk.Button(
            user_card,
            text="Manage Users",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.manage_users,
            height=2
        )
        user_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # System Settings
        settings_card = self.create_card(controls_frame, "System Settings", 0, 1)
        settings_btn = tk.Button(
            settings_card,
            text="System Settings",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.system_settings,
            height=2
        )
        settings_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Reports
        reports_card = self.create_card(controls_frame, "Reports & Analytics", 1, 0)
        reports_btn = tk.Button(
            reports_card,
            text="View Reports",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.view_reports,
            height=2
        )
        reports_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Database Management
        db_card = self.create_card(controls_frame, "Database Management", 1, 1)
        db_btn = tk.Button(
            db_card,
            text="Database Tools",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.database_tools,
            height=2
        )
        db_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
    def create_card(self, parent, title, row, col):
        """Create a dashboard card"""
        card = tk.Frame(parent, bg=self.card_bg, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        title_label = tk.Label(
            card,
            text=title,
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        title_label.pack(pady=(10, 5))
        
        return card
        
    def manage_users(self):
        messagebox.showinfo("User Management", "User management functionality will be implemented here")
        
    def system_settings(self):
        messagebox.showinfo("System Settings", "System settings functionality will be implemented here")
        
    def view_reports(self):
        messagebox.showinfo("Reports", "Reports and analytics functionality will be implemented here")
        
    def database_tools(self):
        messagebox.showinfo("Database Tools", "Database management tools will be implemented here")

class ManagerDashboard(BaseDashboard):
    def create_main_content(self):
        """Create manager-specific content"""
        content_frame = tk.Frame(self.window, bg=self.bg_color)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Manager controls
        controls_frame = tk.Frame(content_frame, bg=self.bg_color)
        controls_frame.pack(fill='both', expand=True)
        
        # Staff Management
        staff_card = self.create_card(controls_frame, "Staff Management", 0, 0)
        staff_btn = tk.Button(
            staff_card,
            text="Manage Staff",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.manage_staff,
            height=2
        )
        staff_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Sales Reports
        sales_card = self.create_card(controls_frame, "Sales Reports", 0, 1)
        sales_btn = tk.Button(
            sales_card,
            text="View Sales",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.view_sales,
            height=2
        )
        sales_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Inventory Overview
        inventory_card = self.create_card(controls_frame, "Inventory Overview", 1, 0)
        inventory_btn = tk.Button(
            inventory_card,
            text="Check Inventory",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.check_inventory,
            height=2
        )
        inventory_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Schedule Management
        schedule_card = self.create_card(controls_frame, "Schedule Management", 1, 1)
        schedule_btn = tk.Button(
            schedule_card,
            text="Manage Schedule",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.manage_schedule,
            height=2
        )
        schedule_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
    def create_card(self, parent, title, row, col):
        """Create a dashboard card"""
        card = tk.Frame(parent, bg=self.card_bg, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        title_label = tk.Label(
            card,
            text=title,
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        title_label.pack(pady=(10, 5))
        
        return card
        
    def manage_staff(self):
        messagebox.showinfo("Staff Management", "Staff management functionality will be implemented here")
        
    def view_sales(self):
        messagebox.showinfo("Sales Reports", "Sales reporting functionality will be implemented here")
        
    def check_inventory(self):
        messagebox.showinfo("Inventory", "Inventory overview functionality will be implemented here")
        
    def manage_schedule(self):
        messagebox.showinfo("Schedule", "Schedule management functionality will be implemented here")

class CashierDashboard(BaseDashboard):
    def create_main_content(self):
        """Create cashier-specific content"""
        content_frame = tk.Frame(self.window, bg=self.bg_color)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Cashier controls
        controls_frame = tk.Frame(content_frame, bg=self.bg_color)
        controls_frame.pack(fill='both', expand=True)
        
        # Point of Sale
        pos_card = self.create_card(controls_frame, "Point of Sale", 0, 0)
        pos_btn = tk.Button(
            pos_card,
            text="Open POS",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.open_pos,
            height=2
        )
        pos_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Daily Sales
        sales_card = self.create_card(controls_frame, "Daily Sales", 0, 1)
        sales_btn = tk.Button(
            sales_card,
            text="View Today's Sales",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.view_daily_sales,
            height=2
        )
        sales_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Customer Management
        customer_card = self.create_card(controls_frame, "Customer Management", 1, 0)
        customer_btn = tk.Button(
            customer_card,
            text="Manage Customers",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.manage_customers,
            height=2
        )
        customer_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Receipt History
        receipt_card = self.create_card(controls_frame, "Receipt History", 1, 1)
        receipt_btn = tk.Button(
            receipt_card,
            text="View Receipts",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.view_receipts,
            height=2
        )
        receipt_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
    def create_card(self, parent, title, row, col):
        """Create a dashboard card"""
        card = tk.Frame(parent, bg=self.card_bg, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        title_label = tk.Label(
            card,
            text=title,
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        title_label.pack(pady=(10, 5))
        
        return card
        
    def open_pos(self):
        messagebox.showinfo("Point of Sale", "POS system will be implemented here")
        
    def view_daily_sales(self):
        messagebox.showinfo("Daily Sales", "Daily sales reporting will be implemented here")
        
    def manage_customers(self):
        messagebox.showinfo("Customer Management", "Customer management will be implemented here")
        
    def view_receipts(self):
        messagebox.showinfo("Receipt History", "Receipt history will be implemented here")

class BaristaDashboard(BaseDashboard):
    def create_main_content(self):
        """Create barista-specific content"""
        content_frame = tk.Frame(self.window, bg=self.bg_color)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Barista controls
        controls_frame = tk.Frame(content_frame, bg=self.bg_color)
        controls_frame.pack(fill='both', expand=True)
        
        # Order Queue
        orders_card = self.create_card(controls_frame, "Order Queue", 0, 0)
        orders_btn = tk.Button(
            orders_card,
            text="View Orders",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.view_orders,
            height=2
        )
        orders_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Recipe Book
        recipe_card = self.create_card(controls_frame, "Recipe Book", 0, 1)
        recipe_btn = tk.Button(
            recipe_card,
            text="View Recipes",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.view_recipes,
            height=2
        )
        recipe_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Inventory Check
        inventory_card = self.create_card(controls_frame, "Inventory Check", 1, 0)
        inventory_btn = tk.Button(
            inventory_card,
            text="Check Ingredients",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.check_ingredients,
            height=2
        )
        inventory_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Time Tracking
        time_card = self.create_card(controls_frame, "Time Tracking", 1, 1)
        time_btn = tk.Button(
            time_card,
            text="Clock In/Out",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.time_tracking,
            height=2
        )
        time_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
    def create_card(self, parent, title, row, col):
        """Create a dashboard card"""
        card = tk.Frame(parent, bg=self.card_bg, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        title_label = tk.Label(
            card,
            text=title,
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        title_label.pack(pady=(10, 5))
        
        return card
        
    def view_orders(self):
        messagebox.showinfo("Order Queue", "Order management will be implemented here")
        
    def view_recipes(self):
        messagebox.showinfo("Recipe Book", "Recipe management will be implemented here")
        
    def check_ingredients(self):
        messagebox.showinfo("Inventory Check", "Ingredient inventory will be implemented here")
        
    def time_tracking(self):
        messagebox.showinfo("Time Tracking", "Time tracking will be implemented here")

class InventoryManagerDashboard(BaseDashboard):
    def create_main_content(self):
        """Create inventory manager-specific content"""
        content_frame = tk.Frame(self.window, bg=self.bg_color)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Inventory manager controls
        controls_frame = tk.Frame(content_frame, bg=self.bg_color)
        controls_frame.pack(fill='both', expand=True)
        
        # Inventory Management
        inventory_card = self.create_card(controls_frame, "Inventory Management", 0, 0)
        inventory_btn = tk.Button(
            inventory_card,
            text="Manage Inventory",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.manage_inventory,
            height=2
        )
        inventory_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Stock Alerts
        alerts_card = self.create_card(controls_frame, "Stock Alerts", 0, 1)
        alerts_btn = tk.Button(
            alerts_card,
            text="View Alerts",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.view_alerts,
            height=2
        )
        alerts_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Supplier Management
        supplier_card = self.create_card(controls_frame, "Supplier Management", 1, 0)
        supplier_btn = tk.Button(
            supplier_card,
            text="Manage Suppliers",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.manage_suppliers,
            height=2
        )
        supplier_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Purchase Orders
        orders_card = self.create_card(controls_frame, "Purchase Orders", 1, 1)
        orders_btn = tk.Button(
            orders_card,
            text="Manage Orders",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.manage_purchase_orders,
            height=2
        )
        orders_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
    def create_card(self, parent, title, row, col):
        """Create a dashboard card"""
        card = tk.Frame(parent, bg=self.card_bg, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        title_label = tk.Label(
            card,
            text=title,
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        title_label.pack(pady=(10, 5))
        
        return card
        
    def manage_inventory(self):
        messagebox.showinfo("Inventory Management", "Inventory management will be implemented here")
        
    def view_alerts(self):
        messagebox.showinfo("Stock Alerts", "Stock alert system will be implemented here")
        
    def manage_suppliers(self):
        messagebox.showinfo("Supplier Management", "Supplier management will be implemented here")
        
    def manage_purchase_orders(self):
        messagebox.showinfo("Purchase Orders", "Purchase order management will be implemented here")
