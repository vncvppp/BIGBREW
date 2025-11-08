import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from db_config import get_db_connection
import mysql.connector

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

class AdminDashboard(BaseDashboard):
    CURATED_PRODUCTS = [
        {
            "id": 1,
            "name": "Cookies n Cream",
            "category": "milk tea",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Crushed chocolate cookies blended with creamy milk tea.",
        },
        {
            "id": 2,
            "name": "Okinawa",
            "category": "milk tea",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Rich brown sugar milk tea with a mellow roasted finish.",
        },
        {
            "id": 3,
            "name": "Dark Choco",
            "category": "milk tea",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Bold cocoa infused milk tea with bittersweet notes.",
        },
        {
            "id": 4,
            "name": "Matcha",
            "category": "milk tea",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Earthy Japanese green tea balanced with creamy milk.",
        },
        {
            "id": 5,
            "name": "Red Velvet",
            "category": "milk tea",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Velvety cocoa and cream cheese inspired milk tea.",
        },
        {
            "id": 6,
            "name": "Winter Melon",
            "category": "milk tea",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Classic winter melon nectar with a caramelized sweetness.",
        },
        {
            "id": 7,
            "name": "Cheesecake",
            "category": "milk tea",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Silky cheesecake cream layered over smooth milk tea.",
        },
        {
            "id": 8,
            "name": "Chocolate",
            "category": "milk tea",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Classic chocolate milk tea with a sweet, silky finish.",
        },
        {
            "id": 9,
            "name": "Taro",
            "category": "milk tea",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Creamy taro root flavor blended into rich milk tea.",
        },
        {
            "id": 10,
            "name": "Salted Caramel",
            "category": "milk tea",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Sweet caramel milk tea with a hint of sea salt.",
        },
        {
            "id": 11,
            "name": "Brusko",
            "category": "coffee",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Strong brewed coffee with bold smoky undertones.",
        },
        {
            "id": 12,
            "name": "Mocha",
            "category": "coffee",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Chocolate kissed espresso with creamy milk foam.",
        },
        {
            "id": 13,
            "name": "Macchiato",
            "category": "coffee",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Espresso crowned with a dollop of velvety milk foam.",
        },
        {
            "id": 14,
            "name": "Vanilla",
            "category": "coffee",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Smooth espresso mellowed with fragrant vanilla cream.",
        },
        {
            "id": 15,
            "name": "Caramel",
            "category": "coffee",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Buttery caramel espresso rounded with creamy milk.",
        },
        {
            "id": 16,
            "name": "Matcha",
            "category": "coffee",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Espresso fused with vibrant matcha for an energizing blend.",
        },
        {
            "id": 17,
            "name": "Fudge",
            "category": "coffee",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Rich espresso layered with gooey chocolate fudge syrup.",
        },
        {
            "id": 18,
            "name": "Spanish Latte",
            "category": "coffee",
            "price_regular": 29.00,
            "price_large": 39.00,
            "description": "Velvety espresso sweetened with condensed milk.",
        },
    ]

    def __init__(self, user_data, login_window):
        self.product_inventory = {item["id"]: 100 for item in self.CURATED_PRODUCTS}
        super().__init__(user_data, login_window)

    def _get_curated_products(self):
        """Return curated products merged with current stock levels."""
        products = []
        for product in self.CURATED_PRODUCTS:
            merged = product.copy()
            merged["stock"] = self.product_inventory.get(product["id"], 0)
            products.append(merged)
        return products
    
    def _get_curated_product_by_id(self, product_id):
        for product in self.CURATED_PRODUCTS:
            if product["id"] == product_id:
                return product
        return None
    
    def _refresh_inventory_view(self):
        if getattr(self, 'inventory_tree', None) and self.inventory_tree.winfo_exists():
            self.refresh_inventory_list()

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
    
    def _get_product_id_column(self):
        """Detect the primary key column name for products table"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DESCRIBE products")
            columns = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Check for 'id' or 'product_id' column
            column_names = [col[0] for col in columns]
            if 'id' in column_names:
                return 'id'
            elif 'product_id' in column_names:
                return 'product_id'
            else:
                # Default to 'id' if we can't determine
                return 'id'
        except Exception:
            # Fallback to 'id' if we can't check
            return 'id'
    
    def _get_table_columns(self, table_name):
        """Return list of column names for a table, or empty list on failure"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE {table_name}")
            cols = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return cols
        except Exception:
            return []
    
    def _get_schema(self):
        """Detect commonly varying column names across products/categories/inventory"""
        prod_cols = self._get_table_columns('products')
        cat_cols = self._get_table_columns('categories')
        inv_cols = self._get_table_columns('inventory')

        # products
        prod_id = 'id' if 'id' in prod_cols else ('product_id' if 'product_id' in prod_cols else self._get_product_id_column())
        prod_name = 'name' if 'name' in prod_cols else ('product_name' if 'product_name' in prod_cols else 'name')
        prod_price = 'price' if 'price' in prod_cols else ('unit_price' if 'unit_price' in prod_cols else 'price')
        prod_desc = 'description' if 'description' in prod_cols else None
        prod_image = 'image_path' if 'image_path' in prod_cols else None
        prod_cat_fk = 'category_id' if 'category_id' in prod_cols else next((c for c in prod_cols if 'category' in c and 'id' in c), 'category_id')

        # categories
        cat_id = 'id' if 'id' in cat_cols else ('category_id' if 'category_id' in cat_cols else 'id')
        cat_name = 'name' if 'name' in cat_cols else ('category_name' if 'category_name' in cat_cols else 'name')

        # inventory
        inv_qty = 'quantity' if 'quantity' in inv_cols else ('current_stock' if 'current_stock' in inv_cols else 'quantity')
        inv_prod_fk = 'product_id' if 'product_id' in inv_cols else 'product_id'

        return {
            'prod_id': prod_id,
            'prod_name': prod_name,
            'prod_price': prod_price,
            'prod_desc': prod_desc,
            'prod_image': prod_image,
            'prod_cat_fk': prod_cat_fk,
            'cat_id': cat_id,
            'cat_name': cat_name,
            'inv_qty': inv_qty,
            'inv_prod_fk': inv_prod_fk,
        }
    
    def _get_sales_schema(self):
        """Detect varying column names for sales-related tables"""
        sales_cols = self._get_table_columns('sales')
        sale_items_cols = self._get_table_columns('sale_items')
        customer_cols = self._get_table_columns('customers')
        product_cols = self._get_table_columns('products')

        def find_col(columns, exact=(), contains=()):
            for name in exact:
                if name in columns:
                    return name
            for patterns in contains:
                for col in columns:
                    lower = col.lower()
                    if all(pattern in lower for pattern in patterns):
                        return col
            return columns[0] if columns else None

        sale_id = find_col(
            sales_cols,
            exact=('id', 'sale_id'),
            contains=(('sale', 'id'),)
        )
        sale_date = find_col(
            sales_cols,
            exact=('sale_date', 'date', 'created_at', 'transaction_date'),
            contains=(('sale', 'date'), ('trans', 'date'), ('order', 'date'), ('date',),)
        )
        total_amount = find_col(
            sales_cols,
            exact=('total_amount', 'grand_total', 'amount', 'total'),
            contains=(('total', 'amount'), ('grand', 'total'), ('amount',),)
        )
        payment_method = find_col(
            sales_cols,
            exact=('payment_method', 'payment_type', 'paymentmode'),
            contains=(('payment', 'method'), ('payment', 'type'), ('pay',),)
        )
        customer_fk = find_col(
            sales_cols,
            exact=('customer_id', 'client_id', 'customer'),
            contains=(('customer', 'id'), ('client', 'id'), ('cust',),)
        )

        customer_id = find_col(
            customer_cols,
            exact=('id', 'customer_id'),
            contains=(('customer', 'id'), ('client', 'id'),)
        )
        customer_first = find_col(
            customer_cols,
            exact=('first_name', 'firstname', 'given_name'),
            contains=(('first',), ('given',),)
        )
        customer_last = find_col(
            customer_cols,
            exact=('last_name', 'lastname', 'surname', 'family_name'),
            contains=(('last',), ('sur', 'name'), ('family',),)
        )

        sale_item_sale_fk = find_col(
            sale_items_cols,
            exact=('sale_id', 'sales_id', 'order_id'),
            contains=(('sale', 'id'), ('order', 'id'),)
        )
        sale_item_product_fk = find_col(
            sale_items_cols,
            exact=('product_id', 'item_id'),
            contains=(('product', 'id'), ('item', 'id'),)
        )
        sale_item_qty = find_col(
            sale_items_cols,
            exact=('quantity', 'qty', 'amount'),
            contains=(('qty',), ('quantity',),)
        )
        sale_item_price = find_col(
            sale_items_cols,
            exact=('price', 'unit_price', 'amount'),
            contains=(('price',), ('amount',),)
        )

        product_name = find_col(
            product_cols,
            exact=('name', 'product_name'),
            contains=(('product', 'name'),)
        )
        product_id = find_col(
            product_cols,
            exact=('id', 'product_id'),
            contains=(('product', 'id'),)
        )

        return {
            'sale_id': sale_id or 'id',
            'sale_date': sale_date or 'sale_date',
            'total_amount': total_amount or 'total_amount',
            'payment_method': payment_method or 'payment_method',
            'customer_fk': customer_fk or 'customer_id',
            'customer_pk': customer_id or 'id',
            'customer_first': customer_first or 'first_name',
            'customer_last': customer_last or 'last_name',
            'sale_item_sale_fk': sale_item_sale_fk or 'sale_id',
            'sale_item_product_fk': sale_item_product_fk or 'product_id',
            'sale_item_qty': sale_item_qty or 'quantity',
            'sale_item_price': sale_item_price or 'price',
            'product_name': product_name or 'name',
            'product_id': product_id or 'id',
        }
    
    def get_categories(self):
        """Get all categories from database"""
        categories = [
            {"id": "milk tea", "name": "milk tea"},
            {"id": "praf", "name": "praf"},
            {"id": "fruit tea", "name": "fruit tea"},
            {"id": "coffee", "name": "coffee"},
            {"id": "brosty", "name": "brosty"},
            {"id": "add-on", "name": "add-on"},
        ]
        return categories
    
    def manage_products(self):
        """Open product management window with CRUD operations"""
        self.product_window = tk.Toplevel(self.window)
        self.product_window.title("Product Management - CRUD Operations")
        self.product_window.geometry("1400x800")
        self.product_window.configure(bg=self.bg_color)
        
        # Center the window
        self.product_window.update_idletasks()
        width, height = 1400, 800
        screen_width = self.product_window.winfo_screenwidth()
        screen_height = self.product_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.product_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.product_window, bg=self.bg_color, height=60)
        header_frame.pack(fill='x', padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Product Management - Add, Edit, Delete Products",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(side='left')
        
        add_btn = tk.Button(
            header_frame,
            text="➕ Add New Product",
            font=("Arial", 12, "bold"),
            bg="#28A745",
            fg="white",
            relief='flat',
            bd=0,
            command=self.add_product_window,
            padx=20,
            pady=5
        )
        add_btn.pack(side='right', padx=(10, 0))
        
        # Main content area
        main_frame = tk.Frame(self.product_window, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Products list with Treeview
        list_frame = tk.Frame(main_frame, bg=self.card_bg, relief='raised', bd=2)
        list_frame.pack(fill='both', expand=True)
        
        tk.Label(
            list_frame,
            text="Products List",
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(pady=10)
        
        # Treeview with scrollbars
        tree_frame = tk.Frame(list_frame, bg=self.card_bg)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar_y = tk.Scrollbar(tree_frame, orient='vertical')
        scrollbar_x = tk.Scrollbar(tree_frame, orient='horizontal')
        
        self.products_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Name", "Category", "PriceRegular", "PriceLarge", "Description"),
            show='headings',
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=20
        )
        
        scrollbar_y.config(command=self.products_tree.yview)
        scrollbar_x.config(command=self.products_tree.xview)
        
        # Configure columns
        self.products_tree.heading("ID", text="ID")
        self.products_tree.heading("Name", text="Product Name")
        self.products_tree.heading("Category", text="Category")
        self.products_tree.heading("PriceRegular", text="Price Regular (₱)")
        self.products_tree.heading("PriceLarge", text="Price Large (₱)")
        self.products_tree.heading("Description", text="Description")
        
        self.products_tree.column("ID", width=50, anchor='center')
        self.products_tree.column("Name", width=220, anchor='w')
        self.products_tree.column("Category", width=140, anchor='w')
        self.products_tree.column("PriceRegular", width=140, anchor='center')
        self.products_tree.column("PriceLarge", width=140, anchor='center')
        self.products_tree.column("Description", width=360, anchor='w')
        
        self.products_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        
        # Action buttons
        button_frame = tk.Frame(list_frame, bg=self.card_bg)
        button_frame.pack(fill='x', pady=10)
        
        edit_btn = tk.Button(
            button_frame,
            text="✏️ Edit Product",
            font=("Arial", 11),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.edit_product_window,
            width=15,
            padx=10
        )
        edit_btn.pack(side='left', padx=5)
        
        delete_btn = tk.Button(
            button_frame,
            text="❌ Delete Product",
            font=("Arial", 11),
            bg="#DC3545",
            fg="white",
            relief='flat',
            bd=0,
            command=self.delete_product,
            width=15,
            padx=10
        )
        delete_btn.pack(side='left', padx=5)
        
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#6C757D",
            fg="white",
            relief='flat',
            bd=0,
            command=self.refresh_products_list,
            width=15,
            padx=10
        )
        refresh_btn.pack(side='left', padx=5)
        
        # Load products
        self.refresh_products_list()
    
    def refresh_products_list(self):
        """Refresh the products list"""
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        for product in self._get_curated_products():
            self.products_tree.insert(
                "",
                tk.END,
                values=(
                    product["id"],
                    product["name"],
                    product["category"],
                    f"₱{product['price_regular']:.2f}",
                    f"₱{product['price_large']:.2f}",
                    product["description"]
                )
            )
    
    def add_product_window(self):
        """Open window to add a new product"""
        add_window = tk.Toplevel(self.product_window)
        add_window.title("Add New Product")
        add_window.geometry("600x700")
        add_window.configure(bg=self.bg_color)
        
        # Center the window
        add_window.update_idletasks()
        width, height = 600, 700
        screen_width = add_window.winfo_screenwidth()
        screen_height = add_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        add_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(add_window, bg=self.card_bg, relief='raised', bd=2)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(
            form_frame,
            text="Add New Product",
            font=("Arial", 16, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(pady=20)
        
        # Category selection
        tk.Label(
            form_frame,
            text="Category:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            form_frame,
            textvariable=category_var,
            font=("Arial", 11),
            state='readonly',
            width=40
        )
        category_combo.pack(padx=20, pady=(0, 10), fill='x')
        
        categories = self.get_categories()
        category_dict = {cat['name']: cat['id'] for cat in categories}
        category_combo['values'] = list(category_dict.keys())
        if categories:
            category_combo.current(0)
        
        # Product name
        tk.Label(
            form_frame,
            text="Product Name:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        name_entry = tk.Entry(form_frame, font=("Arial", 11), width=40)
        name_entry.pack(padx=20, pady=(0, 10))
        
        # Description
        tk.Label(
            form_frame,
            text="Description:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        desc_text = tk.Text(form_frame, font=("Arial", 11), width=40, height=4)
        desc_text.pack(padx=20, pady=(0, 10))
        
        # Price
        tk.Label(
            form_frame,
            text="Price (₱):",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        price_entry = tk.Entry(form_frame, font=("Arial", 11), width=40)
        price_entry.pack(padx=20, pady=(0, 10))
        
        # Initial stock
        tk.Label(
            form_frame,
            text="Initial Stock Quantity:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        stock_entry = tk.Entry(form_frame, font=("Arial", 11), width=40)
        stock_entry.insert(0, "100")
        stock_entry.pack(padx=20, pady=(0, 10))
        
        # Image path (optional)
        image_path_var = tk.StringVar()
        
        def browse_image():
            filename = filedialog.askopenfilename(
                title="Select Product Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if filename:
                image_path_var.set(filename)
        
        tk.Label(
            form_frame,
            text="Image Path (Optional):",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        image_frame = tk.Frame(form_frame, bg=self.card_bg)
        image_frame.pack(padx=20, pady=(0, 10), fill='x')
        
        image_entry = tk.Entry(image_frame, textvariable=image_path_var, font=("Arial", 11), width=30)
        image_entry.pack(side='left', fill='x', expand=True)
        
        browse_btn = tk.Button(
            image_frame,
            text="Browse",
            font=("Arial", 10),
            bg="#6C757D",
            fg="white",
            relief='flat',
            command=browse_image,
            width=10
        )
        browse_btn.pack(side='right', padx=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=self.card_bg)
        button_frame.pack(pady=20)
        
        def save_product():
            try:
                category_name = category_var.get()
                if not category_name:
                    messagebox.showerror("Error", "Please select a category")
                    return
                
                name = name_entry.get().strip()
                description = desc_text.get("1.0", tk.END).strip()
                price = float(price_entry.get())
                stock = int(stock_entry.get())
                image_path = image_path_var.get().strip() or None
                
                if not name:
                    messagebox.showerror("Error", "Product name is required")
                    return
                
                if price < 0:
                    messagebox.showerror("Error", "Price cannot be negative")
                    return
                
                if stock < 0:
                    messagebox.showerror("Error", "Stock cannot be negative")
                    return
                
                # Determine new product ID
                existing_ids = [product["id"] for product in self.CURATED_PRODUCTS]
                new_id = max(existing_ids) + 1 if existing_ids else 1
                
                new_product = {
                    "id": new_id,
                    "name": name,
                    "category": category_name,
                    "price_regular": price,
                    "price_large": price + 10 if price >= 0 else price,
                    "description": description or "No description",
                    "image_path": image_path,
                }
                
                self.CURATED_PRODUCTS.append(new_product)
                self.product_inventory[new_id] = stock
                
                messagebox.showinfo("Success", f"Product '{name}' added successfully!")
                add_window.destroy()
                self.refresh_products_list()
                self._refresh_inventory_view()
            
            except ValueError:
                messagebox.showerror("Error", "Invalid price or stock value")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add product: {e}")
        
        save_btn = tk.Button(
            button_frame,
            text="Save Product",
            font=("Arial", 12, "bold"),
            bg="#28A745",
            fg="white",
            relief='flat',
            command=save_product,
            width=15,
            padx=10
        )
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 12),
            bg="#6C757D",
            fg="white",
            relief='flat',
            command=add_window.destroy,
            width=15,
            padx=10
        )
        cancel_btn.pack(side='left', padx=5)
    
    def edit_product_window(self):
        """Open window to edit selected product"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a product to edit")
            return
        
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        
        product = self._get_curated_product_by_id(product_id)
        if not product:
            messagebox.showerror("Error", "Product not found")
            return
        
        edit_window = tk.Toplevel(self.product_window)
        edit_window.title("Edit Product")
        edit_window.geometry("600x700")
        edit_window.configure(bg=self.bg_color)
        
        # Center the window
        edit_window.update_idletasks()
        width, height = 600, 700
        screen_width = edit_window.winfo_screenwidth()
        screen_height = edit_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        edit_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(edit_window, bg=self.card_bg, relief='raised', bd=2)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(
            form_frame,
            text=f"Edit Product: {product['name']}",
            font=("Arial", 16, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(pady=20)
        
        # Category selection
        tk.Label(
            form_frame,
            text="Category:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            form_frame,
            textvariable=category_var,
            font=("Arial", 11),
            state='readonly',
            width=40
        )
        category_combo.pack(padx=20, pady=(0, 10), fill='x')
        
        categories = self.get_categories()
        category_dict = {cat['name']: cat['id'] for cat in categories}
        category_combo['values'] = list(category_dict.keys())
        
        # Set current category
        current_cat = product.get('category', '')
        if current_cat in category_dict:
            category_combo.set(current_cat)
        elif categories:
            category_combo.current(0)
        
        # Product name
        tk.Label(
            form_frame,
            text="Product Name:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        name_entry = tk.Entry(form_frame, font=("Arial", 11), width=40)
        name_entry.insert(0, product['name'])
        name_entry.pack(padx=20, pady=(0, 10))
        
        # Description
        tk.Label(
            form_frame,
            text="Description:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        desc_text = tk.Text(form_frame, font=("Arial", 11), width=40, height=4)
        desc_text.insert("1.0", product.get('description', ''))
        desc_text.pack(padx=20, pady=(0, 10))
        
        # Price
        tk.Label(
            form_frame,
            text="Price (₱):",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        price_entry = tk.Entry(form_frame, font=("Arial", 11), width=40)
        price_entry.insert(0, str(product.get('price_regular', 0)))
        price_entry.pack(padx=20, pady=(0, 10))
        
        # Image path
        image_path_var = tk.StringVar(value=product.get('image_path', ''))
        
        def browse_image():
            filename = filedialog.askopenfilename(
                title="Select Product Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if filename:
                image_path_var.set(filename)
        
        tk.Label(
            form_frame,
            text="Image Path (Optional):",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        image_frame = tk.Frame(form_frame, bg=self.card_bg)
        image_frame.pack(padx=20, pady=(0, 10), fill='x')
        
        image_entry = tk.Entry(image_frame, textvariable=image_path_var, font=("Arial", 11), width=30)
        image_entry.pack(side='left', fill='x', expand=True)
        
        browse_btn = tk.Button(
            image_frame,
            text="Browse",
            font=("Arial", 10),
            bg="#6C757D",
            fg="white",
            relief='flat',
            command=browse_image,
            width=10
        )
        browse_btn.pack(side='right', padx=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=self.card_bg)
        button_frame.pack(pady=20)
        
        def update_product():
            try:
                category_name = category_var.get()
                if not category_name:
                    messagebox.showerror("Error", "Please select a category")
                    return
                
                name = name_entry.get().strip()
                description = desc_text.get("1.0", tk.END).strip()
                price = float(price_entry.get())
                image_path = image_path_var.get().strip() or None
                
                if not name:
                    messagebox.showerror("Error", "Product name is required")
                    return
                
                if price < 0:
                    messagebox.showerror("Error", "Price cannot be negative")
                    return
                
                updated = self._get_curated_product_by_id(product_id)
                if not updated:
                    messagebox.showerror("Error", "Product not found")
                    return
                
                updated["name"] = name
                updated["category"] = category_name
                updated["description"] = description or "No description"
                updated["price_regular"] = price
                updated["price_large"] = price + 10 if price >= 0 else price
                updated["image_path"] = image_path
                
                messagebox.showinfo("Success", f"Product '{name}' updated successfully!")
                edit_window.destroy()
                self.refresh_products_list()
                self._refresh_inventory_view()
            
            except ValueError:
                messagebox.showerror("Error", "Invalid price value")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update product: {e}")
        
        save_btn = tk.Button(
            button_frame,
            text="Update Product",
            font=("Arial", 12, "bold"),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            command=update_product,
            width=15,
            padx=10
        )
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 12),
            bg="#6C757D",
            fg="white",
            relief='flat',
            command=edit_window.destroy,
            width=15,
            padx=10
        )
        cancel_btn.pack(side='left', padx=5)
    
    def delete_product(self):
        """Delete selected product"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a product to delete")
            return
        
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{product_name}'?\n\n"
            "This action cannot be undone and will also remove inventory records."
        )
        
        if confirm:
            original_length = len(self.CURATED_PRODUCTS)
            filtered = [
                product for product in self.CURATED_PRODUCTS if product["id"] != product_id
            ]
            self.__class__.CURATED_PRODUCTS = filtered
            self.product_inventory.pop(product_id, None)
            
            if len(self.CURATED_PRODUCTS) < original_length:
                messagebox.showinfo("Success", f"Product '{product_name}' deleted successfully!")
                self.refresh_products_list()
                self._refresh_inventory_view()
            else:
                messagebox.showerror("Error", "Failed to delete product")
    
    def manage_inventory(self):
        """Open inventory management window"""
        self.inventory_window = tk.Toplevel(self.window)
        self.inventory_window.title("Inventory Management")
        self.inventory_window.geometry("1200x700")
        self.inventory_window.configure(bg=self.bg_color)
        
        def close_inventory():
            try:
                if getattr(self, 'inventory_tree', None) is not None:
                    self.inventory_tree = None
            except Exception:
                pass
            win = getattr(self, 'inventory_window', None)
            if win is not None:
                self.inventory_window = None
                win.destroy()
        
        self.inventory_window.protocol("WM_DELETE_WINDOW", close_inventory)
        
        # Center the window
        self.inventory_window.update_idletasks()
        width, height = 1200, 700
        screen_width = self.inventory_window.winfo_screenwidth()
        screen_height = self.inventory_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.inventory_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.inventory_window, bg=self.bg_color, height=60)
        header_frame.pack(fill='x', padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Inventory Management - Stock Tracking",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(side='left')
        
        # Main content
        main_frame = tk.Frame(self.inventory_window, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Inventory list
        list_frame = tk.Frame(main_frame, bg=self.card_bg, relief='raised', bd=2)
        list_frame.pack(fill='both', expand=True)
        
        tk.Label(
            list_frame,
            text="Current Stock Levels",
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(pady=10)
        
        # Treeview with scrollbars
        tree_frame = tk.Frame(list_frame, bg=self.card_bg)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar_y = tk.Scrollbar(tree_frame, orient='vertical')
        scrollbar_x = tk.Scrollbar(tree_frame, orient='horizontal')
        
        self.inventory_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Product", "Category", "PriceRegular", "PriceLarge", "Current Stock", "Status"),
            show='headings',
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=20
        )
        
        scrollbar_y.config(command=self.inventory_tree.yview)
        scrollbar_x.config(command=self.inventory_tree.xview)
        
        # Configure columns
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Product", text="Product Name")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.heading("PriceRegular", text="Price Regular (₱)")
        self.inventory_tree.heading("PriceLarge", text="Price Large (₱)")
        self.inventory_tree.heading("Current Stock", text="Current Stock")
        self.inventory_tree.heading("Status", text="Status")
        
        self.inventory_tree.column("ID", width=50, anchor='center')
        self.inventory_tree.column("Product", width=230, anchor='w')
        self.inventory_tree.column("Category", width=130, anchor='w')
        self.inventory_tree.column("PriceRegular", width=140, anchor='center')
        self.inventory_tree.column("PriceLarge", width=140, anchor='center')
        self.inventory_tree.column("Current Stock", width=140, anchor='center')
        self.inventory_tree.column("Status", width=130, anchor='center')
        
        self.inventory_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        
        # Action buttons
        button_frame = tk.Frame(list_frame, bg=self.card_bg)
        button_frame.pack(fill='x', pady=10)
        
        update_stock_btn = tk.Button(
            button_frame,
            text="📦 Update Stock",
            font=("Arial", 11),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.update_stock_window,
            width=15,
            padx=10
        )
        update_stock_btn.pack(side='left', padx=5)
        
        refresh_inv_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#6C757D",
            fg="white",
            relief='flat',
            bd=0,
            command=self.refresh_inventory_list,
            width=15,
            padx=10
        )
        refresh_inv_btn.pack(side='left', padx=5)
        
        # Load inventory
        self.refresh_inventory_list()
    
    def refresh_inventory_list(self):
        """Refresh the inventory list"""
        tree = getattr(self, 'inventory_tree', None)
        if tree is None:
            return
        try:
            if not tree.winfo_exists():
                return
        except tk.TclError:
            return
        # Clear existing items
        try:
            for item in tree.get_children():
                tree.delete(item)
        except tk.TclError:
            return
        
        for product in self._get_curated_products():
            stock = product["stock"]
            if stock == 0:
                status = "Out of Stock"
                status_color = "#DC3545"
            elif stock < 10:
                status = "Low Stock"
                status_color = "#FFC107"
            else:
                status = "In Stock"
                status_color = "#28A745"
            
            try:
                item_id = tree.insert(
                "",
                tk.END,
                values=(
                    product["id"],
                    product["name"],
                    product["category"],
                    f"₱{product['price_regular']:.2f}",
                    f"₱{product['price_large']:.2f}",
                    stock,
                    status
                ),
                tags=(status_color,)
            )
            
                tree.tag_configure(status_color, foreground=status_color)
            except tk.TclError:
                return
    
    def update_stock_window(self):
        """Open window to update stock for selected product"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a product to update stock")
            return
        
        item = self.inventory_tree.item(selection[0])
        product_id = int(item['values'][0])
        product_name = item['values'][1]
        current_stock = int(item['values'][5])
        
        update_window = tk.Toplevel(self.inventory_window)
        update_window.title("Update Stock")
        update_window.geometry("400x300")
        update_window.configure(bg=self.bg_color)
        
        # Center the window
        update_window.update_idletasks()
        width, height = 400, 300
        screen_width = update_window.winfo_screenwidth()
        screen_height = update_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        update_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(update_window, bg=self.card_bg, relief='raised', bd=2)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(
            form_frame,
            text=f"Update Stock: {product_name}",
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(pady=20)
        
        tk.Label(
            form_frame,
            text=f"Current Stock: {current_stock}",
            font=("Arial", 12),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(pady=10)
        
        tk.Label(
            form_frame,
            text="New Stock Quantity:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(pady=(20, 5))
        
        stock_entry = tk.Entry(form_frame, font=("Arial", 12), width=20)
        stock_entry.insert(0, str(current_stock))
        stock_entry.pack(pady=10)
        stock_entry.select_range(0, tk.END)
        stock_entry.focus()
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=self.card_bg)
        button_frame.pack(pady=20)
        
        def save_stock():
            try:
                new_stock = int(stock_entry.get())
                if new_stock < 0:
                    messagebox.showerror("Error", "Stock cannot be negative")
                    return
                
                self.product_inventory[product_id] = new_stock
                
                messagebox.showinfo("Success", f"Stock updated to {new_stock} for {product_name}")
                update_window.destroy()
                self.refresh_inventory_list()
                self.refresh_products_list()
            
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update stock: {e}")
        
        save_btn = tk.Button(
            button_frame,
            text="Update Stock",
            font=("Arial", 12, "bold"),
            bg="#28A745",
            fg="white",
            relief='flat',
            command=save_stock,
            width=15,
            padx=10
        )
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 12),
            bg="#6C757D",
            fg="white",
            relief='flat',
            command=update_window.destroy,
            width=15,
            padx=10
        )
        cancel_btn.pack(side='left', padx=5)
    
    def manage_sales(self):
        """Open sales management window"""
        self.sales_window = tk.Toplevel(self.window)
        self.sales_window.title("Sales Management")
        self.sales_window.geometry("1400x800")
        self.sales_window.configure(bg=self.bg_color)
        
        # Center the window
        self.sales_window.update_idletasks()
        width, height = 1400, 800
        screen_width = self.sales_window.winfo_screenwidth()
        screen_height = self.sales_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.sales_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.sales_window, bg=self.bg_color, height=60)
        header_frame.pack(fill='x', padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Sales Management - View and Manage Transactions",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(side='left')
        
        # Filter frame
        filter_frame = tk.Frame(header_frame, bg=self.bg_color)
        filter_frame.pack(side='right')
        
        tk.Label(
            filter_frame,
            text="Date Range:",
            font=("Arial", 10),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side='left', padx=5)
        
        date_filter_var = tk.StringVar(value="All")
        date_filter = ttk.Combobox(
            filter_frame,
            textvariable=date_filter_var,
            values=["All", "Today", "Last 7 Days", "Last 30 Days", "This Month", "Last Month"],
            state='readonly',
            width=15
        )
        date_filter.pack(side='left', padx=5)
        date_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_sales_list())
        
        # Main content area
        main_frame = tk.Frame(self.sales_window, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Sales list with Treeview
        list_frame = tk.Frame(main_frame, bg=self.card_bg, relief='raised', bd=2)
        list_frame.pack(fill='both', expand=True)
        
        tk.Label(
            list_frame,
            text="Sales Transactions",
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728"
        ).pack(pady=10)
        
        # Treeview with scrollbars
        tree_frame = tk.Frame(list_frame, bg=self.card_bg)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar_y = tk.Scrollbar(tree_frame, orient='vertical')
        scrollbar_x = tk.Scrollbar(tree_frame, orient='horizontal')
        
        self.sales_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Date", "Customer", "Total Amount", "Payment Method", "Items"),
            show='headings',
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=20
        )
        
        scrollbar_y.config(command=self.sales_tree.yview)
        scrollbar_x.config(command=self.sales_tree.xview)
        
        # Configure columns
        self.sales_tree.heading("ID", text="Sale ID")
        self.sales_tree.heading("Date", text="Date & Time")
        self.sales_tree.heading("Customer", text="Customer")
        self.sales_tree.heading("Total Amount", text="Total (₱)")
        self.sales_tree.heading("Payment Method", text="Payment")
        self.sales_tree.heading("Items", text="Items")
        
        self.sales_tree.column("ID", width=80, anchor='center')
        self.sales_tree.column("Date", width=180, anchor='w')
        self.sales_tree.column("Customer", width=200, anchor='w')
        self.sales_tree.column("Total Amount", width=120, anchor='center')
        self.sales_tree.column("Payment Method", width=120, anchor='center')
        self.sales_tree.column("Items", width=300, anchor='w')
        
        self.sales_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        
        # Action buttons
        button_frame = tk.Frame(list_frame, bg=self.card_bg)
        button_frame.pack(fill='x', pady=10)
        
        view_details_btn = tk.Button(
            button_frame,
            text="📋 View Details",
            font=("Arial", 11),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            command=self.view_sale_details,
            width=15,
            padx=10
        )
        view_details_btn.pack(side='left', padx=5)
        
        delete_sale_btn = tk.Button(
            button_frame,
            text="❌ Delete Sale",
            font=("Arial", 11),
            bg="#DC3545",
            fg="white",
            relief='flat',
            bd=0,
            command=self.delete_sale,
            width=15,
            padx=10
        )
        delete_sale_btn.pack(side='left', padx=5)
        
        refresh_sales_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#6C757D",
            fg="white",
            relief='flat',
            bd=0,
            command=self.refresh_sales_list,
            width=15,
            padx=10
        )
        refresh_sales_btn.pack(side='left', padx=5)
        
        # Store filter variable
        self.date_filter_var = date_filter_var
        
        # Load sales
        self.refresh_sales_list()
    
    def refresh_sales_list(self):
        """Refresh the sales list"""
        # Clear existing items
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            schema = self._get_sales_schema()
            sale_id_col = schema['sale_id']
            sale_date_col = schema['sale_date']
            total_amount_col = schema['total_amount']
            payment_method_col = schema['payment_method']
            customer_fk_col = schema['customer_fk']
            customer_pk_col = schema['customer_pk']
            customer_first_col = schema['customer_first']
            customer_last_col = schema['customer_last']
            sale_item_sale_fk = schema['sale_item_sale_fk']
            sale_item_qty = schema['sale_item_qty']
            sale_item_product_fk = schema['sale_item_product_fk']
            product_name_col = schema['product_name']
            product_id_col = schema['product_id']
            
            # Build date filter
            date_filter = getattr(self, 'date_filter_var', tk.StringVar(value="All")).get()
            date_condition = ""
            params = []
            
            if date_filter == "Today":
                date_condition = f"DATE(s.{sale_date_col}) = CURDATE()"
            elif date_filter == "Last 7 Days":
                date_condition = f"s.{sale_date_col} >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
            elif date_filter == "Last 30 Days":
                date_condition = f"s.{sale_date_col} >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
            elif date_filter == "This Month":
                date_condition = f"MONTH(s.{sale_date_col}) = MONTH(NOW()) AND YEAR(s.{sale_date_col}) = YEAR(NOW())"
            elif date_filter == "Last Month":
                date_condition = (
                    f"MONTH(s.{sale_date_col}) = MONTH(DATE_SUB(NOW(), INTERVAL 1 MONTH)) "
                    f"AND YEAR(s.{sale_date_col}) = YEAR(DATE_SUB(NOW(), INTERVAL 1 MONTH))"
                )
            
            where_clause = f"WHERE {date_condition}" if date_condition else ""
            
            query = f"""
                SELECT s.{sale_id_col} AS sale_id,
                       s.{sale_date_col} AS sale_date,
                       s.{total_amount_col} AS total_amount,
                       s.{payment_method_col} AS payment_method,
                       COALESCE(c.{customer_first_col}, '') AS customer_first,
                       COALESCE(c.{customer_last_col}, '') AS customer_last,
                       (
                           SELECT GROUP_CONCAT(CONCAT(si.{sale_item_qty}, 'x ', p.{product_name_col}) SEPARATOR ', ')
                           FROM sale_items si
                           JOIN products p ON si.{sale_item_product_fk} = p.{product_id_col}
                           WHERE si.{sale_item_sale_fk} = s.{sale_id_col}
                       ) AS items
                FROM sales s
                LEFT JOIN customers c ON s.{customer_fk_col} = c.{customer_pk_col}
                {where_clause}
                ORDER BY s.{sale_date_col} DESC
            """
            
            cursor.execute(query, params)
            sales = cursor.fetchall()
            
            for sale in sales:
                customer_name = f"{sale['customer_first']} {sale['customer_last']}".strip() or "Walk-in"
                sale_date = sale['sale_date']
                if isinstance(sale_date, str):
                    sale_date_str = sale_date
                elif sale_date is not None:
                    sale_date_str = sale_date.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    sale_date_str = "N/A"
                
                payment_method = sale.get('payment_method') or 'Unknown'
                if isinstance(payment_method, str):
                    payment_display = payment_method.title()
                else:
                    payment_display = str(payment_method)
                
                total_amount = sale.get('total_amount') or 0
                
                self.sales_tree.insert(
                    "",
                    tk.END,
                    values=(
                        sale['sale_id'],
                        sale_date_str,
                        customer_name,
                        f"₱{total_amount:.2f}",
                        payment_display,
                        sale.get('items') or 'N/A'
                    )
                )
            
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sales: {e}")
    
    def view_sale_details(self):
        """View details of selected sale"""
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sale to view details")
            return
        
        item = self.sales_tree.item(selection[0])
        sale_id = item['values'][0]
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            schema = self._get_sales_schema()
            sale_id_col = schema['sale_id']
            sale_date_col = schema['sale_date']
            total_amount_col = schema['total_amount']
            payment_method_col = schema['payment_method']
            customer_fk_col = schema['customer_fk']
            customer_pk_col = schema['customer_pk']
            customer_first_col = schema['customer_first']
            customer_last_col = schema['customer_last']
            sale_item_sale_fk = schema['sale_item_sale_fk']
            sale_item_product_fk = schema['sale_item_product_fk']
            sale_item_qty = schema['sale_item_qty']
            sale_item_price = schema['sale_item_price']
            product_schema = self._get_schema()
            product_name_col = product_schema['prod_name']
            product_id_col = product_schema['prod_id']
            
            # Get sale details
            sale_query = f"""
                SELECT s.{sale_id_col} AS sale_id,
                       s.{sale_date_col} AS sale_date,
                       s.{total_amount_col} AS total_amount,
                       s.{payment_method_col} AS payment_method,
                       COALESCE(c.{customer_first_col}, '') AS customer_first,
                       COALESCE(c.{customer_last_col}, '') AS customer_last
                FROM sales s
                LEFT JOIN customers c ON s.{customer_fk_col} = c.{customer_pk_col}
                WHERE s.{sale_id_col} = %s
            """
            cursor.execute(sale_query, (sale_id,))
            sale = cursor.fetchone()
            
            # Get sale items
            items_query = f"""
                SELECT si.{sale_item_qty} AS quantity,
                       si.{sale_item_price} AS price,
                       p.{product_name_col} AS product_name
                FROM sale_items si
                JOIN products p ON si.{sale_item_product_fk} = p.{product_id_col}
                WHERE si.{sale_item_sale_fk} = %s
            """
            cursor.execute(items_query, (sale_id,))
            items = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            if not sale:
                messagebox.showerror("Error", "Sale not found")
                return
            
            # Show details window
            details_window = tk.Toplevel(self.sales_window)
            details_window.title(f"Sale Details - #{sale_id}")
            details_window.geometry("600x500")
            details_window.configure(bg=self.bg_color)
            
            # Center the window
            details_window.update_idletasks()
            width, height = 600, 500
            screen_width = details_window.winfo_screenwidth()
            screen_height = details_window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            details_window.geometry(f"{width}x{height}+{x}+{y}")
            
            # Form frame
            form_frame = tk.Frame(details_window, bg=self.card_bg, relief='raised', bd=2)
            form_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            tk.Label(
                form_frame,
                text=f"Sale Details - #{sale_id}",
                font=("Arial", 16, "bold"),
                bg=self.card_bg,
                fg="#4A3728"
            ).pack(pady=20)
            
            # Sale info
            payment_method = sale.get('payment_method') or 'Unknown'
            if isinstance(payment_method, str):
                payment_display = payment_method.title()
            else:
                payment_display = str(payment_method)
            
            total_amount = sale.get('total_amount') or 0
            
            info_text = f"""
Sale ID: {sale['sale_id']}
Date: {sale['sale_date']}
Customer: {f"{sale['customer_first']} {sale['customer_last']}".strip() or 'Walk-in'}
Payment Method: {payment_display}
Total Amount: ₱{total_amount:.2f}

Items:
"""
            tk.Label(
                form_frame,
                text=info_text,
                font=("Arial", 11),
                bg=self.card_bg,
                fg="#4A3728",
                justify='left',
                anchor='w'
            ).pack(padx=20, pady=10, anchor='w')
            
            # Items list
            items_text = ""
            for item in items:
                quantity = item.get('quantity') or 0
                price = item.get('price') or 0
                items_text += (
                    f"  • {quantity}x {item.get('product_name', 'Unknown')} @ ₱{price:.2f} = ₱{quantity * price:.2f}\n"
                )
            
            items_label = tk.Label(
                form_frame,
                text=items_text,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#666666",
                justify='left',
                anchor='w'
            )
            items_label.pack(padx=20, pady=10, anchor='w')
            
            # Close button
            close_btn = tk.Button(
                form_frame,
                text="Close",
                font=("Arial", 12),
                bg="#6C757D",
                fg="white",
                relief='flat',
                command=details_window.destroy,
                width=15,
                padx=10
            )
            close_btn.pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sale details: {e}")
    
    def delete_sale(self):
        """Delete selected sale"""
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sale to delete")
            return
        
        item = self.sales_tree.item(selection[0])
        sale_id = item['values'][0]
        sale_date = item['values'][1]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete sale #{sale_id} from {sale_date}?\n\n"
            "This action cannot be undone and will also remove all associated sale items."
        )
        
        if confirm:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                schema = self._get_sales_schema()
                sale_id_col = schema['sale_id']
                
                # Delete sale (cascade will delete sale_items)
                cursor.execute(f"DELETE FROM sales WHERE {sale_id_col} = %s", (sale_id,))
                conn.commit()
                
                success = cursor.rowcount > 0
                cursor.close()
                conn.close()
                
                if success:
                    messagebox.showinfo("Success", f"Sale #{sale_id} deleted successfully!")
                    self.refresh_sales_list()
                else:
                    messagebox.showerror("Error", "Failed to delete sale")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete sale: {e}")
    
    def view_reports(self):
        """Open reports and analytics window"""
        try:
            from reports import ReportsAnalytics
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
