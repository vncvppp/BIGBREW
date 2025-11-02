import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

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
        # Call the main app's logout method if it exists
        if hasattr(self.login_window, 'logout'):
            self.login_window.logout()
        else:
            # Fallback: show the login window
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
        user_card = self.create_card(controls_frame, "User Access Management", 0, 0)
        user_btn = tk.Button(
            user_card,
            text="Manage User Access",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.manage_users,
            height=2
        )
        user_btn.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Add access summary
        access_summary = tk.Label(
            user_card,
            text="View and manage user permissions\nand access controls",
            font=("Arial", 9),
            bg=self.card_bg,
            fg="#666666",
            justify='center'
        )
        access_summary.pack(pady=(0, 10))
        
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
        """Open user management window with access controls"""
        self.user_management_window = tk.Toplevel(self.window)
        self.user_management_window.title("User Access Management")
        self.user_management_window.geometry("1200x800")
        self.user_management_window.configure(bg=self.bg_color)
        
        # Center the window
        self.user_management_window.update_idletasks()
        width, height = 1200, 800
        screen_width = self.user_management_window.winfo_screenwidth()
        screen_height = self.user_management_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.user_management_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.user_management_window, bg=self.bg_color, height=60)
        header_frame.pack(fill='x', padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="User Access Management",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(side='left')
        
        # Main content area
        main_frame = tk.Frame(self.user_management_window, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - User list
        left_frame = tk.Frame(main_frame, bg=self.card_bg, relief='raised', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="Users",
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(pady=10)
        
        # User listbox with scrollbar
        list_frame = tk.Frame(left_frame, bg=self.card_bg)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.user_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 11),
            bg="white",
            fg="#4A3728",
            selectbackground=self.button_color,
            selectforeground="white"
        )
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.user_listbox.yview)
        self.user_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.user_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Populate user list (mock data for demonstration)
        self.populate_user_list()
        
        # Right panel - User details and permissions
        right_frame = tk.Frame(main_frame, bg=self.card_bg, relief='raised', bd=2)
        right_frame.pack(side='right', fill='both', expand=True)
        
        tk.Label(
            right_frame,
            text="User Access Details",
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(pady=10)
        
        # User details frame
        details_frame = tk.Frame(right_frame, bg=self.card_bg)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # User info
        self.user_info_frame = tk.Frame(details_frame, bg=self.card_bg)
        self.user_info_frame.pack(fill='x', pady=(0, 10))
        
        # Permissions frame
        permissions_frame = tk.LabelFrame(
            details_frame,
            text="Permissions",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        permissions_frame.pack(fill='both', expand=True)
        
        # Permission checkboxes
        self.permission_vars = {}
        permissions = [
            ("User Management", "user_mgmt"),
            ("System Settings", "system_settings"),
            ("Reports Access", "reports"),
            ("Database Tools", "database"),
            ("Staff Management", "staff_mgmt"),
            ("Sales Reports", "sales_reports"),
            ("Inventory Management", "inventory"),
            ("Schedule Management", "schedule"),
            ("Point of Sale", "pos"),
            ("Customer Management", "customer_mgmt"),
            ("Order Management", "order_mgmt"),
            ("Recipe Access", "recipe_access"),
            ("Time Tracking", "time_tracking"),
            ("Supplier Management", "supplier_mgmt"),
            ("Purchase Orders", "purchase_orders")
        ]
        
        for i, (permission_name, permission_key) in enumerate(permissions):
            var = tk.BooleanVar()
            self.permission_vars[permission_key] = var
            
            cb = tk.Checkbutton(
                permissions_frame,
                text=permission_name,
                variable=var,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728",
                activebackground=self.card_bg,
                command=self.update_permissions
            )
            cb.grid(row=i//2, column=i%2, sticky='w', padx=10, pady=2)
        
        # Action buttons
        button_frame = tk.Frame(details_frame, bg=self.card_bg)
        button_frame.pack(fill='x', pady=10)
        
        save_btn = tk.Button(
            button_frame,
            text="Save Changes",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.save_user_changes,
            width=15
        )
        save_btn.pack(side='left', padx=(0, 10))
        
        reset_btn = tk.Button(
            button_frame,
            text="Reset",
            font=("Arial", 12),
            bg="#6C757D",
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.reset_permissions,
            width=15
        )
        reset_btn.pack(side='left')
        
        # Bind selection event
        self.user_listbox.bind('<<ListboxSelect>>', self.on_user_select)
        
        # Load first user by default
        if self.user_listbox.size() > 0:
            self.user_listbox.selection_set(0)
            self.on_user_select(None)
    
    def populate_user_list(self):
        """Populate the user list with sample data"""
        # Mock user data - in a real application, this would come from a database
        self.users_data = {
            "admin": {
                "name": "John Admin",
                "email": "admin@bigbrew.com",
                "role": "Administrator",
                "status": "Active",
                "last_login": "2024-01-15 09:30:00",
                "permissions": ["user_mgmt", "system_settings", "reports", "database"]
            },
            "manager": {
                "name": "Sarah Manager",
                "email": "manager@bigbrew.com",
                "role": "Manager",
                "status": "Active",
                "last_login": "2024-01-15 08:45:00",
                "permissions": ["staff_mgmt", "sales_reports", "inventory", "schedule"]
            },
            "cashier": {
                "name": "Mike Cashier",
                "email": "cashier@bigbrew.com",
                "role": "Cashier",
                "status": "Active",
                "last_login": "2024-01-15 07:15:00",
                "permissions": ["pos", "customer_mgmt"]
            },
            "barista": {
                "name": "Emma Barista",
                "email": "barista@bigbrew.com",
                "role": "Barista",
                "status": "Active",
                "last_login": "2024-01-15 06:30:00",
                "permissions": ["order_mgmt", "recipe_access", "time_tracking"]
            },
            "inventory_manager": {
                "name": "David Inventory",
                "email": "inventory@bigbrew.com",
                "role": "Inventory Manager",
                "status": "Active",
                "last_login": "2024-01-14 16:20:00",
                "permissions": ["inventory", "supplier_mgmt", "purchase_orders"]
            }
        }
        
        # Clear existing items
        self.user_listbox.delete(0, tk.END)
        
        # Add users to listbox
        for user_id, user_data in self.users_data.items():
            display_text = f"{user_data['name']} ({user_data['role']})"
            self.user_listbox.insert(tk.END, display_text)
    
    def on_user_select(self, event):
        """Handle user selection from listbox"""
        selection = self.user_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        user_ids = list(self.users_data.keys())
        if index < len(user_ids):
            user_id = user_ids[index]
            self.current_user_id = user_id
            self.display_user_details(user_id)
    
    def display_user_details(self, user_id):
        """Display user details and permissions"""
        user_data = self.users_data[user_id]
        
        # Clear existing user info
        for widget in self.user_info_frame.winfo_children():
            widget.destroy()
        
        # Display user information
        info_labels = [
            ("Name:", user_data['name']),
            ("Email:", user_data['email']),
            ("Role:", user_data['role']),
            ("Status:", user_data['status']),
            ("Last Login:", user_data['last_login'])
        ]
        
        for i, (label_text, value_text) in enumerate(info_labels):
            label = tk.Label(
                self.user_info_frame,
                text=label_text,
                font=("Arial", 10, "bold"),
                bg=self.card_bg,
                fg="#4A3728"
            )
            label.grid(row=i, column=0, sticky='w', padx=(0, 10))
            
            value = tk.Label(
                self.user_info_frame,
                text=value_text,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728"
            )
            value.grid(row=i, column=1, sticky='w')
        
        # Update permission checkboxes
        self.update_permission_checkboxes(user_data['permissions'])
    
    def update_permission_checkboxes(self, permissions):
        """Update permission checkboxes based on user permissions"""
        for permission_key, var in self.permission_vars.items():
            var.set(permission_key in permissions)
    
    def update_permissions(self):
        """Handle permission checkbox changes"""
        # This method can be used to implement real-time permission updates
        pass
    
    def save_user_changes(self):
        """Save user permission changes"""
        if not hasattr(self, 'current_user_id'):
            messagebox.showwarning("No Selection", "Please select a user first")
            return
        
        # Get current permissions
        current_permissions = []
        for permission_key, var in self.permission_vars.items():
            if var.get():
                current_permissions.append(permission_key)
        
        # Update user data
        self.users_data[self.current_user_id]['permissions'] = current_permissions
        
        messagebox.showinfo("Success", f"Permissions updated for {self.users_data[self.current_user_id]['name']}")
        
        # Refresh the display
        self.display_user_details(self.current_user_id)
    
    def reset_permissions(self):
        """Reset permissions to default for selected user"""
        if not hasattr(self, 'current_user_id'):
            messagebox.showwarning("No Selection", "Please select a user first")
            return
        
        # Get default permissions based on role
        role_defaults = {
            'admin': ["user_mgmt", "system_settings", "reports", "database"],
            'manager': ["staff_mgmt", "sales_reports", "inventory", "schedule"],
            'cashier': ["pos", "customer_mgmt"],
            'barista': ["order_mgmt", "recipe_access", "time_tracking"],
            'inventory_manager': ["inventory", "supplier_mgmt", "purchase_orders"]
        }
        
        user_role = self.users_data[self.current_user_id]['role'].lower()
        if user_role in role_defaults:
            default_permissions = role_defaults[user_role]
            self.update_permission_checkboxes(default_permissions)
            messagebox.showinfo("Reset", f"Permissions reset to default for {user_role} role")
        
    def system_settings(self):
        messagebox.showinfo("System Settings", "System settings functionality will be implemented here")
        
    def view_reports(self):
        """Open the reports and analytics window"""
        from reports import ReportsAnalytics
        reports = ReportsAnalytics(self.window)
        
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
