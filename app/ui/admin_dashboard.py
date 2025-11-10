import tkinter as tk
from tkinter import messagebox
from app.ui.admin_product_management import ProductManagementMixin
from app.ui.admin_inventory_management import InventoryManagementMixin
from app.ui.admin_sales_management import SalesManagementMixin

class DashboardFactory:
    def __init__(self, user_data, main_app):
        self.user_data = user_data
        self.main_app = main_app
        self.dashboard_window = None
        
    def show_dashboard(self):
        """Show the appropriate dashboard based on user role"""
        role = self.user_data['user_type']
        
        if role == 'admin':
            self.dashboard_window = AdminDashboard(self.user_data, self.main_app)
        elif role == 'manager':
            self.dashboard_window = ManagerDashboard(self.user_data, self.main_app)
        elif role == 'cashier':
            self.dashboard_window = CashierDashboard(self.user_data, self.main_app)
        elif role == 'barista':
            self.dashboard_window = BaristaDashboard(self.user_data, self.main_app)
        elif role == 'inventory_manager':
            self.dashboard_window = InventoryManagerDashboard(self.user_data, self.main_app)
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
        # Center the dashboard on screen
        try:
            self.window.update_idletasks()
            width, height = 1000, 700
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass
        
        # Hide the login window (main app root) when dashboard opens
        if hasattr(self.login_window, 'root'):
            try:
                self.login_window.root.withdraw()  # Hide the main window
            except Exception:
                pass
        
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
        # Show the login window (main app root) again
        if hasattr(self.login_window, 'root'):
            try:
                self.login_window.root.deiconify()  # Show the main window
            except Exception:
                pass
        # Call the main app's logout method if it exists
        if hasattr(self.login_window, 'logout'):
            self.login_window.logout()
        else:
            # Fallback: show the login window
            try:
                self.login_window.deiconify()
            except Exception:
                pass
        
    def on_closing(self):
        """Handle window close"""
        self.logout()
        
    def show(self):
        """Show the dashboard window"""
        self.window.mainloop()

class AdminDashboard(
    ProductManagementMixin,
    InventoryManagementMixin,
    SalesManagementMixin,
    BaseDashboard,
):
    def __init__(self, user_data, login_window):
        super().__init__(user_data, login_window)

    def create_main_content(self):
        """Create admin-specific content with CRUD operations"""
        content_frame = tk.Frame(self.window, bg=self.bg_color)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Admin controls grid
        controls_frame = tk.Frame(content_frame, bg=self.bg_color)
        controls_frame.pack(fill='both', expand=True)
        
        # Product Management (CRUD)
        product_card = self.create_card(controls_frame, "Product Management", 0, 0)
        product_btn = tk.Button(
            product_card,
            text="Manage Products",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.manage_products,
            height=2
        )
        product_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Add product summary
        product_summary = tk.Label(
            product_card,
            text="Add, Edit, Delete\nmilk tea flavors & menu items",
            font=("Arial", 9),
            bg=self.card_bg,
            fg="#666666",
            justify='center'
        )
        product_summary.pack(pady=(0, 10))
        
        # Inventory Management
        inventory_card = self.create_card(controls_frame, "Inventory Management", 0, 1)
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
        
        # Add inventory summary
        inventory_summary = tk.Label(
            inventory_card,
            text="Track and update\nremaining stock levels",
            font=("Arial", 9),
            bg=self.card_bg,
            fg="#666666",
            justify='center'
        )
        inventory_summary.pack(pady=(0, 10))
        
        # Sales Management
        sales_card = self.create_card(controls_frame, "Sales Management", 1, 0)
        sales_btn = tk.Button(
            sales_card,
            text="Manage Sales",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.manage_sales,
            height=2
        )
        sales_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Add sales summary
        sales_summary = tk.Label(
            sales_card,
            text="View, filter, and manage\nsales transactions",
            font=("Arial", 9),
            bg=self.card_bg,
            fg="#666666",
            justify='center'
        )
        sales_summary.pack(pady=(0, 10))
        
        # Reports & Analytics
        reports_card = self.create_card(controls_frame, "Reports & Analytics", 1, 1)
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
        
        # Add reports summary
        reports_summary = tk.Label(
            reports_card,
            text="Sales analytics, inventory\nreports, and insights",
            font=("Arial", 9),
            bg=self.card_bg,
            fg="#666666",
            justify='center'
        )
        reports_summary.pack(pady=(0, 10))
        
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
    
    # Sales management behavior provided by SalesManagementMixin.
    
    def view_reports(self):
        """Open reports and analytics window"""
        try:
            from app.ui.reports import ReportsAnalytics
            reports = ReportsAnalytics(self.window)
        except ImportError:
            messagebox.showerror("Error", "Reports module not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open reports: {e}")
        

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

    def manage_purchase_orders(self):
        messagebox.showinfo("Purchase Orders", "Purchase order management will be implemented here")
