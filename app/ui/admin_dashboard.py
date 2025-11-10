import tkinter as tk
from tkinter import messagebox

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
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
        self.window.geometry("1270x790")
        self.window.resizable(True, True)
        # Center the dashboard on screen
        try:
            self.window.update_idletasks()
            width, height = 1270, 790
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
        self.graph_canvas = None
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
        """Create admin-specific content with sidebar navigation"""
        content_frame = tk.Frame(self.window, bg=self.bg_color)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Sidebar for primary actions
        sidebar_frame = tk.Frame(content_frame, bg="#3B2A1F", width=220)
        sidebar_frame.pack(side='left', fill='y', padx=(0, 15))
        sidebar_frame.pack_propagate(False)
        
        sidebar_title = tk.Label(
            sidebar_frame,
            text="Admin Tools",
            font=("Arial", 14, "bold"),
            bg="#3B2A1F",
            fg=self.accent_color
        )
        sidebar_title.pack(anchor='w', padx=20, pady=(20, 10))
        
        # Content area on the right
        self.detail_frame = tk.Frame(content_frame, bg=self.card_bg)
        self.detail_frame.pack(side='left', fill='both', expand=True)
        
        self.detail_header_frame = tk.Frame(self.detail_frame, bg=self.card_bg)
        self.detail_header_frame.pack(fill='x', padx=30, pady=(30, 10))
        
        self.detail_title = tk.Label(
            self.detail_header_frame,
            text="Welcome to the Administrator Dashboard",
            font=("Arial", 18, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
            anchor='w',
            justify='left',
            wraplength=520
        )
        self.detail_title.pack(fill='x')
        
        self.detail_description = tk.Label(
            self.detail_header_frame,
            text=(
                "Use the tools on the left to manage products, inventory, sales, "
                "and reports. Selected tool details and shortcuts will appear here."
            ),
            font=("Arial", 12),
            bg=self.card_bg,
            fg="#5C4A3A",
            anchor='w',
            justify='left',
            wraplength=540
        )
        self.detail_description.pack(fill='x', pady=(10, 0))
        
        self.detail_hint = tk.Label(
            self.detail_header_frame,
            text="Tip: Double-check inventory levels before publishing product updates.",
            font=("Arial", 10, "italic"),
            bg=self.card_bg,
            fg="#7A6757",
            anchor='w',
            justify='left',
            wraplength=540
        )
        self.detail_hint.pack(fill='x', pady=(10, 0))

        self.graph_button_frame = tk.Frame(self.detail_frame, bg=self.card_bg)
        self.graph_button_frame.pack(fill='x', padx=30, pady=(0, 10))
        self._add_graph_button(
            "Sales Overview",
            "Last 7 days of sales totals",
            lambda: self._show_graph("sales")
        )
        self._add_graph_button(
            "Inventory Levels",
            "Top items by current stock",
            lambda: self._show_graph("inventory")
        )
        self._add_graph_button(
            "Top Products",
            "Best-selling products",
            lambda: self._show_graph("top_products")
        )
        
        self.detail_content_frame = tk.Frame(self.detail_frame, bg=self.card_bg)
        self.detail_content_frame.pack(fill='both', expand=True, padx=10, pady=12)
        
        self._show_default_detail()
        
        # Sidebar navigation buttons
        self.create_sidebar_button(
            sidebar_frame,
            title="Dashboard Overview",
            command=self._show_default_detail,
            detail_title="Dashboard Overview",
            detail_description=(
                "Monitor BigBrew at a glance. Explore sales, inventory, and product performance "
                "graphs to stay ahead of daily operations."
            ),
            detail_hint="Use the buttons above to switch between dashboard charts.",
            renderer=None,
        )

        self.create_sidebar_button(
            sidebar_frame,
            title="Product Management",
            command=self.manage_products,
            detail_title="Product Management",
            detail_description=(
                "Maintain the BigBrew catalog. Update pricing, descriptions, and availability "
                "for milk tea flavors and specialty coffee drinks."
            ),
            detail_hint="Remember to sync changes with inventory to avoid stock mismatches.",
            renderer=lambda container: self.manage_products(parent=container)
        )
        
        self.create_sidebar_button(
            sidebar_frame,
            title="Inventory Management",
            command=self.manage_inventory,
            detail_title="Inventory Management",
            detail_description=(
                "Monitor ingredient availability, receive deliveries, and configure low-stock "
                "alerts to keep operations running smoothly."
            ),
            detail_hint="Review weekly usage trends before ordering new supplies.",
            renderer=lambda container: self.manage_inventory(parent=container)
        )
        
        self.create_sidebar_button(
            sidebar_frame,
            title="Sales Management",
            command=self.manage_sales,
            detail_title="Sales Management",
            detail_description=(
                "Analyze daily sales, process adjustments, and review payment summaries "
                "for comprehensive oversight."
            ),
            detail_hint="Export a CSV summary for accounting every Friday.",
            renderer=lambda container: self.manage_sales(parent=container)
        )
        
        self.create_sidebar_button(
            sidebar_frame,
            title="Reports & Analytics",
            command=self.view_reports,
            detail_title="Reports & Analytics",
            detail_description=(
                "Explore sales trends, product performance, and inventory turnover to make "
                "data-driven decisions."
            ),
            detail_hint="Compare month-over-month growth to track seasonal campaigns.",
            renderer=None
        )

    def create_sidebar_button(
        self,
        parent,
        title,
        command,
        detail_title,
        detail_description,
        detail_hint,
        renderer,
    ):
        """Create a sidebar navigation entry"""
        container = tk.Frame(parent, bg="#3B2A1F")
        container.pack(fill='x', padx=15, pady=8)
        
        button = tk.Button(
            container,
            text=title,
            font=("Arial", 12, "bold"),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            activebackground="#B45818",
            activeforeground=self.text_color,
            height=2,
            command=lambda: self._handle_sidebar_action(
                command,
                detail_title,
                detail_description,
                detail_hint,
                renderer
            )
        )
        button.pack(fill='x')
        
    def _add_graph_button(self, title, tooltip, command):
        """Create a graph selector button"""
        container = tk.Frame(self.graph_button_frame, bg=self.card_bg)
        container.pack(side='left', padx=(0, 18))

        button = tk.Button(
            container,
            text=title,
            font=("Arial", 11, "bold"),
            bg=self.button_color,
            fg=self.text_color,
            relief='flat',
            bd=0,
            padx=16,
            pady=8,
            activebackground="#B45818",
            activeforeground=self.text_color,
            command=command,
        )
        button.pack(fill='x')
        
        hint = tk.Label(
            container,
            text=tooltip,
            font=("Arial", 9),
            bg=self.card_bg,
            fg="#7A6757",
            wraplength=140,
            justify='center'
        )
        hint.pack(pady=(4, 0))

    def _clear_detail_content(self):
        """Remove existing widgets/graphs from the detail panel"""
        if getattr(self, "graph_canvas", None):
            try:
                self.graph_canvas.get_tk_widget().destroy()
            except Exception:
                pass
            self.graph_canvas = None
        for child in self.detail_content_frame.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

    def _show_default_detail(self):
        """Display the default welcome message in detail panel"""
        self.detail_header_frame.pack(fill='x', padx=30, pady=(30, 10))
        self.graph_button_frame.pack(fill='x', padx=30, pady=(0, 10))
        self.detail_title.config(text="Welcome to the Administrator Dashboard")
        self.detail_description.config(
            text=(
                "Use the tools on the left to manage products, inventory, sales, "
                "and reports. Selected tool details and shortcuts will appear here."
            )
        )
        self.detail_hint.config(
            text="Tip: Double-check inventory levels before publishing product updates."
        )
        self._clear_detail_content()
        self.detail_content_frame.configure(bg=self.card_bg)
        placeholder = tk.Label(
            self.detail_content_frame,
            text="Select a graph button above or choose a management module from the sidebar.",
            font=("Arial", 12),
            bg=self.card_bg,
            fg="#5C4A3A",
            anchor='center',
            justify='center',
            wraplength=520,
        )
        placeholder.pack(expand=True)

    def _show_graph(self, graph_type):
        """Render a graph in the detail panel"""
        graph_meta = {
            "sales": {
                "title": "Sales Overview",
                "description": "Daily sales totals for the last 7 days.",
                "hint": "Identify peak days and plan staffing accordingly.",
                "chart": "line",
                "color": "#D2691E",
                "ylabel": "Total Sales (₱)",
            },
            "inventory": {
                "title": "Inventory Levels",
                "description": "Current stock for the top 10 products.",
                "hint": "Restock items before they dip into the low threshold.",
                "chart": "bar",
                "color": "#8B4513",
                "ylabel": "Available Units",
            },
            "top_products": {
                "title": "Top Products",
                "description": "Best-selling products based on recent sales volume.",
                "hint": "Feature these items in promotions to boost repeat purchases.",
                "chart": "bar",
                "color": "#A0522D",
                "ylabel": "Units Sold",
            },
        }

        meta = graph_meta.get(graph_type)
        if not meta:
            return

        self.detail_header_frame.pack(fill='x', padx=30, pady=(30, 10))
        self.graph_button_frame.pack(fill='x', padx=30, pady=(0, 10))
        self.detail_title.config(text=meta["title"])
        self.detail_description.config(text=meta["description"])
        self.detail_hint.config(text=meta["hint"])

        self._clear_detail_content()
        self.detail_content_frame.configure(bg=self.card_bg)

        data = self._get_graph_data(graph_type)

        if not MATPLOTLIB_AVAILABLE:
            message = (
                "Matplotlib is not installed. Please install it to view charts:\n"
                "`pip install matplotlib`"
            )
            tk.Label(
                self.detail_content_frame,
                text=message,
                font=("Arial", 11),
                bg=self.card_bg,
                fg="#7A6757",
                justify='left',
                wraplength=520,
            ).pack(fill='both', expand=True, padx=10, pady=10)
            return

        if not data or not data["labels"]:
            tk.Label(
                self.detail_content_frame,
                text="No data available yet for this chart.",
                font=("Arial", 12, "italic"),
                bg=self.card_bg,
                fg="#7A6757",
            ).pack(fill='both', expand=True, padx=10, pady=10)
            return

        figure = Figure(figsize=(5.6, 3.6), dpi=100)
        ax = figure.add_subplot(111)

        labels = data["labels"]
        values = data["values"]

        x_positions = list(range(len(labels)))

        if meta["chart"] == "line":
            ax.plot(x_positions, values, marker='o', linewidth=2, color=meta["color"])
        else:
            ax.bar(x_positions, values, color=meta["color"])

        ax.set_ylabel(meta["ylabel"])
        ax.set_xticks(x_positions)
        ax.set_xticklabels(labels, rotation=25, ha='right')
        ax.grid(True, axis='y', linestyle='--', linewidth=0.5, alpha=0.5)
        ax.set_facecolor("#F8F1D4")
        figure.patch.set_facecolor(self.card_bg)
        figure.tight_layout()

        self.graph_canvas = FigureCanvasTkAgg(figure, master=self.detail_content_frame)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(fill='both', expand=True)

    def _get_graph_data(self, graph_type):
        """Fetch data for the requested graph type"""
        cursor = None
        try:
            conn = getattr(self.login_window, "get_db_connection", lambda: None)()
            if not conn:
                return None

            cursor = conn.cursor(dictionary=True)

            if graph_type == "sales":
                schema = self._get_sales_schema()
                sale_date_col = schema["sale_date"]
                total_amount_col = schema["total_amount"]
                query = f"""
                    SELECT DATE(s.{sale_date_col}) AS label,
                           COALESCE(SUM(s.{total_amount_col}), 0) AS total
                    FROM sales s
                    WHERE s.{sale_date_col} >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
                    GROUP BY DATE(s.{sale_date_col})
                    ORDER BY DATE(s.{sale_date_col})
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                labels = [row["label"].strftime("%b %d") if hasattr(row["label"], "strftime") else str(row["label"]) for row in rows]
                values = [float(row["total"] or 0) for row in rows]
                return {"labels": labels, "values": values}

            if graph_type == "inventory":
                schema = self._get_schema()
                prod_id = schema["prod_id"]
                prod_name = schema["prod_name"]
                inv_qty = schema["inv_qty"]
                inv_prod_fk = schema["inv_prod_fk"]
                query = f"""
                    SELECT COALESCE(p.{prod_name}, 'Unknown') AS label,
                           COALESCE(i.{inv_qty}, 0) AS total
                    FROM products p
                    LEFT JOIN inventory i ON p.{prod_id} = i.{inv_prod_fk}
                    ORDER BY total DESC
                    LIMIT 10
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                labels = [str(row["label"]) for row in rows]
                values = [int(row["total"] or 0) for row in rows]
                return {"labels": labels, "values": values}

            if graph_type == "top_products":
                schema = self._get_sales_schema()
                sale_item_qty = schema["sale_item_qty"]
                sale_item_product_fk = schema["sale_item_product_fk"]
                product_name_col = schema["product_name"]
                product_id_col = schema["product_id"]
                query = f"""
                    SELECT COALESCE(p.{product_name_col}, 'Unknown') AS label,
                           COALESCE(SUM(si.{sale_item_qty}), 0) AS total
                    FROM sale_items si
                    JOIN products p ON si.{sale_item_product_fk} = p.{product_id_col}
                    GROUP BY p.{product_id_col}, p.{product_name_col}
                    ORDER BY total DESC
                    LIMIT 10
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                labels = [str(row["label"]) for row in rows]
                values = [int(row["total"] or 0) for row in rows]
                return {"labels": labels, "values": values}

        except Exception as exc:
            print(f"[Dashboard] Failed to load graph data ({graph_type}): {exc}")
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass

    def _handle_sidebar_action(self, action, title, description, hint, renderer):
        """Run the selected action and update detail panel"""
        if renderer:
            self.detail_header_frame.pack_forget()
            self.graph_button_frame.pack_forget()
            self._clear_detail_content()
            self.detail_content_frame.configure(bg=self.bg_color)
            try:
                renderer(self.detail_content_frame)
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to display {title}: {exc}")
                self._show_default_detail()
        else:
            self.detail_header_frame.pack(fill='x', padx=30, pady=(30, 10))
            self.graph_button_frame.pack(fill='x', padx=30, pady=(0, 10))
            self.detail_title.config(text=title)
            self.detail_description.config(text=description)
            self.detail_hint.config(text=hint)
            self._clear_detail_content()
            self.detail_content_frame.configure(bg=self.card_bg)
            if action:
                try:
                    action()
                except Exception as exc:
                    messagebox.showerror("Error", f"Failed to open {title}: {exc}")
    
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
