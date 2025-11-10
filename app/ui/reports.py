import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.db.connection import DatabaseConfig
import json

class ReportsAnalytics:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.window = tk.Toplevel(self.parent)
        self.window.title("BigBrew - Reports & Analytics")
        self.window.geometry("1200x800")
        
        # Database connection
        self.db = DatabaseConfig()
        
        # Color scheme matching the main app
        self.bg_color = "#4A3728"  # Dark brown
        self.accent_color = "#FFD700"  # Gold
        self.card_bg = "#F5F5DC"  # Beige
        self.text_color = "#FFFFFF"  # White
        self.button_color = "#D2691E"  # Coffee brown
        
        self.window.configure(bg=self.bg_color)
        self.setup_ui()
        
        # Center window
        self.window.update_idletasks()
        width, height = 1200, 800
        x = (self.window.winfo_screenwidth() - width) // 2
        y = (self.window.winfo_screenheight() - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Header
        self.create_header()
        
        # Main content area with notebook tabs
        self.create_notebook()
        
    def create_header(self):
        """Create the header section"""
        header = tk.Frame(self.window, bg=self.bg_color, height=60)
        header.pack(fill='x', padx=20, pady=10)
        
        # Title
        title = tk.Label(
            header,
            text="Reports & Analytics",
            font=("Arial", 24, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title.pack(side='left')
        
        # Date range
        date_frame = tk.Frame(header, bg=self.bg_color)
        date_frame.pack(side='right')
        
        periods = ["Today", "Last 7 Days", "Last 30 Days", "This Month", "Last Month", "Custom"]
        self.period_var = tk.StringVar(value="Last 7 Days")
        period_menu = ttk.Combobox(
            date_frame,
            textvariable=self.period_var,
            values=periods,
            state="readonly",
            width=15
        )
        period_menu.pack(side='left', padx=5)
        period_menu.bind('<<ComboboxSelected>>', self.on_period_change)
        
        refresh_btn = tk.Button(
            date_frame,
            text="↻ Refresh",
            font=("Arial", 10),
            bg=self.button_color,
            fg=self.text_color,
            command=self.refresh_reports
        )
        refresh_btn.pack(side='left', padx=5)
        
    def create_notebook(self):
        """Create tabbed interface for different reports"""
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Sales Reports
        sales_frame = tk.Frame(self.notebook, bg=self.card_bg)
        self.notebook.add(sales_frame, text="Sales Reports")
        self.setup_sales_tab(sales_frame)
        
        # Customer Analytics
        customer_frame = tk.Frame(self.notebook, bg=self.card_bg)
        self.notebook.add(customer_frame, text="Customer Analytics")
        self.setup_customer_tab(customer_frame)
        
        # Inventory Analytics
        inventory_frame = tk.Frame(self.notebook, bg=self.card_bg)
        self.notebook.add(inventory_frame, text="Inventory Analytics")
        self.setup_inventory_tab(inventory_frame)
        
    def setup_sales_tab(self, parent):
        """Setup the sales reports tab"""
        # Top stats cards
        stats_frame = tk.Frame(parent, bg=self.card_bg)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        stats = [
            ("Total Sales", "$0.00"),
            ("Orders", "0"),
            ("Avg Order Value", "$0.00"),
            ("Top Product", "None")
        ]
        
        for i, (label, value) in enumerate(stats):
            card = tk.Frame(stats_frame, bg='white', relief='solid', bd=1)
            card.grid(row=0, column=i, padx=5, sticky='nsew')
            
            tk.Label(
                card,
                text=label,
                font=("Arial", 12),
                bg='white'
            ).pack(pady=(10, 5))
            
            tk.Label(
                card,
                text=value,
                font=("Arial", 16, "bold"),
                bg='white'
            ).pack(pady=(0, 10))
            
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        
        # Sales graph
        graph_frame = tk.Frame(parent, bg=self.card_bg)
        graph_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.sales_figure = plt.Figure(figsize=(10, 4))
        self.sales_canvas = FigureCanvasTkAgg(self.sales_figure, graph_frame)
        self.sales_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Product table
        table_frame = tk.Frame(parent, bg=self.card_bg)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('Product', 'Quantity', 'Revenue', 'Profit')
        self.product_table = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.product_table.heading(col, text=col)
            self.product_table.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.product_table.yview)
        self.product_table.configure(yscrollcommand=scrollbar.set)
        
        self.product_table.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def setup_customer_tab(self, parent):
        """Setup the customer analytics tab"""
        # Customer stats cards
        stats_frame = tk.Frame(parent, bg=self.card_bg)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        stats = [
            ("Total Customers", "0"),
            ("New Customers", "0"),
            ("Avg Customer Value", "$0.00"),
            ("Loyalty Points Issued", "0")
        ]
        
        for i, (label, value) in enumerate(stats):
            card = tk.Frame(stats_frame, bg='white', relief='solid', bd=1)
            card.grid(row=0, column=i, padx=5, sticky='nsew')
            
            tk.Label(
                card,
                text=label,
                font=("Arial", 12),
                bg='white'
            ).pack(pady=(10, 5))
            
            tk.Label(
                card,
                text=value,
                font=("Arial", 16, "bold"),
                bg='white'
            ).pack(pady=(0, 10))
            
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        
        # Customer segments graph
        segments_frame = tk.Frame(parent, bg=self.card_bg)
        segments_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.segments_figure = plt.Figure(figsize=(6, 4))
        self.segments_canvas = FigureCanvasTkAgg(self.segments_figure, segments_frame)
        self.segments_canvas.get_tk_widget().pack(side='left', fill='both', expand=True)
        
        # Customer visit frequency graph
        frequency_frame = tk.Frame(parent, bg=self.card_bg)
        frequency_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.frequency_figure = plt.Figure(figsize=(6, 4))
        self.frequency_canvas = FigureCanvasTkAgg(self.frequency_figure, frequency_frame)
        self.frequency_canvas.get_tk_widget().pack(side='right', fill='both', expand=True)
        
    def setup_inventory_tab(self, parent):
        """Setup the inventory analytics tab"""
        # Inventory stats cards
        stats_frame = tk.Frame(parent, bg=self.card_bg)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        stats = [
            ("Total Items", "0"),
            ("Low Stock Items", "0"),
            ("Out of Stock", "0"),
            ("Inventory Value", "$0.00")
        ]
        
        for i, (label, value) in enumerate(stats):
            card = tk.Frame(stats_frame, bg='white', relief='solid', bd=1)
            card.grid(row=0, column=i, padx=5, sticky='nsew')
            
            tk.Label(
                card,
                text=label,
                font=("Arial", 12),
                bg='white'
            ).pack(pady=(10, 5))
            
            tk.Label(
                card,
                text=value,
                font=("Arial", 16, "bold"),
                bg='white'
            ).pack(pady=(0, 10))
            
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        
        # Inventory levels graph
        levels_frame = tk.Frame(parent, bg=self.card_bg)
        levels_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.inventory_figure = plt.Figure(figsize=(10, 4))
        self.inventory_canvas = FigureCanvasTkAgg(self.inventory_figure, levels_frame)
        self.inventory_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Low stock alerts table
        table_frame = tk.Frame(parent, bg=self.card_bg)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('Item', 'Current Stock', 'Min Stock', 'Status', 'Last Ordered')
        self.inventory_table = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.inventory_table.heading(col, text=col)
            self.inventory_table.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.inventory_table.yview)
        self.inventory_table.configure(yscrollcommand=scrollbar.set)
        
        self.inventory_table.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def on_period_change(self, event):
        """Handle date period changes"""
        period = self.period_var.get()
        if period == "Custom":
            # TODO: Show date picker dialog
            pass
        self.refresh_reports()
        
    def refresh_reports(self):
        """Refresh all reports with current date range"""
        self.update_sales_reports()
        self.update_customer_analytics()
        self.update_inventory_analytics()
        
    def get_date_range(self):
        """Get start and end dates based on selected period"""
        period = self.period_var.get()
        end_date = datetime.now()
        
        if period == "Today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "Last 7 Days":
            start_date = end_date - timedelta(days=7)
        elif period == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif period == "This Month":
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "Last Month":
            if end_date.month == 1:
                start_date = end_date.replace(year=end_date.year-1, month=12, day=1)
            else:
                start_date = end_date.replace(month=end_date.month-1, day=1)
        else:  # Custom - default to last 7 days
            start_date = end_date - timedelta(days=7)
            
        return start_date, end_date
        
    def update_sales_reports(self):
        """Update sales reports with current data"""
        start_date, end_date = self.get_date_range()
        
        # Get sales data from database
        query = """
        SELECT 
            DATE(created_at) as sale_date,
            COUNT(*) as num_orders,
            SUM(total_amount) as total_sales,
            AVG(total_amount) as avg_order
        FROM orders 
        WHERE created_at BETWEEN %s AND %s
        GROUP BY DATE(created_at)
        ORDER BY sale_date
        """
        
        results = self.db.execute_query(query, (start_date, end_date), fetch=True)
        
        if results:
            # Update sales graph
            self.sales_figure.clear()
            ax = self.sales_figure.add_subplot(111)
            
            dates = [r['sale_date'] for r in results]
            sales = [r['total_sales'] for r in results]
            
            ax.plot(dates, sales, marker='o')
            ax.set_title('Daily Sales')
            ax.set_xlabel('Date')
            ax.set_ylabel('Sales ($)')
            ax.tick_params(axis='x', rotation=45)
            
            self.sales_figure.tight_layout()
            self.sales_canvas.draw()
            
            # Update product table
            product_query = """
            SELECT 
                p.name as product_name,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.price * oi.quantity) as total_revenue,
                SUM((oi.price - p.cost) * oi.quantity) as total_profit
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.created_at BETWEEN %s AND %s
            GROUP BY p.product_id, p.name
            ORDER BY total_revenue DESC
            """
            
            products = self.db.execute_query(product_query, (start_date, end_date), fetch=True)
            
            self.product_table.delete(*self.product_table.get_children())
            if products:
                for product in products:
                    self.product_table.insert('', 'end', values=(
                        product['product_name'],
                        product['total_quantity'],
                        f"${product['total_revenue']:.2f}",
                        f"${product['total_profit']:.2f}"
                    ))
                    
    def update_customer_analytics(self):
        """Update customer analytics with current data"""
        start_date, end_date = self.get_date_range()
        
        # Get customer segments data
        segments_query = """
        SELECT 
            CASE 
                WHEN total_spent >= 500 THEN 'VIP'
                WHEN total_spent >= 200 THEN 'Regular'
                ELSE 'Occasional'
            END as segment,
            COUNT(*) as customer_count
        FROM customers
        GROUP BY segment
        """
        
        segments = self.db.execute_query(segments_query, None, fetch=True)
        
        if segments:
            # Update segments pie chart
            self.segments_figure.clear()
            ax = self.segments_figure.add_subplot(111)
            
            labels = [s['segment'] for s in segments]
            sizes = [s['customer_count'] for s in segments]
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
            ax.set_title('Customer Segments')
            
            self.segments_figure.tight_layout()
            self.segments_canvas.draw()
            
        # Get visit frequency data
        frequency_query = """
        SELECT 
            customer_id,
            COUNT(*) as visit_count
        FROM orders
        WHERE created_at BETWEEN %s AND %s
        GROUP BY customer_id
        """
        
        frequencies = self.db.execute_query(frequency_query, (start_date, end_date), fetch=True)
        
        if frequencies:
            # Update frequency histogram
            self.frequency_figure.clear()
            ax = self.frequency_figure.add_subplot(111)
            
            visits = [f['visit_count'] for f in frequencies]
            
            ax.hist(visits, bins=range(1, max(visits) + 2))
            ax.set_title('Visit Frequency')
            ax.set_xlabel('Number of Visits')
            ax.set_ylabel('Number of Customers')
            
            self.frequency_figure.tight_layout()
            self.frequency_canvas.draw()
            
    def update_inventory_analytics(self):
        """Update inventory analytics with current data"""
        # Get current inventory levels
        query = """
        SELECT 
            i.name as item_name,
            i.current_stock,
            i.min_stock,
            i.last_ordered,
            CASE
                WHEN i.current_stock = 0 THEN 'Out of Stock'
                WHEN i.current_stock < i.min_stock THEN 'Low Stock'
                ELSE 'In Stock'
            END as status
        FROM inventory i
        ORDER BY 
            CASE 
                WHEN i.current_stock = 0 THEN 1
                WHEN i.current_stock < i.min_stock THEN 2
                ELSE 3
            END,
            i.name
        """
        
        inventory = self.db.execute_query(query, None, fetch=True)
        
        if inventory:
            # Update inventory levels graph
            self.inventory_figure.clear()
            ax = self.inventory_figure.add_subplot(111)
            
            items = [i['item_name'] for i in inventory]
            current = [i['current_stock'] for i in inventory]
            minimum = [i['min_stock'] for i in inventory]
            
            x = range(len(items))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], current, width, label='Current Stock')
            ax.bar([i + width/2 for i in x], minimum, width, label='Minimum Stock')
            
            ax.set_ylabel('Stock Level')
            ax.set_title('Inventory Levels')
            ax.set_xticks(x)
            ax.set_xticklabels(items, rotation=45, ha='right')
            ax.legend()
            
            self.inventory_figure.tight_layout()
            self.inventory_canvas.draw()
            
            # Update inventory table
            self.inventory_table.delete(*self.inventory_table.get_children())
            for item in inventory:
                self.inventory_table.insert('', 'end', values=(
                    item['item_name'],
                    item['current_stock'],
                    item['min_stock'],
                    item['status'],
                    item['last_ordered'].strftime('%Y-%m-%d') if item['last_ordered'] else 'Never'
                ))
