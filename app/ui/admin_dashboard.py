import tkinter as tk
from tkinter import messagebox, ttk

import bcrypt

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.ticker import FuncFormatter

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    FuncFormatter = None
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
        sidebar_title.pack(anchor='w', padx=40, pady=(40, 20))
        
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
        
        self.detail_description = None
        self.detail_hint = None

        self.graph_button_frame = None
        self.detail_content_frame = tk.Frame(self.detail_frame, bg=self.card_bg)
        self.detail_content_frame.pack(fill='both', expand=True, padx=10, pady=12)
        
        self._show_default_detail()
        
        # Sidebar navigation buttons
        self.create_sidebar_button(
            sidebar_frame,
            title="Dashboard Overview",
            command=self._show_default_detail,
            detail_title="Dashboard Overview",
            detail_description="",
            detail_hint="",
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
            title="User Management",
            command=self.manage_users,
            detail_title="User Management",
            detail_description=(
                "Add, edit, and deactivate staff accounts. Assign appropriate roles and reset credentials."
            ),
            detail_hint="Always enforce least-privilege access for security.",
            renderer=lambda container: self.manage_users(parent=container)
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
        
    def _clear_detail_content(self):
        """Remove existing widgets/graphs from the detail panel"""
        for attr in ("graph_canvas", "user_panel", "info_panel"):
            obj = getattr(self, attr, None)
            if obj is None:
                continue
            try:
                widget = obj.get_tk_widget() if hasattr(obj, "get_tk_widget") else obj
                widget.destroy()
            except Exception:
                pass
            setattr(self, attr, None)
        for child in self.detail_content_frame.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

    def manage_users(self, parent=None):
        container = parent or self.detail_content_frame

        self._clear_detail_content()

        tree_container = tk.Frame(container, bg=self.card_bg)
        tree_container.pack(fill='both', expand=True)

        columns = ("username", "name", "email", "role", "status", "last_login")
        self.user_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=12,
        )

        headings = {
            "username": "Username",
            "name": "Name",
            "email": "Email",
            "role": "Role",
            "status": "Status",
            "last_login": "Last Login",
        }

        for col, title in headings.items():
            self.user_tree.heading(col, text=title)
            anchor = "w" if col in ("username", "name", "email") else "center"
            width = 180 if col == "email" else 140
            if col == "last_login":
                width = 160
            self.user_tree.column(col, anchor=anchor, width=width)

        self.user_tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.user_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.user_tree.configure(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(container, bg=self.card_bg)
        button_frame.pack(fill='x', pady=(12, 0))

        button_specs = [
            ("▶", "Add User", "#28A745", "white", self._open_add_user_dialog),
            ("✏️", "Edit User", self.button_color, self.text_color, self._open_edit_user_dialog),
            ("🔐", "Reset Password", "#6C757D", "white", self._open_reset_password_dialog),
            ("🔁", "Activate/Deactivate", "#DC3545", "white", self._toggle_user_status),
        ]

        for icon, label, bg_color, fg_color, command in button_specs:
            btn = tk.Button(
                button_frame,
                text=f"{icon}  {label}",
                font=("Arial", 11),
                bg=bg_color,
                fg=fg_color,
                relief="flat",
                width=18,
                command=command,
                padx=4,
                pady=6,
            )
            btn.pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="🔄  Refresh",
            font=("Arial", 11),
            bg="#6C757D",
            fg="white",
            relief="flat",
            width=12,
            command=self._refresh_user_list,
            padx=4,
            pady=6,
        ).pack(side='right', padx=5)

        self._user_records = {}
        self._refresh_user_list()

    def _get_app_connection(self):
        getter = getattr(self.login_window, "get_db_connection", None)
        if callable(getter):
            return getter()
        return None

    def _load_users(self):
        connection = self._get_app_connection()
        if not connection:
            messagebox.showerror("Database Error", "Unable to connect to the database.")
            return []
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT user_id, username, email, user_type, first_name, last_name, is_active, last_login
                FROM users
                ORDER BY created_at DESC
                """
            )
            return cursor.fetchall()
        except Exception as exc:
            messagebox.showerror("Database Error", f"Failed to load users: {exc}")
            return []
        finally:
            if cursor:
                cursor.close()

    def _refresh_user_list(self):
        if not hasattr(self, "user_tree"):
            return
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)

        users = self._load_users()
        self._user_records = {}
        for user in users:
            user_id = user["user_id"]
            name = f"{user.get('first_name') or ''} {user.get('last_name') or ''}".strip() or "—"
            status = "Active" if user.get("is_active") else "Inactive"
            last_login = user.get("last_login")
            if last_login and hasattr(last_login, "strftime"):
                last_login = last_login.strftime("%Y-%m-%d %H:%M")
            elif not last_login:
                last_login = "—"
            values = (
                user.get("username") or "—",
                name,
                user.get("email") or "—",
                user.get("user_type") or "—",
                status,
                last_login,
            )
            self.user_tree.insert("", tk.END, iid=str(user_id), values=values)
            self._user_records[user_id] = user

    def _get_selected_user(self):
        if not hasattr(self, "user_tree"):
            return None
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user first.")
            return None
        user_id = int(selection[0])
        return self._user_records.get(user_id)

    def _open_add_user_dialog(self):
        self._open_user_form_dialog("Add User")

    def _open_edit_user_dialog(self):
        user = self._get_selected_user()
        if user:
            self._open_user_form_dialog("Edit User", user)

    def _open_user_form_dialog(self, title, user=None):
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.configure(bg=self.card_bg)
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        try:
            dialog.update_idletasks()
            width, height = 420, (380 if user else 450)
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            dialog.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

        form = tk.Frame(dialog, bg=self.card_bg)
        form.pack(fill='both', expand=True, padx=20, pady=20)

        entries = {}

        def add_field(label, key, row, show=None):
            tk.Label(
                form, text=label, font=("Arial", 11), bg=self.card_bg, fg="#4A3728"
            ).grid(row=row, column=0, sticky='w', pady=6)
            entry = tk.Entry(form, font=("Arial", 11), show=show)
            entry.grid(row=row, column=1, sticky='ew', pady=6)
            entries[key] = entry

        form.columnconfigure(1, weight=1)

        add_field("Username:", "username", 0)
        add_field("Email:", "email", 1)
        add_field("First Name:", "first_name", 2)
        add_field("Last Name:", "last_name", 3)

        tk.Label(
            form, text="Role:", font=("Arial", 11), bg=self.card_bg, fg="#4A3728"
        ).grid(row=4, column=0, sticky='w', pady=6)
        role_var = tk.StringVar(value="staff")
        role_combo = ttk.Combobox(
            form,
            textvariable=role_var,
            values=["admin", "staff", "inventory_manager"],
            state="readonly",
            font=("Arial", 11),
        )
        role_combo.grid(row=4, column=1, sticky='ew', pady=6)

        if user is None:
            add_field("Password:", "password", 5, show="*")
            add_field("Confirm Password:", "confirm_password", 6, show="*")
        else:
            tk.Label(
                form,
                text="Use 'Reset Password' to update credentials.",
                font=("Arial", 9, "italic"),
            bg=self.card_bg,
                fg="#7A6757",
            ).grid(row=5, column=0, columnspan=2, sticky='w', pady=(8, 0))

        if user:
            entries["username"].insert(0, user.get("username") or "")
            entries["email"].insert(0, user.get("email") or "")
            entries["first_name"].insert(0, user.get("first_name") or "")
            entries["last_name"].insert(0, user.get("last_name") or "")
            role_var.set(user.get("user_type") or "staff")

        def submit():
            username = entries["username"].get().strip()
            email = entries["email"].get().strip()
            first_name = entries["first_name"].get().strip() or None
            last_name = entries["last_name"].get().strip() or None
            role = role_var.get()

            if not username or not email:
                messagebox.showerror("Validation Error", "Username and email are required.")
                return

            connection = self._get_app_connection()
            if not connection:
                messagebox.showerror("Database Error", "Unable to connect to the database.")
                return

            cursor = connection.cursor()
            try:
                if user is None:
                    password = entries["password"].get()
                    confirm_password = entries["confirm_password"].get()
                    if len(password) < 6:
                        messagebox.showerror("Validation Error", "Password must be at least 6 characters long.")
                        return
                    if password != confirm_password:
                        messagebox.showerror("Validation Error", "Passwords do not match.")
                        return
                    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    cursor.execute(
                        """
                        INSERT INTO users (username, email, password_hash, user_type, first_name, last_name, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, 1)
                        """,
                        (username, email, password_hash, role, first_name, last_name),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE users
                        SET username = %s,
                            email = %s,
                            user_type = %s,
                            first_name = %s,
                            last_name = %s
                        WHERE user_id = %s
                        """,
                        (username, email, role, first_name, last_name, user["user_id"]),
                    )
                connection.commit()
                messagebox.showinfo("Success", f"User {'created' if user is None else 'updated'} successfully.")
                dialog.destroy()
                self._refresh_user_list()
            except Exception as exc:
                connection.rollback()
                messagebox.showerror("Database Error", f"Failed to save user: {exc}")
            finally:
                cursor.close()

        button_row = tk.Frame(dialog, bg=self.card_bg)
        button_row.pack(fill='x', padx=20, pady=(0, 15))

        tk.Button(
            button_row,
            text="Save",
            font=("Arial", 11, "bold"),
            bg="#28A745",
            fg="white",
            relief="flat",
            width=12,
            command=submit,
        ).pack(side='left', padx=5)

        tk.Button(
            button_row,
            text="Cancel",
            font=("Arial", 11),
            bg="#6C757D",
            fg="white",
            relief="flat",
            width=12,
            command=dialog.destroy,
        ).pack(side='right', padx=5)

    def _toggle_user_status(self):
        user = self._get_selected_user()
        if not user:
            return
        new_status = 0 if user.get("is_active") else 1
        action = "deactivate" if user.get("is_active") else "activate"

        if not messagebox.askyesno("Confirm", f"Are you sure you want to {action} {user.get('username')}?"):
            return

        connection = self._get_app_connection()
        if not connection:
            messagebox.showerror("Database Error", "Unable to connect to the database.")
            return
        cursor = connection.cursor()
        try:
            cursor.execute(
                "UPDATE users SET is_active = %s WHERE user_id = %s",
                (new_status, user["user_id"]),
            )
            connection.commit()
            messagebox.showinfo("Success", f"User has been {'deactivated' if new_status == 0 else 'activated'}.")
            self._refresh_user_list()
        except Exception as exc:
            connection.rollback()
            messagebox.showerror("Database Error", f"Failed to update status: {exc}")
        finally:
            cursor.close()

    def _open_reset_password_dialog(self):
        user = self._get_selected_user()
        if not user:
            return

        dialog = tk.Toplevel(self.window)
        dialog.title(f"Reset Password - {user.get('username')}")
        dialog.configure(bg=self.card_bg)
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        try:
            dialog.update_idletasks()
            width, height = 380, 240
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            dialog.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

        frame = tk.Frame(dialog, bg=self.card_bg)
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(
            frame,
            text=f"Reset password for {user.get('username')}",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor='w', pady=(0, 12))

        tk.Label(
            frame, text="New Password:", font=("Arial", 11), bg=self.card_bg, fg="#4A3728"
        ).pack(anchor='w')
        password_entry = tk.Entry(frame, font=("Arial", 11), show="*")
        password_entry.pack(fill='x', pady=(0, 10))

        tk.Label(
            frame, text="Confirm Password:", font=("Arial", 11), bg=self.card_bg, fg="#4A3728"
        ).pack(anchor='w')
        confirm_entry = tk.Entry(frame, font=("Arial", 11), show="*")
        confirm_entry.pack(fill='x', pady=(0, 10))

        def reset_password():
            password = password_entry.get()
            confirm_password = confirm_entry.get()
            if len(password) < 6:
                messagebox.showerror("Validation Error", "Password must be at least 6 characters long.")
                return
            if password != confirm_password:
                messagebox.showerror("Validation Error", "Passwords do not match.")
                return

            connection = self._get_app_connection()
            if not connection:
                messagebox.showerror("Database Error", "Unable to connect to the database.")
                return

            cursor = connection.cursor()
            try:
                password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE user_id = %s",
                    (password_hash, user["user_id"]),
                )
                connection.commit()
                messagebox.showinfo("Success", "Password reset successfully.")
                dialog.destroy()
            except Exception as exc:
                connection.rollback()
                messagebox.showerror("Database Error", f"Failed to reset password: {exc}")
            finally:
                cursor.close()

        button_bar = tk.Frame(dialog, bg=self.card_bg)
        button_bar.pack(fill='x', padx=20, pady=(0, 15))

        tk.Button(
            button_bar,
            text="Reset Password",
            font=("Arial", 11, "bold"),
            bg="#28A745",
            fg="white",
            relief="flat",
            width=14,
            command=reset_password,
        ).pack(side='left', padx=5)

        tk.Button(
            button_bar,
            text="Cancel",
            font=("Arial", 11),
            bg="#6C757D",
            fg="white",
            relief="flat",
            width=12,
            command=dialog.destroy,
        ).pack(side='right', padx=5)

    def _show_default_detail(self):
        """Display the default welcome message in detail panel"""
        self.detail_title.config(text="Executive Overview")
        self._clear_detail_content()
        self.detail_content_frame.configure(bg=self.card_bg)
        self._render_dashboard_overview()

    def _build_chart_figure(self, graph_type):
        """Build a matplotlib figure for the requested chart"""
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

        data = self._get_graph_data(graph_type)

        if not MATPLOTLIB_AVAILABLE:
            figure = Figure(figsize=(4.5, 3.0), dpi=100)
            ax = figure.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                "Matplotlib not installed.\nInstall with `pip install matplotlib`.",
                ha="center",
                va="center",
                fontsize=10,
                color="#7A6757",
            )
            ax.axis('off')
            figure.patch.set_facecolor(self.card_bg)
            return figure

        figure = Figure(figsize=(4.5, 3.0), dpi=100)
        ax = figure.add_subplot(111)

        labels = data.get("labels") if data else []
        values = data.get("values") if data else []

        if not labels:
            ax.text(
                0.5,
                0.5,
                "No data available yet for this chart.",
                ha="center",
                va="center",
                fontsize=11,
                color="#7A6757",
            )
            ax.axis('off')
            figure.patch.set_facecolor(self.card_bg)
            return figure

        x_positions = list(range(len(labels)))

        if meta["chart"] == "line":
            ax.plot(x_positions, values, marker='o', linewidth=2, color=meta["color"])
        else:
            ax.bar(x_positions, values, color=meta["color"])

        if graph_type == "sales" and FuncFormatter:
            ax.yaxis.set_major_formatter(FuncFormatter(lambda val, _: f"₱{val:,.0f}"))

        ax.set_ylabel(meta["ylabel"])
        ax.set_xticks(x_positions)
        ax.set_xticklabels(labels, rotation=90, ha='center')
        ax.grid(True, axis='y', linestyle='--', linewidth=0.5, alpha=0.5)
        ax.set_facecolor("#F8F1D4")
        figure.patch.set_facecolor(self.card_bg)
        figure.tight_layout()

        return figure

    def _calculate_summary_values(self):
        sales_data = self._get_graph_data("sales") or {"values": []}
        sales_values = sales_data.get("values", [])
        total_sales = sum(sales_values)
        avg_sales = total_sales / len(sales_values) if sales_values else 0.0

        inventory_data = self._get_graph_data("inventory") or {"values": []}
        inventory_values = inventory_data.get("values", [])
        total_stock = sum(inventory_values) if inventory_values else 0.0

        return total_sales, avg_sales, total_stock

    def _calculate_summary_values(self):
        sales_data = self._get_graph_data("sales") or {"values": []}
        sales_values = sales_data.get("values", [])
        total_sales = sum(sales_values)
        avg_sales = total_sales / len(sales_values) if sales_values else 0.0

        inventory_data = self._get_graph_data("inventory") or {"values": []}
        inventory_values = inventory_data.get("values", [])
        total_stock = sum(inventory_values) if inventory_values else 0.0

        return total_sales, avg_sales, total_stock

    def _render_dashboard_overview(self):
        """Render all dashboard charts simultaneously."""
        total_sales, avg_sales, total_stock = self._calculate_summary_values()

        summary_frame = tk.Frame(self.detail_content_frame, bg=self.card_bg)
        summary_frame.pack(fill='x', pady=(0, 12))

        summary_specs = [
            ("Total Sales (₱)", f"₱{total_sales:,.2f}"),
            ("Average Daily Sales", f"₱{avg_sales:,.2f}"),
            ("Total Stock On-hand", f"{total_stock:,.0f} units"),
        ]

        for idx, (title, value) in enumerate(summary_specs):
            card = tk.Frame(summary_frame, bg="#FFF8DC", bd=1, relief='solid')
            card.pack(side='left', expand=True, fill='both', padx=6)
            tk.Label(
                card, text=title, font=("Arial", 11, "bold"), bg="#FFF8DC", fg="#4A3728"
            ).pack(anchor='w', padx=15, pady=(12, 4))
            tk.Label(
                card, text=value, font=("Arial", 16, "bold"), bg="#FFF8DC", fg="#B85C2D"
            ).pack(anchor='w', padx=15, pady=(0, 12))

        container = tk.Frame(self.detail_content_frame, bg=self.card_bg)
        container.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        charts_frame = tk.Frame(self.detail_content_frame, bg=self.card_bg)
        charts_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.columnconfigure(1, weight=1)
        charts_frame.columnconfigure(2, weight=1)

        sales_data = self._get_graph_data("sales") or {"values": []}
        total_sales = sum(sales_data.get("values", []))
        daily_count = len(sales_data.get("values", [])) or 1
        avg_sales = total_sales / daily_count

        inventory_data = self._get_graph_data("inventory") or {"values": []}
        total_stock = sum(inventory_data.get("values", []))


        chart_specs = [
            ("Sales Trend", "sales"),
            ("Inventory Health", "inventory"),
            ("Top Selling Products", "top_products"),
        ]

        for idx, (title, key) in enumerate(chart_specs):
            card = tk.Frame(charts_frame, bg="#FFF8DC", bd=1, relief='solid')
            card.grid(row=0, column=idx, padx=6, pady=8, sticky='nsew')

            tk.Label(
                card, text=title, font=("Arial", 12, "bold"), bg="#FFF8DC", fg="#4A3728"
            ).pack(anchor='w', padx=12, pady=(10, 5))

            figure = self._build_chart_figure(key)
            chart_canvas = FigureCanvasTkAgg(figure, master=card)
            chart_canvas.draw()
            chart_canvas.get_tk_widget().pack(fill='both', expand=True, padx=8, pady=8)

        data = self._get_graph_data("top_products") or {"labels": [], "values": []}
        labels = data.get("labels", [])
        values = data.get("values", [])

        table_frame = tk.Frame(self.detail_content_frame, bg=self.card_bg)
        table_frame.pack(fill='x', pady=(0, 12))

        tk.Label(
            table_frame,
            text="Top Products Snapshot",
            font=("Arial", 12, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor='w', pady=(0, 6))

        summary_text = ""
        if labels:
            lines = [f"• {label}: {int(qty)} units sold" for label, qty in zip(labels, values)]
            summary_text = "\n".join(lines)
        else:
            summary_text = "No sales data yet."

        tk.Label(
            table_frame,
            text=summary_text,
            font=("Arial", 11),
            bg=self.card_bg,
            fg="#5C4A3A",
            justify='left',
        ).pack(anchor='w')

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
        header_packed = bool(self.detail_header_frame.winfo_manager())
        if not header_packed or self.detail_header_frame.winfo_y() != 30:
            self.detail_header_frame.pack_forget()
            self.detail_header_frame.pack(fill='x', padx=30, pady=(30, 10))

        if renderer:
            self.detail_title.config(text=title)
            self._clear_detail_content()
            self.detail_content_frame.configure(bg=self.card_bg)
            try:
                renderer(self.detail_content_frame)
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to display {title}: {exc}")
                self._show_default_detail()
        else:
            self.detail_title.config(text=title)
            self._clear_detail_content()
            self.detail_content_frame.configure(bg=self.card_bg)
            info_message = description or ""
            if action:
                try:
                    action()
                except Exception as exc:
                    messagebox.showerror("Error", f"Failed to open {title}: {exc}")
                else:
                    if info_message:
                        self._render_info_message(info_message)
            else:
                if info_message:
                    self._render_info_message(info_message)
    
    # Sales management behavior provided by SalesManagementMixin.
    
    def view_reports(self):
        messagebox.showinfo(
            "Reports",
            "Detailed reports are currently unavailable. Please contact the system administrator."
        )
        

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
