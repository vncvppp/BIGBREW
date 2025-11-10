import tkinter as tk
from tkinter import ttk, messagebox


class InventoryManagementMixin:
    def _refresh_inventory_view(self):
        if (
            getattr(self, "inventory_tree", None)
            and self.inventory_tree.winfo_exists()
        ):
            self.refresh_inventory_list()

    def manage_inventory(self):
        self.inventory_window = tk.Toplevel(self.window)
        self.inventory_window.title("Inventory Management")
        self.inventory_window.geometry("1200x700")
        self.inventory_window.configure(bg=self.bg_color)

        def close_inventory():
            try:
                if getattr(self, "inventory_tree", None) is not None:
                    self.inventory_tree = None
            except Exception:
                pass
            win = getattr(self, "inventory_window", None)
            if win is not None:
                self.inventory_window = None
                win.destroy()

        self.inventory_window.protocol("WM_DELETE_WINDOW", close_inventory)

        self.inventory_window.update_idletasks()
        width, height = 1200, 700
        screen_width = self.inventory_window.winfo_screenwidth()
        screen_height = self.inventory_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.inventory_window.geometry(f"{width}x{height}+{x}+{y}")

        header_frame = tk.Frame(self.inventory_window, bg=self.bg_color, height=60)
        header_frame.pack(fill="x", padx=20, pady=10)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="Inventory Management - Stock Tracking",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color,
        )
        title_label.pack(side="left")

        main_frame = tk.Frame(self.inventory_window, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        list_frame = tk.Frame(main_frame, bg=self.card_bg, relief="raised", bd=2)
        list_frame.pack(fill="both", expand=True)

        tk.Label(
            list_frame,
            text="Current Stock Levels",
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(pady=10)

        tree_frame = tk.Frame(list_frame, bg=self.card_bg)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar_y = tk.Scrollbar(tree_frame, orient="vertical")
        scrollbar_x = tk.Scrollbar(tree_frame, orient="horizontal")

        self.inventory_tree = ttk.Treeview(
            tree_frame,
            columns=(
                "ID",
                "Product",
                "Category",
                "PriceRegular",
                "PriceLarge",
                "Current Stock",
                "Status",
            ),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=20,
        )

        scrollbar_y.config(command=self.inventory_tree.yview)
        scrollbar_x.config(command=self.inventory_tree.xview)

        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Product", text="Product Name")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.heading("PriceRegular", text="Price Regular (₱)")
        self.inventory_tree.heading("PriceLarge", text="Price Large (₱)")
        self.inventory_tree.heading("Current Stock", text="Current Stock")
        self.inventory_tree.heading("Status", text="Status")

        self.inventory_tree.column("ID", width=50, anchor="center")
        self.inventory_tree.column("Product", width=230, anchor="w")
        self.inventory_tree.column("Category", width=130, anchor="w")
        self.inventory_tree.column("PriceRegular", width=140, anchor="center")
        self.inventory_tree.column("PriceLarge", width=140, anchor="center")
        self.inventory_tree.column("Current Stock", width=140, anchor="center")
        self.inventory_tree.column("Status", width=130, anchor="center")

        self.inventory_tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        button_frame = tk.Frame(list_frame, bg=self.card_bg)
        button_frame.pack(fill="x", pady=10)

        update_stock_btn = tk.Button(
            button_frame,
            text="📦 Update Stock",
            font=("Arial", 11),
            bg=self.button_color,
            fg=self.text_color,
            relief="flat",
            bd=0,
            command=self.update_stock_window,
            width=15,
            padx=10,
        )
        update_stock_btn.pack(side="left", padx=5)

        refresh_inv_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#6C757D",
            fg="white",
            relief="flat",
            bd=0,
            command=self.refresh_inventory_list,
            width=15,
            padx=10,
        )
        refresh_inv_btn.pack(side="left", padx=5)

        self.refresh_inventory_list()

    def refresh_inventory_list(self):
        tree = getattr(self, "inventory_tree", None)
        if tree is None:
            return
        try:
            if not tree.winfo_exists():
                return
        except tk.TclError:
            return
        try:
            for item in tree.get_children():
                tree.delete(item)
        except tk.TclError:
            return

        products = self._load_products()
        for product in products:
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
                tree.insert(
                    "",
                    tk.END,
                    values=(
                        product["product_id"],
                        product["name"],
                        product["category"],
                        f"₱{product['price_regular']:.2f}",
                        f"₱{product['price_large']:.2f}",
                        stock,
                        status,
                    ),
                    tags=(status_color,),
                )

                tree.tag_configure(status_color, foreground=status_color)
            except tk.TclError:
                return

    def update_stock_window(self):
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning(
                "No Selection", "Please select a product to update stock"
            )
            return

        item = self.inventory_tree.item(selection[0])
        product_id = int(item["values"][0])
        product_name = item["values"][1]
        current_stock = int(item["values"][5])

        update_window = tk.Toplevel(self.inventory_window)
        update_window.title("Update Stock")
        update_window.geometry("400x300")
        update_window.configure(bg=self.bg_color)

        update_window.update_idletasks()
        width, height = 400, 300
        screen_width = update_window.winfo_screenwidth()
        screen_height = update_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        update_window.geometry(f"{width}x{height}+{x}+{y}")

        form_frame = tk.Frame(update_window, bg=self.card_bg, relief="raised", bd=2)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            form_frame,
            text=f"Update Stock: {product_name}",
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(pady=20)

        tk.Label(
            form_frame,
            text=f"Current Stock: {current_stock}",
            font=("Arial", 12),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(pady=10)

        tk.Label(
            form_frame,
            text="New Stock Quantity:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(pady=(20, 5))

        stock_entry = tk.Entry(form_frame, font=("Arial", 12), width=20)
        stock_entry.insert(0, str(current_stock))
        stock_entry.pack(pady=10)
        stock_entry.select_range(0, tk.END)
        stock_entry.focus()

        button_frame = tk.Frame(form_frame, bg=self.card_bg)
        button_frame.pack(pady=20)

        def save_stock():
            try:
                new_stock = int(stock_entry.get())
                if new_stock < 0:
                    messagebox.showerror("Error", "Stock cannot be negative")
                    return

                self._create_or_update_inventory(product_id, new_stock)
                try:
                    self._products_cache = []
                except AttributeError:
                    pass

                messagebox.showinfo(
                    "Success", f"Stock updated to {new_stock} for {product_name}"
                )
                update_window.destroy()
                self.refresh_inventory_list()
                self.refresh_products_list()

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to update stock: {exc}")

        save_btn = tk.Button(
            button_frame,
            text="Update Stock",
            font=("Arial", 12, "bold"),
            bg="#28A745",
            fg="white",
            relief="flat",
            command=save_stock,
            width=15,
            padx=10,
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 12),
            bg="#6C757D",
            fg="white",
            relief="flat",
            command=update_window.destroy,
            width=15,
            padx=10,
        )
        cancel_btn.pack(side="left", padx=5)



