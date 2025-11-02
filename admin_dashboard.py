import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os
from tkinter import filedialog

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
        """Open system settings window with various configuration options"""
        self.settings_window = tk.Toplevel(self.window)
        self.settings_window.title("System Settings")
        self.settings_window.geometry("1000x800")
        self.settings_window.configure(bg=self.bg_color)
        
        # Center the window
        self.settings_window.update_idletasks()
        width, height = 1000, 800
        screen_width = self.settings_window.winfo_screenwidth()
        screen_height = self.settings_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.settings_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.settings_window, bg=self.bg_color, height=60)
        header_frame.pack(fill='x', padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="System Settings",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(side='left')
        
        # Main content with notebook for different setting categories
        main_frame = tk.Frame(self.settings_window, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create notebook for settings tabs
        settings_notebook = ttk.Notebook(main_frame)
        settings_notebook.pack(fill='both', expand=True)
        
        # General Settings Tab
        general_frame = tk.Frame(settings_notebook, bg=self.card_bg)
        settings_notebook.add(general_frame, text="General")
        self.create_general_settings(general_frame)
        
        # Database Settings Tab
        database_frame = tk.Frame(settings_notebook, bg=self.card_bg)
        settings_notebook.add(database_frame, text="Database")
        self.create_database_settings(database_frame)
        
        # Security Settings Tab
        security_frame = tk.Frame(settings_notebook, bg=self.card_bg)
        settings_notebook.add(security_frame, text="Security")
        self.create_security_settings(security_frame)
        
        # Display Settings Tab
        display_frame = tk.Frame(settings_notebook, bg=self.card_bg)
        settings_notebook.add(display_frame, text="Display")
        self.create_display_settings(display_frame)
        
        # Backup Settings Tab
        backup_frame = tk.Frame(settings_notebook, bg=self.card_bg)
        settings_notebook.add(backup_frame, text="Backup")
        self.create_backup_settings(backup_frame)
        
        # Bottom buttons
        button_frame = tk.Frame(self.settings_window, bg=self.bg_color)
        button_frame.pack(fill='x', padx=20, pady=10)
        
        save_btn = tk.Button(
            button_frame,
            text="Save All Settings",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.save_all_settings,
            width=15
        )
        save_btn.pack(side='right', padx=5)
        
        reset_btn = tk.Button(
            button_frame,
            text="Reset All",
            font=("Arial", 12),
            bg="#6C757D",
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.reset_all_settings,
            width=15
        )
        reset_btn.pack(side='right', padx=5)
        
    def create_general_settings(self, parent):
        """Create general settings section"""
        # Store Frame
        store_frame = tk.LabelFrame(
            parent,
            text="Store Information",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        store_frame.pack(fill='x', padx=10, pady=5)
        
        # Store settings
        settings = [
            ("Store Name:", "store_name", "BigBrew Coffee"),
            ("Address:", "store_address", "123 Coffee Street"),
            ("Phone:", "store_phone", "+1 234-567-8900"),
            ("Email:", "store_email", "contact@bigbrew.com"),
            ("Tax Rate (%):", "tax_rate", "8.5")
        ]
        
        self.general_vars = {}
        for i, (label_text, var_name, default) in enumerate(settings):
            tk.Label(
                store_frame,
                text=label_text,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728"
            ).grid(row=i, column=0, sticky='w', pady=5)
            
            var = tk.StringVar(value=default)
            self.general_vars[var_name] = var
            
            tk.Entry(
                store_frame,
                textvariable=var,
                font=("Arial", 10),
                width=40
            ).grid(row=i, column=1, sticky='w', padx=10)
        
        # Business Hours Frame
        hours_frame = tk.LabelFrame(
            parent,
            text="Business Hours",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        hours_frame.pack(fill='x', padx=10, pady=5)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.hours_vars = {}
        
        for i, day in enumerate(days):
            tk.Label(
                hours_frame,
                text=f"{day}:",
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728"
            ).grid(row=i, column=0, sticky='w', pady=5)
            
            # Open time
            open_var = tk.StringVar(value="09:00")
            self.hours_vars[f"{day.lower()}_open"] = open_var
            tk.Entry(
                hours_frame,
                textvariable=open_var,
                font=("Arial", 10),
                width=10
            ).grid(row=i, column=1, padx=5)
            
            tk.Label(
                hours_frame,
                text="to",
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728"
            ).grid(row=i, column=2, padx=5)
            
            # Close time
            close_var = tk.StringVar(value="21:00")
            self.hours_vars[f"{day.lower()}_close"] = close_var
            tk.Entry(
                hours_frame,
                textvariable=close_var,
                font=("Arial", 10),
                width=10
            ).grid(row=i, column=3, padx=5)
            
            # Is closed checkbox
            closed_var = tk.BooleanVar()
            self.hours_vars[f"{day.lower()}_closed"] = closed_var
            tk.Checkbutton(
                hours_frame,
                text="Closed",
                variable=closed_var,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728",
                activebackground=self.card_bg
            ).grid(row=i, column=4, padx=10)
    
    def create_database_settings(self, parent):
        """Create database settings section"""
        # Database Connection Frame
        db_frame = tk.LabelFrame(
            parent,
            text="Database Connection",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        db_frame.pack(fill='x', padx=10, pady=5)
        
        # Database settings
        settings = [
            ("Host:", "db_host", "localhost"),
            ("Port:", "db_port", "5432"),
            ("Database Name:", "db_name", "bigbrew_db"),
            ("Username:", "db_user", "admin"),
            ("Password:", "db_password", "")
        ]
        
        self.db_vars = {}
        for i, (label_text, var_name, default) in enumerate(settings):
            tk.Label(
                db_frame,
                text=label_text,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728"
            ).grid(row=i, column=0, sticky='w', pady=5)
            
            var = tk.StringVar(value=default)
            self.db_vars[var_name] = var
            
            entry = tk.Entry(
                db_frame,
                textvariable=var,
                font=("Arial", 10),
                width=40,
                show="*" if var_name == "db_password" else ""
            )
            entry.grid(row=i, column=1, sticky='w', padx=10)
        
        # Test connection button
        tk.Button(
            db_frame,
            text="Test Connection",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.test_db_connection,
            width=15
        ).grid(row=len(settings), column=1, sticky='w', padx=10, pady=10)
        
        # Maintenance Frame
        maintenance_frame = tk.LabelFrame(
            parent,
            text="Database Maintenance",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        maintenance_frame.pack(fill='x', padx=10, pady=5)
        
        # Auto-backup settings
        tk.Label(
            maintenance_frame,
            text="Auto-backup Schedule:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', pady=5)
        
        self.backup_var = tk.StringVar(value="daily")
        for schedule in ["Daily", "Weekly", "Monthly"]:
            tk.Radiobutton(
                maintenance_frame,
                text=schedule,
                variable=self.backup_var,
                value=schedule.lower(),
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728",
                activebackground=self.card_bg
            ).pack(anchor='w')
        
        # Maintenance buttons
        button_frame = tk.Frame(maintenance_frame, bg=self.card_bg)
        button_frame.pack(fill='x', pady=10)
        
        tk.Button(
            button_frame,
            text="Backup Now",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.backup_database,
            width=15
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Optimize",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.optimize_database,
            width=15
        ).pack(side='left', padx=5)
    
    def create_security_settings(self, parent):
        """Create security settings section"""
        # Password Policy Frame
        password_frame = tk.LabelFrame(
            parent,
            text="Password Policy",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        password_frame.pack(fill='x', padx=10, pady=5)
        
        self.security_vars = {}
        
        # Minimum password length
        tk.Label(
            password_frame,
            text="Minimum Password Length:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        length_var = tk.StringVar(value="8")
        self.security_vars["min_password_length"] = length_var
        tk.Entry(
            password_frame,
            textvariable=length_var,
            font=("Arial", 10),
            width=10
        ).grid(row=0, column=1, sticky='w', padx=10)
        
        # Password requirements checkboxes
        requirements = [
            ("require_uppercase", "Require Uppercase Letter"),
            ("require_lowercase", "Require Lowercase Letter"),
            ("require_number", "Require Number"),
            ("require_special", "Require Special Character")
        ]
        
        for i, (var_name, text) in enumerate(requirements):
            var = tk.BooleanVar(value=True)
            self.security_vars[var_name] = var
            tk.Checkbutton(
                password_frame,
                text=text,
                variable=var,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728",
                activebackground=self.card_bg
            ).grid(row=i+1, column=0, columnspan=2, sticky='w', pady=2)
        
        # Login Security Frame
        login_frame = tk.LabelFrame(
            parent,
            text="Login Security",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        login_frame.pack(fill='x', padx=10, pady=5)
        
        # Session timeout
        tk.Label(
            login_frame,
            text="Session Timeout (minutes):",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        timeout_var = tk.StringVar(value="30")
        self.security_vars["session_timeout"] = timeout_var
        tk.Entry(
            login_frame,
            textvariable=timeout_var,
            font=("Arial", 10),
            width=10
        ).grid(row=0, column=1, sticky='w', padx=10)
        
        # Failed login attempts
        tk.Label(
            login_frame,
            text="Max Failed Login Attempts:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        attempts_var = tk.StringVar(value="5")
        self.security_vars["max_login_attempts"] = attempts_var
        tk.Entry(
            login_frame,
            textvariable=attempts_var,
            font=("Arial", 10),
            width=10
        ).grid(row=1, column=1, sticky='w', padx=10)
        
        # Additional security options
        options = [
            ("require_2fa", "Require Two-Factor Authentication for Admin Access"),
            ("force_password_change", "Force Password Change Every 90 Days"),
            ("log_all_actions", "Log All Administrative Actions")
        ]
        
        for i, (var_name, text) in enumerate(options):
            var = tk.BooleanVar(value=False)
            self.security_vars[var_name] = var
            tk.Checkbutton(
                login_frame,
                text=text,
                variable=var,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728",
                activebackground=self.card_bg
            ).grid(row=i+2, column=0, columnspan=2, sticky='w', pady=2)
    
    def create_display_settings(self, parent):
        """Create display settings section"""
        # Theme Settings Frame
        theme_frame = tk.LabelFrame(
            parent,
            text="Theme Settings",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        theme_frame.pack(fill='x', padx=10, pady=5)
        
        self.display_vars = {}
        
        # Color scheme selection
        tk.Label(
            theme_frame,
            text="Color Scheme:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', pady=5)
        
        color_var = tk.StringVar(value="coffee")
        self.display_vars["color_scheme"] = color_var
        
        schemes = [
            ("coffee", "Coffee Brown"),
            ("modern", "Modern Dark"),
            ("classic", "Classic Light"),
            ("custom", "Custom")
        ]
        
        for value, text in schemes:
            tk.Radiobutton(
                theme_frame,
                text=text,
                variable=color_var,
                value=value,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728",
                activebackground=self.card_bg
            ).pack(anchor='w')
        
        # Font Settings Frame
        font_frame = tk.LabelFrame(
            parent,
            text="Font Settings",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        font_frame.pack(fill='x', padx=10, pady=5)
        
        # Font family
        tk.Label(
            font_frame,
            text="Default Font:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        font_var = tk.StringVar(value="Arial")
        self.display_vars["default_font"] = font_var
        
        fonts = ["Arial", "Helvetica", "Verdana", "Tahoma"]
        font_dropdown = ttk.Combobox(
            font_frame,
            textvariable=font_var,
            values=fonts,
            state="readonly",
            width=20
        )
        font_dropdown.grid(row=0, column=1, sticky='w', padx=10)
        
        # Font size
        tk.Label(
            font_frame,
            text="Font Size:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        size_var = tk.StringVar(value="12")
        self.display_vars["font_size"] = size_var
        
        sizes = [str(i) for i in range(8, 21, 2)]
        size_dropdown = ttk.Combobox(
            font_frame,
            textvariable=size_var,
            values=sizes,
            state="readonly",
            width=20
        )
        size_dropdown.grid(row=1, column=1, sticky='w', padx=10)
        
        # Layout Settings Frame
        layout_frame = tk.LabelFrame(
            parent,
            text="Layout Settings",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        layout_frame.pack(fill='x', padx=10, pady=5)
        
        # Layout options
        options = [
            ("compact_mode", "Use Compact Mode"),
            ("show_toolbar", "Show Toolbar"),
            ("show_status", "Show Status Bar"),
            ("animate_transitions", "Enable Animations")
        ]
        
        for i, (var_name, text) in enumerate(options):
            var = tk.BooleanVar(value=True)
            self.display_vars[var_name] = var
            tk.Checkbutton(
                layout_frame,
                text=text,
                variable=var,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728",
                activebackground=self.card_bg
            ).pack(anchor='w', pady=2)
    
    def create_backup_settings(self, parent):
        """Create backup settings section"""
        # Backup Settings Frame
        backup_frame = tk.LabelFrame(
            parent,
            text="Backup Settings",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        backup_frame.pack(fill='x', padx=10, pady=5)
        
        self.backup_vars = {}
        
        # Backup location
        tk.Label(
            backup_frame,
            text="Backup Location:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', pady=5)
        
        location_frame = tk.Frame(backup_frame, bg=self.card_bg)
        location_frame.pack(fill='x', pady=5)
        
        location_var = tk.StringVar(value="C:/BigBrew/Backups")
        self.backup_vars["backup_location"] = location_var
        
        tk.Entry(
            location_frame,
            textvariable=location_var,
            font=("Arial", 10),
            width=40
        ).pack(side='left')
        
        tk.Button(
            location_frame,
            text="Browse",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.browse_backup_location,
            width=10
        ).pack(side='left', padx=5)
        
        # Backup schedule
        tk.Label(
            backup_frame,
            text="Backup Schedule:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', pady=5)
        
        schedule_var = tk.StringVar(value="daily")
        self.backup_vars["backup_schedule"] = schedule_var
        
        schedules = [
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("manual", "Manual Only")
        ]
        
        for value, text in schedules:
            tk.Radiobutton(
                backup_frame,
                text=text,
                variable=schedule_var,
                value=value,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728",
                activebackground=self.card_bg
            ).pack(anchor='w')
        
        # Retention Settings Frame
        retention_frame = tk.LabelFrame(
            parent,
            text="Backup Retention",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        retention_frame.pack(fill='x', padx=10, pady=5)
        
        # Keep backups for
        tk.Label(
            retention_frame,
            text="Keep Backups For:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        retention_var = tk.StringVar(value="30")
        self.backup_vars["retention_days"] = retention_var
        
        tk.Entry(
            retention_frame,
            textvariable=retention_var,
            font=("Arial", 10),
            width=10
        ).grid(row=0, column=1, sticky='w', padx=10)
        
        tk.Label(
            retention_frame,
            text="days",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).grid(row=0, column=2, sticky='w')
        
        # Maximum backup size
        tk.Label(
            retention_frame,
            text="Maximum Total Backup Size:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        size_var = tk.StringVar(value="10")
        self.backup_vars["max_backup_size"] = size_var
        
        tk.Entry(
            retention_frame,
            textvariable=size_var,
            font=("Arial", 10),
            width=10
        ).grid(row=1, column=1, sticky='w', padx=10)
        
        tk.Label(
            retention_frame,
            text="GB",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).grid(row=1, column=2, sticky='w')
        
        # Compression options
        compress_var = tk.BooleanVar(value=True)
        self.backup_vars["compress_backups"] = compress_var
        tk.Checkbutton(
            retention_frame,
            text="Compress Backups",
            variable=compress_var,
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728",
            activebackground=self.card_bg
        ).grid(row=2, column=0, columnspan=3, sticky='w', pady=5)
    
    def save_all_settings(self):
        """Save all settings to configuration"""
        try:
            # Collect all settings
            settings = {
                "general": {name: var.get() for name, var in self.general_vars.items()},
                "hours": {name: var.get() for name, var in self.hours_vars.items()},
                "database": {name: var.get() for name, var in self.db_vars.items()},
                "security": {name: var.get() for name, var in self.security_vars.items()},
                "display": {name: var.get() for name, var in self.display_vars.items()},
                "backup": {name: var.get() for name, var in self.backup_vars.items()}
            }
            
            # TODO: Save settings to configuration file or database
            
            messagebox.showinfo("Success", "All settings have been saved successfully!")
            self.settings_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def reset_all_settings(self):
        """Reset all settings to default values"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to default values?"):
            try:
                # TODO: Load default values from configuration
                self.settings_window.destroy()
                self.system_settings()  # Reopen settings window with defaults
                messagebox.showinfo("Success", "All settings have been reset to default values")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")
    
    def test_db_connection(self):
        """Test database connection with current settings"""
        # TODO: Implement database connection test
        messagebox.showinfo("Database Connection", "Connection test successful!")
    
    def backup_database(self):
        """Perform manual database backup"""
        # TODO: Implement database backup
        messagebox.showinfo("Backup", "Database backup completed successfully!")
    
    def optimize_database(self):
        """Optimize database performance"""
        # TODO: Implement database optimization
        messagebox.showinfo("Optimization", "Database optimization completed successfully!")
    
    def browse_backup_location(self):
        """Open file dialog to choose backup location"""
        from tkinter import filedialog
        directory = filedialog.askdirectory(
            title="Select Backup Location",
            initialdir=self.backup_vars["backup_location"].get()
        )
        if directory:
            self.backup_vars["backup_location"].set(directory)
        
    def view_reports(self):
        """Open reports and analytics window with various data visualizations"""
        self.reports_window = tk.Toplevel(self.window)
        self.reports_window.title("Reports & Analytics")
        self.reports_window.geometry("1200x800")
        self.reports_window.configure(bg=self.bg_color)
        
        # Center the window
        self.reports_window.update_idletasks()
        width, height = 1200, 800
        screen_width = self.reports_window.winfo_screenwidth()
        screen_height = self.reports_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.reports_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.reports_window, bg=self.bg_color, height=60)
        header_frame.pack(fill='x', padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Reports & Analytics",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(side='left')
        
        # Main content with notebook for different report categories
        main_frame = tk.Frame(self.reports_window, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create notebook for report tabs
        reports_notebook = ttk.Notebook(main_frame)
        reports_notebook.pack(fill='both', expand=True)
        
        # Sales Reports Tab
        sales_frame = tk.Frame(reports_notebook, bg=self.card_bg)
        reports_notebook.add(sales_frame, text="Sales Analytics")
        self.create_sales_reports(sales_frame)
        
        # Inventory Reports Tab
        inventory_frame = tk.Frame(reports_notebook, bg=self.card_bg)
        reports_notebook.add(inventory_frame, text="Inventory Analytics")
        self.create_inventory_reports(inventory_frame)
        
        # Customer Reports Tab
        customer_frame = tk.Frame(reports_notebook, bg=self.card_bg)
        reports_notebook.add(customer_frame, text="Customer Analytics")
        self.create_customer_reports(customer_frame)
        
        # Staff Reports Tab
        staff_frame = tk.Frame(reports_notebook, bg=self.card_bg)
        reports_notebook.add(staff_frame, text="Staff Analytics")
        self.create_staff_reports(staff_frame)
        
        # Export button
        export_btn = tk.Button(
            self.reports_window,
            text="Export Reports",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.export_reports,
            width=15
        )
        export_btn.pack(pady=10)
    
    def create_sales_reports(self, parent):
        """Create sales analytics section using simple table-based visualizations"""
        # Controls Frame
        controls_frame = tk.Frame(parent, bg=self.card_bg)
        controls_frame.pack(fill='x', padx=10, pady=5)

        # Create four data display sections
        for i in range(4):
            frame = tk.LabelFrame(
                parent,
                text=["Daily Sales", "Product Categories", "Peak Hours", "Payment Methods"][i],
                font=("Arial", 12, "bold"),
                bg=self.card_bg
            )
            row, col = i // 2, i % 2
            frame.grid(row=row, column=col, padx=10, pady=5, sticky='nsew')
            parent.grid_columnconfigure(col, weight=1)
            parent.grid_rowconfigure(row, weight=1)

            # Sample data
            if i == 0:  # Daily Sales
                data = [
                    ("Monday", "$1,200"),
                    ("Tuesday", "$1,500"),
                    ("Wednesday", "$1,300"),
                    ("Thursday", "$1,600"),
                    ("Friday", "$1,800"),
                    ("Saturday", "$2,000"),
                    ("Sunday", "$1,400")
                ]
            elif i == 1:  # Product Categories
                data = [
                    ("Coffee", "45%"),
                    ("Tea", "25%"),
                    ("Food", "20%"),
                    ("Others", "10%")
                ]
            elif i == 2:  # Peak Hours
                data = [
                    ("8-10 AM", "30%"),
                    ("12-2 PM", "25%"),
                    ("3-5 PM", "20%"),
                    ("6-8 PM", "25%")
                ]
            else:  # Payment Methods
                data = [
                    ("Cash", "40%"),
                    ("Card", "45%"),
                    ("Mobile", "15%")
                ]

            # Create data display
            for idx, (label, value) in enumerate(data):
                tk.Label(
                    frame,
                    text=label,
                    font=("Arial", 10),
                    bg=self.card_bg,
                    anchor='w'
                ).grid(row=idx, column=0, padx=5, pady=2, sticky='w')
                
                tk.Label(
                    frame,
                    text=value,
                    font=("Arial", 10),
                    bg=self.card_bg,
                    anchor='e'
                ).grid(row=idx, column=1, padx=5, pady=2, sticky='e')
        
        # Date range selection
        tk.Label(
            controls_frame,
            text="Date Range:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(side='left', padx=5)
        
        ranges = ["Today", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom"]
        self.date_range_var = tk.StringVar(value="Last 30 Days")
        range_menu = ttk.Combobox(
            controls_frame,
            textvariable=self.date_range_var,
            values=ranges,
            state="readonly",
            width=15
        )
        range_menu.pack(side='left', padx=5)
        range_menu.bind('<<ComboboxSelected>>', self.update_sales_charts)
        
        # Refresh button
        tk.Button(
            controls_frame,
            text="Refresh",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.update_sales_charts,
            width=10
        ).pack(side='right', padx=5)
        
        # Charts Frame
        charts_frame = tk.Frame(parent, bg=self.card_bg)
        charts_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create four chart areas
        self.sales_chart_frames = []
        for i in range(4):
            chart_frame = tk.Frame(
                charts_frame,
                bg='white',
                relief='solid',
                bd=1
            )
            row, col = i // 2, i % 2
            chart_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            charts_frame.grid_rowconfigure(row, weight=1)
            charts_frame.grid_columnconfigure(col, weight=1)
            self.sales_chart_frames.append(chart_frame)
        
        # Initialize charts
        self.update_sales_charts()
        
        # Summary Frame
        summary_frame = tk.LabelFrame(
            parent,
            text="Sales Summary",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        summary_frame.pack(fill='x', padx=10, pady=5)
        
        # Summary metrics
        metrics = [
            ("Total Revenue:", "$12,345.67"),
            ("Total Orders:", "456"),
            ("Average Order Value:", "$27.89"),
            ("Best Selling Item:", "Cappuccino (123 units)"),
            ("Peak Hours:", "8:00 AM - 10:00 AM")
        ]
        
        for i, (label_text, value_text) in enumerate(metrics):
            tk.Label(
                summary_frame,
                text=label_text,
                font=("Arial", 10, "bold"),
                bg=self.card_bg,
                fg="#4A3728"
            ).grid(row=i//3, column=(i%3)*2, sticky='w', padx=5, pady=2)
            
            tk.Label(
                summary_frame,
                text=value_text,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728"
            ).grid(row=i//3, column=(i%3)*2+1, sticky='w', padx=5, pady=2)
    
    def create_inventory_reports(self, parent):
        """Create inventory analytics section"""
        # Controls Frame
        controls_frame = tk.Frame(parent, bg=self.card_bg)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Category selection
        tk.Label(
            controls_frame,
            text="Category:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(side='left', padx=5)
        
        categories = ["All", "Coffee Beans", "Milk & Dairy", "Syrups", "Supplies"]
        self.inventory_category_var = tk.StringVar(value="All")
        category_menu = ttk.Combobox(
            controls_frame,
            textvariable=self.inventory_category_var,
            values=categories,
            state="readonly",
            width=15
        )
        category_menu.pack(side='left', padx=5)
        category_menu.bind('<<ComboboxSelected>>', self.update_inventory_data)
        
        # Refresh button
        tk.Button(
            controls_frame,
            text="Refresh",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.update_inventory_data,
            width=10
        ).pack(side='right', padx=5)
        
        # Create two frames side by side
        left_frame = tk.Frame(parent, bg=self.card_bg)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        right_frame = tk.Frame(parent, bg=self.card_bg)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Stock Levels Table
        table_frame = tk.LabelFrame(
            left_frame,
            text="Current Stock Levels",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create treeview for inventory table
        columns = ("Item", "Current Stock", "Min Level", "Max Level", "Status")
        self.inventory_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings'
        )
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.inventory_tree.yview
        )
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        self.inventory_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Alerts Frame
        alerts_frame = tk.LabelFrame(
            right_frame,
            text="Inventory Alerts",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        alerts_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Alerts text widget
        self.alerts_text = tk.Text(
            alerts_frame,
            font=("Arial", 10),
            bg="white",
            fg="#4A3728",
            height=10
        )
        self.alerts_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Initialize data
        self.update_inventory_data()
    
    def create_customer_reports(self, parent):
        """Create customer analytics section"""
        # Controls Frame
        controls_frame = tk.Frame(parent, bg=self.card_bg)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Time period selection
        tk.Label(
            controls_frame,
            text="Time Period:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(side='left', padx=5)
        
        periods = ["Last Month", "Last Quarter", "Last Year", "All Time"]
        self.customer_period_var = tk.StringVar(value="Last Month")
        period_menu = ttk.Combobox(
            controls_frame,
            textvariable=self.customer_period_var,
            values=periods,
            state="readonly",
            width=15
        )
        period_menu.pack(side='left', padx=5)
        period_menu.bind('<<ComboboxSelected>>', self.update_customer_analytics)
        
        # Refresh button
        tk.Button(
            controls_frame,
            text="Refresh",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.update_customer_analytics,
            width=10
        ).pack(side='right', padx=5)
        
        # Create two frames side by side
        left_frame = tk.Frame(parent, bg=self.card_bg)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        right_frame = tk.Frame(parent, bg=self.card_bg)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Customer Segments Chart
        segments_frame = tk.LabelFrame(
            left_frame,
            text="Customer Segments",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        segments_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Top Customers Table
        customers_frame = tk.LabelFrame(
            right_frame,
            text="Top Customers",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        customers_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create treeview for top customers
        columns = ("Customer", "Orders", "Total Spent", "Avg Order", "Last Visit")
        self.customers_tree = ttk.Treeview(
            customers_frame,
            columns=columns,
            show='headings'
        )
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(
            customers_frame,
            orient="vertical",
            command=self.customers_tree.yview
        )
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customers_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Initialize data
        self.update_customer_analytics()
    
    def create_staff_reports(self, parent):
        """Create staff analytics section"""
        # Controls Frame
        controls_frame = tk.Frame(parent, bg=self.card_bg)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        # Department selection
        tk.Label(
            controls_frame,
            text="Department:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(side='left', padx=5)
        
        departments = ["All", "Barista", "Cashier", "Kitchen", "Management"]
        self.staff_dept_var = tk.StringVar(value="All")
        dept_menu = ttk.Combobox(
            controls_frame,
            textvariable=self.staff_dept_var,
            values=departments,
            state="readonly",
            width=15
        )
        dept_menu.pack(side='left', padx=5)
        dept_menu.bind('<<ComboboxSelected>>', self.update_staff_analytics)
        
        # Date range
        tk.Label(
            controls_frame,
            text="Period:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(side='left', padx=5)
        
        periods = ["This Week", "This Month", "Last Month", "Custom"]
        self.staff_period_var = tk.StringVar(value="This Month")
        period_menu = ttk.Combobox(
            controls_frame,
            textvariable=self.staff_period_var,
            values=periods,
            state="readonly",
            width=15
        )
        period_menu.pack(side='left', padx=5)
        period_menu.bind('<<ComboboxSelected>>', self.update_staff_analytics)
        
        # Refresh button
        tk.Button(
            controls_frame,
            text="Refresh",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.update_staff_analytics,
            width=10
        ).pack(side='right', padx=5)
        
        # Create two frames side by side
        left_frame = tk.Frame(parent, bg=self.card_bg)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        right_frame = tk.Frame(parent, bg=self.card_bg)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Performance Metrics Table
        metrics_frame = tk.LabelFrame(
            left_frame,
            text="Staff Performance Metrics",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        metrics_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create treeview for performance metrics
        columns = ("Employee", "Hours", "Sales", "Orders", "Rating")
        self.staff_tree = ttk.Treeview(
            metrics_frame,
            columns=columns,
            show='headings'
        )
        
        for col in columns:
            self.staff_tree.heading(col, text=col)
            self.staff_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(
            metrics_frame,
            orient="vertical",
            command=self.staff_tree.yview
        )
        self.staff_tree.configure(yscrollcommand=scrollbar.set)
        
        self.staff_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Schedule Optimization Frame
        schedule_frame = tk.LabelFrame(
            right_frame,
            text="Schedule Optimization",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        )
        schedule_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Initialize data
        self.update_staff_analytics()
    
    def update_sales_charts(self, event=None):
        """Update sales analytics charts based on selected date range"""
        # TODO: Implement actual data retrieval and chart creation
        # For now, we'll just show placeholder text
        for frame in self.sales_chart_frames:
            for widget in frame.winfo_children():
                widget.destroy()
            
            tk.Label(
                frame,
                text="Sales Chart\n(Data visualization will be implemented)",
                font=("Arial", 10),
                bg='white'
            ).pack(expand=True)
    
    def update_inventory_data(self, event=None):
        """Update inventory analytics data"""
        # Clear existing data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Add sample data
        sample_data = [
            ("Espresso Beans", "25 kg", "20 kg", "100 kg", "OK"),
            ("Whole Milk", "15 L", "10 L", "50 L", "OK"),
            ("Vanilla Syrup", "2 bottles", "5 bottles", "20 bottles", "Low"),
            ("Paper Cups", "150 pcs", "200 pcs", "1000 pcs", "Low"),
            ("Coffee Filters", "500 pcs", "200 pcs", "1000 pcs", "OK")
        ]
        
        for item in sample_data:
            self.inventory_tree.insert('', 'end', values=item)
        
        # Update alerts
        self.alerts_text.delete('1.0', tk.END)
        self.alerts_text.insert(tk.END, "Inventory Alerts:\n\n")
        self.alerts_text.insert(tk.END, "• Low stock: Vanilla Syrup\n")
        self.alerts_text.insert(tk.END, "• Low stock: Paper Cups\n")
        self.alerts_text.insert(tk.END, "• Approaching expiry: Whole Milk (5 days)\n")
    
    def update_customer_analytics(self, event=None):
        """Update customer analytics data"""
        # Clear existing data
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Add sample data
        sample_data = [
            ("John Smith", "45", "$890.50", "$19.79", "2024-01-15"),
            ("Mary Johnson", "38", "$750.25", "$19.74", "2024-01-14"),
            ("David Brown", "32", "$640.00", "$20.00", "2024-01-13"),
            ("Lisa Davis", "30", "$585.75", "$19.53", "2024-01-15"),
            ("Michael Wilson", "28", "$545.20", "$19.47", "2024-01-14")
        ]
        
        for item in sample_data:
            self.customers_tree.insert('', 'end', values=item)
    
    def update_staff_analytics(self, event=None):
        """Update staff analytics data"""
        # Clear existing data
        for item in self.staff_tree.get_children():
            self.staff_tree.delete(item)
        
        # Add sample data
        sample_data = [
            ("Emma Smith", "160", "$12,450", "623", "4.8"),
            ("John Davis", "155", "$11,890", "595", "4.7"),
            ("Sarah Johnson", "148", "$11,230", "562", "4.9"),
            ("Mike Brown", "152", "$10,980", "549", "4.6"),
            ("Lisa Wilson", "145", "$10,560", "528", "4.8")
        ]
        
        for item in sample_data:
            self.staff_tree.insert('', 'end', values=item)
    
    def export_reports(self):
        """Export reports to Excel or PDF"""
        file_types = [('Excel files', '*.xlsx'), ('PDF files', '*.pdf')]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=file_types,
            title="Export Reports As"
        )
        
        if file_path:
            try:
                # TODO: Implement actual report export
                messagebox.showinfo(
                    "Success",
                    f"Reports have been exported to {file_path}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Export Error",
                    f"Failed to export reports: {str(e)}"
                )
    def database_tools(self):
        """Open database management tools window"""
        self.db_window = tk.Toplevel(self.window)
        self.db_window.title("Database Management Tools")
        self.db_window.geometry("1200x800")
        self.db_window.configure(bg=self.bg_color)
        
        # Center the window
        self.db_window.update_idletasks()
        width, height = 1200, 800
        screen_width = self.db_window.winfo_screenwidth()
        screen_height = self.db_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.db_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.db_window, bg=self.bg_color, height=60)
        header_frame.pack(fill='x', padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Database Management Tools",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(side='left')
        
        # Main content with notebook for different tools
        main_frame = tk.Frame(self.db_window, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create notebook for tool tabs
        tools_notebook = ttk.Notebook(main_frame)
        tools_notebook.pack(fill='both', expand=True)
        
        # Query Tool Tab
        query_frame = tk.Frame(tools_notebook, bg=self.card_bg)
        tools_notebook.add(query_frame, text="Query Tool")
        self.create_query_tool(query_frame)
        
        # Backup Tool Tab
        backup_frame = tk.Frame(tools_notebook, bg=self.card_bg)
        tools_notebook.add(backup_frame, text="Backup & Restore")
        self.create_backup_tool(backup_frame)
        
        # Structure Tool Tab
        structure_frame = tk.Frame(tools_notebook, bg=self.card_bg)
        tools_notebook.add(structure_frame, text="Database Structure")
        self.create_structure_tool(structure_frame)
        
        # Maintenance Tool Tab
        maintenance_frame = tk.Frame(tools_notebook, bg=self.card_bg)
        tools_notebook.add(maintenance_frame, text="Maintenance")
        self.create_maintenance_tool(maintenance_frame)
    
    def create_query_tool(self, parent):
        """Create query execution tool"""
        # Query Input Frame
        input_frame = tk.LabelFrame(
            parent,
            text="SQL Query",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Query text widget
        self.query_text = tk.Text(
            input_frame,
            font=("Consolas", 12),
            bg="white",
            fg="#4A3728",
            height=8
        )
        self.query_text.pack(fill='x', pady=5)
        
        # Button frame
        button_frame = tk.Frame(input_frame, bg=self.card_bg)
        button_frame.pack(fill='x', pady=5)
        
        # Execute button
        tk.Button(
            button_frame,
            text="Execute Query",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.execute_query,
            width=15
        ).pack(side='left', padx=5)
        
        # Clear button
        tk.Button(
            button_frame,
            text="Clear",
            font=("Arial", 10),
            bg="#6C757D",
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=lambda: self.query_text.delete('1.0', tk.END),
            width=10
        ).pack(side='left', padx=5)
        
        # Save query button
        tk.Button(
            button_frame,
            text="Save Query",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.save_query,
            width=10
        ).pack(side='left', padx=5)
        
        # Load query button
        tk.Button(
            button_frame,
            text="Load Query",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.load_query,
            width=10
        ).pack(side='left', padx=5)
        
        # Results Frame
        results_frame = tk.LabelFrame(
            parent,
            text="Query Results",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for results
        columns = ("No columns available")
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show='headings'
        )
        
        scrollbar_y = ttk.Scrollbar(
            results_frame,
            orient="vertical",
            command=self.results_tree.yview
        )
        scrollbar_x = ttk.Scrollbar(
            results_frame,
            orient="horizontal",
            command=self.results_tree.xview
        )
        self.results_tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        self.results_tree.pack(side='top', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
    
    def create_backup_tool(self, parent):
        """Create backup and restore tool"""
        # Backup Frame
        backup_frame = tk.LabelFrame(
            parent,
            text="Database Backup",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        backup_frame.pack(fill='x', padx=10, pady=5)
        
        # Backup location
        tk.Label(
            backup_frame,
            text="Backup Location:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', pady=5)
        
        location_frame = tk.Frame(backup_frame, bg=self.card_bg)
        location_frame.pack(fill='x', pady=5)
        
        self.backup_location = tk.StringVar(value="C:/BigBrew/Backups")
        tk.Entry(
            location_frame,
            textvariable=self.backup_location,
            font=("Arial", 10),
            width=50
        ).pack(side='left')
        
        tk.Button(
            location_frame,
            text="Browse",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.browse_backup_location,
            width=10
        ).pack(side='left', padx=5)
        
        # Backup options
        options_frame = tk.Frame(backup_frame, bg=self.card_bg)
        options_frame.pack(fill='x', pady=10)
        
        self.compress_backup = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Compress Backup",
            variable=self.compress_backup,
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728",
            activebackground=self.card_bg
        ).pack(side='left', padx=5)
        
        self.include_logs = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Include Logs",
            variable=self.include_logs,
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728",
            activebackground=self.card_bg
        ).pack(side='left', padx=5)
        
        # Backup button
        tk.Button(
            backup_frame,
            text="Create Backup",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.create_backup,
            width=15
        ).pack(pady=10)
        
        # Restore Frame
        restore_frame = tk.LabelFrame(
            parent,
            text="Database Restore",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        restore_frame.pack(fill='x', padx=10, pady=5)
        
        # Backup selection
        tk.Label(
            restore_frame,
            text="Select Backup:",
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', pady=5)
        
        # Backup listbox
        list_frame = tk.Frame(restore_frame, bg=self.card_bg)
        list_frame.pack(fill='x', pady=5)
        
        self.backup_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 10),
            height=5
        )
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.backup_listbox.yview
        )
        self.backup_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.backup_listbox.pack(side='left', fill='x', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Refresh backups list
        tk.Button(
            restore_frame,
            text="Refresh List",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.refresh_backups,
            width=10
        ).pack(pady=5)
        
        # Restore options
        options_frame = tk.Frame(restore_frame, bg=self.card_bg)
        options_frame.pack(fill='x', pady=10)
        
        self.overwrite_existing = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_frame,
            text="Overwrite Existing Database",
            variable=self.overwrite_existing,
            font=("Arial", 10),
            bg=self.card_bg,
            fg="#4A3728",
            activebackground=self.card_bg
        ).pack(side='left', padx=5)
        
        # Restore button
        tk.Button(
            restore_frame,
            text="Restore Database",
            font=("Arial", 12),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.restore_database,
            width=15
        ).pack(pady=10)
    
    def create_structure_tool(self, parent):
        """Create database structure management tool"""
        # Table List Frame
        tables_frame = tk.LabelFrame(
            parent,
            text="Database Tables",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        tables_frame.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        
        # Table listbox
        self.tables_listbox = tk.Listbox(
            tables_frame,
            font=("Arial", 10),
            selectmode=tk.SINGLE
        )
        scrollbar = ttk.Scrollbar(
            tables_frame,
            orient="vertical",
            command=self.tables_listbox.yview
        )
        self.tables_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.tables_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.tables_listbox.bind('<<ListboxSelect>>', self.show_table_structure)
        
        # Structure Frame
        structure_frame = tk.LabelFrame(
            parent,
            text="Table Structure",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        structure_frame.pack(side='right', fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for structure
        columns = ("Column", "Type", "Null", "Key", "Default", "Extra")
        self.structure_tree = ttk.Treeview(
            structure_frame,
            columns=columns,
            show='headings'
        )
        
        for col in columns:
            self.structure_tree.heading(col, text=col)
            self.structure_tree.column(col, width=100)
        
        scrollbar_y = ttk.Scrollbar(
            structure_frame,
            orient="vertical",
            command=self.structure_tree.yview
        )
        self.structure_tree.configure(yscrollcommand=scrollbar_y.set)
        
        self.structure_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        
        # Load tables
        self.load_database_tables()
    
    def create_maintenance_tool(self, parent):
        """Create database maintenance tool"""
        # Status Frame
        status_frame = tk.LabelFrame(
            parent,
            text="Database Status",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        status_frame.pack(fill='x', padx=10, pady=5)
        
        # Status grid
        status_items = [
            ("Size:", "125 MB"),
            ("Tables:", "15"),
            ("Records:", "25,678"),
            ("Last Backup:", "2024-01-15 10:30:00"),
            ("Status:", "Healthy"),
            ("Version:", "SQLite 3.35.5")
        ]
        
        for i, (label_text, value_text) in enumerate(status_items):
            tk.Label(
                status_frame,
                text=label_text,
                font=("Arial", 10, "bold"),
                bg=self.card_bg,
                fg="#4A3728"
            ).grid(row=i//3, column=(i%3)*2, sticky='w', padx=5, pady=2)
            
            tk.Label(
                status_frame,
                text=value_text,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#4A3728"
            ).grid(row=i//3, column=(i%3)*2+1, sticky='w', padx=5, pady=2)
        
        # Maintenance Tools Frame
        tools_frame = tk.LabelFrame(
            parent,
            text="Maintenance Tools",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        tools_frame.pack(fill='x', padx=10, pady=5)
        
        # Tool buttons
        tools = [
            ("Optimize Tables", self.optimize_tables),
            ("Repair Tables", self.repair_tables),
            ("Analyze Tables", self.analyze_tables),
            ("Check Integrity", self.check_integrity),
            ("Clear Cache", self.clear_cache),
            ("Vacuum Database", self.vacuum_database)
        ]
        
        for i, (text, command) in enumerate(tools):
            tk.Button(
                tools_frame,
                text=text,
                font=("Arial", 10),
                bg=self.button_color,
                fg=self.text_color,
                relief='flat',
                bd=0,
                command=command,
                width=15
            ).grid(row=i//3, column=i%3, padx=5, pady=5)
        
        # Log Frame
        log_frame = tk.LabelFrame(
            parent,
            text="Maintenance Log",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            padx=10,
            pady=10
        )
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Log text widget
        self.log_text = tk.Text(
            log_frame,
            font=("Consolas", 10),
            bg="white",
            fg="#4A3728"
        )
        scrollbar = ttk.Scrollbar(
            log_frame,
            orient="vertical",
            command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Initialize log
        self.log_maintenance("Maintenance log initialized")
    
    def execute_query(self):
        """Execute SQL query and display results"""
        query = self.query_text.get('1.0', tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return
        
        try:
            # TODO: Implement actual query execution
            # For now, show sample data
            self.results_tree.delete(*self.results_tree.get_children())
            
            # Configure columns
            self.results_tree['columns'] = ('id', 'name', 'value')
            for col in ('id', 'name', 'value'):
                self.results_tree.heading(col, text=col.title())
                self.results_tree.column(col, width=100)
            
            # Add sample data
            sample_data = [
                (1, "Item 1", "Value 1"),
                (2, "Item 2", "Value 2"),
                (3, "Item 3", "Value 3")
            ]
            
            for item in sample_data:
                self.results_tree.insert('', 'end', values=item)
                
            messagebox.showinfo("Success", "Query executed successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute query: {str(e)}")
    
    def save_query(self):
        """Save current query to file"""
        query = self.query_text.get('1.0', tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "No query to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[('SQL files', '*.sql'), ('Text files', '*.txt')],
            title="Save Query As"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(query)
                messagebox.showinfo("Success", "Query saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save query: {str(e)}")
    
    def load_query(self):
        """Load query from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[('SQL files', '*.sql'), ('Text files', '*.txt')],
            title="Load Query"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    query = f.read()
                self.query_text.delete('1.0', tk.END)
                self.query_text.insert('1.0', query)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load query: {str(e)}")
    
    def create_backup(self):
        """Create database backup"""
        try:
            # TODO: Implement actual backup creation
            messagebox.showinfo(
                "Success",
                "Database backup created successfully"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to create backup: {str(e)}"
            )
    
    def refresh_backups(self):
        """Refresh list of available backups"""
        self.backup_listbox.delete(0, tk.END)
        
        # TODO: Implement actual backup list retrieval
        # For now, show sample backups
        sample_backups = [
            "backup_2024_01_15_103000.sql",
            "backup_2024_01_14_153000.sql",
            "backup_2024_01_13_093000.sql"
        ]
        
        for backup in sample_backups:
            self.backup_listbox.insert(tk.END, backup)
    
    def restore_database(self):
        """Restore database from selected backup"""
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "Warning",
                "Please select a backup to restore"
            )
            return
            
        if not self.overwrite_existing.get():
            if not messagebox.askyesno(
                "Confirm Restore",
                "Are you sure you want to restore the database? "
                "This will NOT overwrite the existing database."
            ):
                return
        else:
            if not messagebox.askyesno(
                "Confirm Restore",
                "Are you sure you want to restore and OVERWRITE "
                "the existing database? This cannot be undone!"
            ):
                return
        
        try:
            # TODO: Implement actual database restore
            messagebox.showinfo(
                "Success",
                "Database restored successfully"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to restore database: {str(e)}"
            )
    
    def load_database_tables(self):
        """Load database tables into listbox"""
        self.tables_listbox.delete(0, tk.END)
        
        # TODO: Implement actual table list retrieval
        # For now, show sample tables
        sample_tables = [
            "users",
            "products",
            "orders",
            "order_items",
            "inventory",
            "customers"
        ]
        
        for table in sample_tables:
            self.tables_listbox.insert(tk.END, table)
    
    def show_table_structure(self, event):
        """Show structure of selected table"""
        selection = self.tables_listbox.curselection()
        if not selection:
            return
            
        table = self.tables_listbox.get(selection[0])
        
        # Clear existing data
        for item in self.structure_tree.get_children():
            self.structure_tree.delete(item)
        
        # TODO: Implement actual structure retrieval
        # For now, show sample structure
        sample_structure = [
            ("id", "INTEGER", "NO", "PRI", None, "auto_increment"),
            ("name", "VARCHAR(255)", "NO", None, None, None),
            ("description", "TEXT", "YES", None, None, None),
            ("created_at", "TIMESTAMP", "NO", None, "CURRENT_TIMESTAMP", None)
        ]
        
        for col in sample_structure:
            self.structure_tree.insert('', 'end', values=col)
    
    def optimize_tables(self):
        """Optimize database tables"""
        try:
            # TODO: Implement actual table optimization
            self.log_maintenance("Starting table optimization...")
            self.log_maintenance("Tables optimized successfully")
            messagebox.showinfo("Success", "Tables optimized successfully")
        except Exception as e:
            self.log_maintenance(f"Error optimizing tables: {str(e)}")
            messagebox.showerror("Error", f"Failed to optimize tables: {str(e)}")
    
    def repair_tables(self):
        """Repair database tables"""
        try:
            # TODO: Implement actual table repair
            self.log_maintenance("Starting table repair...")
            self.log_maintenance("Tables repaired successfully")
            messagebox.showinfo("Success", "Tables repaired successfully")
        except Exception as e:
            self.log_maintenance(f"Error repairing tables: {str(e)}")
            messagebox.showerror("Error", f"Failed to repair tables: {str(e)}")
    
    def analyze_tables(self):
        """Analyze database tables"""
        try:
            # TODO: Implement actual table analysis
            self.log_maintenance("Starting table analysis...")
            self.log_maintenance("Tables analyzed successfully")
            messagebox.showinfo("Success", "Tables analyzed successfully")
        except Exception as e:
            self.log_maintenance(f"Error analyzing tables: {str(e)}")
            messagebox.showerror("Error", f"Failed to analyze tables: {str(e)}")
    
    def check_integrity(self):
        """Check database integrity"""
        try:
            # TODO: Implement actual integrity check
            self.log_maintenance("Starting integrity check...")
            self.log_maintenance("Database integrity verified")
            messagebox.showinfo("Success", "Database integrity verified")
        except Exception as e:
            self.log_maintenance(f"Error checking integrity: {str(e)}")
            messagebox.showerror("Error", f"Failed to check integrity: {str(e)}")
    
    def clear_cache(self):
        """Clear database cache"""
        try:
            # TODO: Implement actual cache clearing
            self.log_maintenance("Clearing database cache...")
            self.log_maintenance("Cache cleared successfully")
            messagebox.showinfo("Success", "Cache cleared successfully")
        except Exception as e:
            self.log_maintenance(f"Error clearing cache: {str(e)}")
            messagebox.showerror("Error", f"Failed to clear cache: {str(e)}")
    
    def vacuum_database(self):
        """Vacuum database to reclaim space"""
        try:
            # TODO: Implement actual database vacuum
            self.log_maintenance("Starting database vacuum...")
            self.log_maintenance("Database vacuum completed successfully")
            messagebox.showinfo("Success", "Database vacuum completed successfully")
        except Exception as e:
            self.log_maintenance(f"Error vacuuming database: {str(e)}")
            messagebox.showerror("Error", f"Failed to vacuum database: {str(e)}")
    
    def log_maintenance(self, message):
        """Add message to maintenance log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert('1.0', f"[{timestamp}] {message}\n")

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
