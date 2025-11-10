import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from app.db.connection import get_db_connection
from app.repositories.product_repository import ProductRepository


class ProductManagementMixin:
    def __init__(self, *args, **kwargs):
        self._products_cache = []
        self._categories_cache = None
        super().__init__(*args, **kwargs)

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------
    def get_categories(self):
        if self._categories_cache is not None:
            return self._categories_cache

        categories = []
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    category_id,
                    COALESCE(NULLIF(category_name, ''), NULLIF(name, '')) AS display_name,
                    category_name,
                    name AS fallback_name
                FROM categories
                ORDER BY display_name IS NULL, display_name
                """
            )
            rows = cursor.fetchall()
            for row in rows:
                display = (
                    row.get("display_name")
                    or row.get("category_name")
                    or row.get("fallback_name")
                    or "Uncategorized"
                )
                categories.append({"id": row.get("category_id"), "name": display})

            if not categories:
                cursor.execute(
                    """
                    SELECT DISTINCT
                        p.category_id,
                        COALESCE(NULLIF(p.category, ''), 'Uncategorized') AS display_name
                    FROM products p
                    WHERE p.category IS NOT NULL AND p.category <> ''
                    ORDER BY display_name
                    """
                )
                for row in cursor.fetchall():
                    categories.append(
                        {"id": row.get("category_id"), "name": row.get("display_name")}
                    )
        except Exception as exc:
            print(f"Failed to load categories: {exc}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        if not categories:
            categories = [
                {"id": None, "name": "Milk Tea"},
                {"id": None, "name": "Praf"},
                {"id": None, "name": "Fruit Tea"},
                {"id": None, "name": "Coffee"},
                {"id": None, "name": "Brosty"},
                {"id": None, "name": "Add-On"},
            ]

        self._categories_cache = categories
        return categories

    def _fetch_inventory_map(self):
        inventory = {}
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT product_id,
                       COALESCE(current_stock, quantity, 0) AS stock
                FROM inventory
                """
            )
            for row in cursor.fetchall():
                inventory[row["product_id"]] = int(row.get("stock") or 0)
        except Exception as exc:
            print(f"Failed to load inventory: {exc}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        return inventory

    def _load_products(self):
        try:
            products = ProductRepository.get_all_products()
        except Exception as exc:
            print(f"Failed to load products: {exc}")
            products = []

        inventory_map = self._fetch_inventory_map()
        formatted = []
        for product in products:
            price_regular = product.get("price_regular") or product.get("price") or 0.0
            price_large = product.get("price_large") or price_regular
            category_display = (
                product.get("category_name")
                or product.get("categories_category_name")
                or product.get("category")
                or "Uncategorized"
            )
            product_code = product.get("product_code") or ""
            product_name = (
                product.get("name")
                or product.get("product_name")
                or product.get("product_code")
                or ""
            )
            formatted.append(
                {
                    "product_id": product.get("product_id"),
                    "product_code": product_code,
                    "name": product_name,
                    "category_id": product.get("category_id"),
                    "category": category_display,
                    "price_regular": float(price_regular),
                    "price_large": float(price_large),
                    "description": product.get("description") or "",
                    "image_path": product.get("image_path"),
                    "stock": inventory_map.get(product.get("product_id"), 0),
                }
            )

        self._products_cache = formatted
        return formatted

    def _get_curated_products(self):
        if not self._products_cache:
            return self._load_products()
        return list(self._products_cache)

    def _get_curated_product_by_id(self, product_id):
        for product in self._get_curated_products():
            if product["product_id"] == product_id:
                return product
        # Fall back to database lookup if cache is stale
        try:
            product = ProductRepository.get_product_by_id(product_id)
            if not product:
                return None
            inventory_map = self._fetch_inventory_map()
            price_regular = product.get("price_regular") or product.get("price") or 0.0
            price_large = product.get("price_large") or price_regular
            return {
                "product_id": product.get("product_id"),
                "product_code": product.get("product_code") or "",
                "name": product.get("name")
                or product.get("product_name")
                or product.get("product_code")
                or "",
                "category_id": product.get("category_id"),
                "category": product.get("category_name")
                or product.get("categories_category_name")
                or product.get("category")
                or "Uncategorized",
                "price_regular": float(price_regular),
                "price_large": float(price_large),
                "description": product.get("description") or "",
                "image_path": product.get("image_path"),
                "stock": inventory_map.get(product.get("product_id"), 0),
            }
        except Exception as exc:
            print(f"Failed to fetch product by id: {exc}")
            return None

    def _create_or_update_inventory(self, product_id, quantity):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO inventory (product_id, current_stock, quantity, minimum_stock, reorder_point)
                VALUES (%s, %s, %s, 0, 0)
                ON DUPLICATE KEY UPDATE
                    current_stock = VALUES(current_stock),
                    quantity = VALUES(quantity)
                """,
                (product_id, quantity, quantity),
            )
            conn.commit()
        except Exception as exc:
            print(f"Failed to update inventory: {exc}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def manage_products(self, parent=None):
        embedded = parent is not None

        if embedded:
            container = parent
            for child in container.winfo_children():
                child.destroy()
            container.configure(bg=self.bg_color)
            self.product_window = self.window
        else:
            self.product_window = tk.Toplevel(self.window)
            self.product_window.title("Product Management")
            self.product_window.geometry("1270x790")
            self.product_window.configure(bg=self.bg_color)

            self.product_window.update_idletasks()
            width, height = 1270, 790
            screen_width = self.product_window.winfo_screenwidth()
            screen_height = self.product_window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.product_window.geometry(f"{width}x{height}+{x}+{y}")

            container = self.product_window

        pad = 0 if embedded else 0
        frame_bg = self.card_bg if embedded else self.bg_color

        main_frame = tk.Frame(container, bg=frame_bg, bd=0, highlightthickness=0)
        main_frame.pack(fill="both", expand=True, padx=pad, pady=(pad, pad))

        top_bar = tk.Frame(main_frame, bg=frame_bg, bd=0, highlightthickness=0)
        top_bar.pack(fill="x", pady=(0, 8))
        tk.Button(
            top_bar,
            text="➕ Add New Product",
            font=("Arial", 12, "bold"),
            bg="#28A745",
            fg="white",
            relief="flat",
            bd=0,
            command=self.add_product_window,
            padx=20,
            pady=5,
        ).pack(side="right")

        list_frame = tk.Frame(main_frame, bg=self.card_bg, relief="flat", bd=0)
        list_frame.pack(fill="both", expand=True, padx=0, pady=0)

        inner_wrapper = tk.Frame(list_frame, bg=self.card_bg, bd=0, highlightthickness=0)
        inner_wrapper.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        tree_frame = tk.Frame(inner_wrapper, bg=self.card_bg, bd=0, highlightthickness=0)
        tree_frame.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        scrollbar_y = tk.Scrollbar(tree_frame, orient="vertical")
        scrollbar_x = tk.Scrollbar(tree_frame, orient="horizontal")

        self.products_tree = ttk.Treeview(
            tree_frame,
            columns=(
                "ID",
                "Code",
                "Name",
                "Category",
                "PriceRegular",
                "PriceLarge",
                "Description",
            ),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=20,
        )

        scrollbar_y.config(command=self.products_tree.yview)
        scrollbar_x.config(command=self.products_tree.xview)

        self.products_tree.heading("ID", text="ID")
        self.products_tree.heading("Code", text="Product Code")
        self.products_tree.heading("Name", text="Product Name")
        self.products_tree.heading("Category", text="Category")
        self.products_tree.heading("PriceRegular", text="Price Reg (₱)")
        self.products_tree.heading("PriceLarge", text="Price Lrg (₱)")
        self.products_tree.heading("Description", text="Description")

        self.products_tree.column("ID", width=55, anchor="center", stretch=False)
        self.products_tree.column("Code", width=90, anchor="w", stretch=False)
        self.products_tree.column("Name", width=190, anchor="w", stretch=False)
        self.products_tree.column("Category", width=115, anchor="w", stretch=False)
        self.products_tree.column("PriceRegular", width=95, anchor="center", stretch=False)
        self.products_tree.column("PriceLarge", width=95, anchor="center", stretch=False)
        self.products_tree.column("Description", width=330, anchor="w", stretch=True)

        self.products_tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        button_frame = tk.Frame(inner_wrapper, bg=self.card_bg, bd=0, highlightthickness=0)
        button_frame.pack(fill="x", pady=(4, 6))

        edit_btn = tk.Button(
            button_frame,
            text="✏️ Edit Product",
            font=("Arial", 11),
            bg=self.button_color,
            fg=self.text_color,
            relief="flat",
            bd=0,
            command=self.edit_product_window,
            width=15,
            padx=10,
        )
        edit_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(
            button_frame,
            text="❌ Delete Product",
            font=("Arial", 11),
            bg="#DC3545",
            fg="white",
            relief="flat",
            bd=0,
            command=self.delete_product,
            width=15,
            padx=10,
        )
        delete_btn.pack(side="left", padx=5)

        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#6C757D",
            fg="white",
            relief="flat",
            bd=0,
            command=self.refresh_products_list,
            width=15,
            padx=10,
        )
        refresh_btn.pack(side="left", padx=5)

        self.refresh_products_list()

    def refresh_products_list(self):
        tree = getattr(self, "products_tree", None)
        if tree is None:
            return
        try:
            if not tree.winfo_exists():
                return
        except tk.TclError:
            return

        for item in tree.get_children():
            tree.delete(item)

        products = self._load_products()
        for product in products:
            tree.insert(
                "",
                tk.END,
                values=(
                    product["product_id"],
                    product.get("product_code", ""),
                    product["name"],
                    product["category"],
                    f"₱{product['price_regular']:.2f}",
                    f"₱{product['price_large']:.2f}",
                    product["description"],
                ),
            )

    def add_product_window(self):
        add_window = tk.Toplevel(self.product_window)
        add_window.title("Add New Product")
        add_window.geometry("600x700")
        add_window.configure(bg=self.bg_color)

        add_window.update_idletasks()
        width, height = 600, 700
        screen_width = add_window.winfo_screenwidth()
        screen_height = add_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        add_window.geometry(f"{width}x{height}+{x}+{y}")

        form_frame = tk.Frame(add_window, bg=self.card_bg, relief="raised", bd=2)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            form_frame,
            text="Add New Product",
            font=("Arial", 16, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(pady=20)

        tk.Label(
            form_frame,
            text="Category:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            form_frame,
            textvariable=category_var,
            font=("Arial", 11),
            state="readonly",
            width=40,
        )
        category_combo.pack(padx=20, pady=(0, 10), fill="x")

        categories = self.get_categories()
        category_dict = {cat["name"]: cat["id"] for cat in categories}
        category_combo["values"] = list(category_dict.keys())
        if categories:
            category_combo.current(0)

        tk.Label(
            form_frame,
            text="Product Code:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        code_entry = tk.Entry(form_frame, font=("Arial", 11), width=40)
        code_entry.pack(padx=20, pady=(0, 10))

        tk.Label(
            form_frame,
            text="Product Name:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        name_entry = tk.Entry(form_frame, font=("Arial", 11), width=40)
        name_entry.pack(padx=20, pady=(0, 10))

        tk.Label(
            form_frame,
            text="Description:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        desc_text = tk.Text(form_frame, font=("Arial", 11), width=40, height=4)
        desc_text.pack(padx=20, pady=(0, 10))

        price_frame = tk.Frame(form_frame, bg=self.card_bg)
        price_frame.pack(padx=20, pady=(10, 10), fill="x")
        price_frame.columnconfigure(0, weight=1)
        price_frame.columnconfigure(1, weight=1)

        tk.Label(
            price_frame,
            text="Price Regular (₱):",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            price_frame,
            text="Price Large (₱):",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).grid(row=0, column=1, sticky="w", padx=(20, 0))

        price_regular_entry = tk.Entry(price_frame, font=("Arial", 11))
        price_regular_entry.grid(row=1, column=0, sticky="we", pady=(3, 0))

        price_large_entry = tk.Entry(price_frame, font=("Arial", 11))
        price_large_entry.grid(row=1, column=1, sticky="we", padx=(20, 0), pady=(3, 0))

        tk.Label(
            form_frame,
            text="Initial Stock Quantity:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        stock_entry = tk.Entry(form_frame, font=("Arial", 11), width=40)
        stock_entry.insert(0, "100")
        stock_entry.pack(padx=20, pady=(0, 10))

        image_path_var = tk.StringVar()

        def browse_image():
            filename = filedialog.askopenfilename(
                title="Select Product Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")],
            )
            if filename:
                image_path_var.set(filename)

        tk.Label(
            form_frame,
            text="Image Path (Optional):",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        image_frame = tk.Frame(form_frame, bg=self.card_bg)
        image_frame.pack(padx=20, pady=(0, 10), fill="x")

        image_entry = tk.Entry(
            image_frame, textvariable=image_path_var, font=("Arial", 11), width=30
        )
        image_entry.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(
            image_frame,
            text="Browse",
            font=("Arial", 10),
            bg="#6C757D",
            fg="white",
            relief="flat",
            command=browse_image,
            width=10,
        )
        browse_btn.pack(side="right", padx=(5, 0))

        button_frame = tk.Frame(form_frame, bg=self.card_bg)
        button_frame.pack(pady=20)

        def save_product():
            try:
                category_name = category_var.get()
                if not category_name:
                    messagebox.showerror("Error", "Please select a category")
                    return

                name = name_entry.get().strip()
                product_code = code_entry.get().strip() or None
                description = desc_text.get("1.0", tk.END).strip()
                price_regular_value = price_regular_entry.get().strip()
                price_large_value = price_large_entry.get().strip()
                price_regular = float(price_regular_value)
                price_large = float(price_large_value) if price_large_value else price_regular
                stock = int(stock_entry.get())
                image_path = image_path_var.get().strip() or None
                image_blob = None
                if image_path:
                    if not os.path.isfile(image_path):
                        messagebox.showerror("Error", "Selected image file does not exist")
                        return
                    try:
                        with open(image_path, "rb") as img_file:
                            image_blob = img_file.read()
                    except OSError as exc:
                        messagebox.showerror("Error", f"Failed to read image: {exc}")
                        return

                if not name:
                    messagebox.showerror("Error", "Product name is required")
                    return

                if price_regular < 0:
                    messagebox.showerror("Error", "Regular price cannot be negative")
                    return

                if price_large < 0:
                    messagebox.showerror("Error", "Large price cannot be negative")
                    return

                if stock < 0:
                    messagebox.showerror("Error", "Stock cannot be negative")
                    return

                category_id = category_dict.get(category_name)
                new_id = ProductRepository.add_product(
                    category_id=category_id,
                    name=name,
                    product_code=product_code,
                    description=description or "",
                    price_regular=price_regular,
                    price_large=price_large,
                    image_path=image_path,
                    image_blob=image_blob,
                )

                if not new_id:
                    messagebox.showerror(
                        "Error", "Failed to add product to the database."
                    )
                    return

                self._create_or_update_inventory(new_id, stock)

                messagebox.showinfo(
                    "Success", f"Product '{name}' added successfully!"
                )
                self._products_cache = []
                add_window.destroy()
                self.refresh_products_list()
                self._refresh_inventory_view()

            except ValueError:
                messagebox.showerror("Error", "Invalid price or stock value")
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to add product: {exc}")

        save_btn = tk.Button(
            button_frame,
            text="Save Product",
            font=("Arial", 12, "bold"),
            bg="#28A745",
            fg="white",
            relief="flat",
            command=save_product,
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
            command=add_window.destroy,
            width=15,
            padx=10,
        )
        cancel_btn.pack(side="left", padx=5)

    def edit_product_window(self):
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning(
                "No Selection", "Please select a product to edit"
            )
            return

        item = self.products_tree.item(selection[0])
        product_id = item["values"][0]

        product = self._get_curated_product_by_id(product_id)
        if not product:
            messagebox.showerror("Error", "Product not found")
            return

        edit_window = tk.Toplevel(self.product_window)
        edit_window.title("Edit Product")
        edit_window.geometry("600x700")
        edit_window.configure(bg=self.bg_color)

        edit_window.update_idletasks()
        width, height = 600, 700
        screen_width = edit_window.winfo_screenwidth()
        screen_height = edit_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        edit_window.geometry(f"{width}x{height}+{x}+{y}")

        form_frame = tk.Frame(edit_window, bg=self.card_bg, relief="raised", bd=2)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            form_frame,
            text=f"Edit Product: {product['name']}",
            font=("Arial", 16, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(pady=20)

        tk.Label(
            form_frame,
            text="Category:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            form_frame,
            textvariable=category_var,
            font=("Arial", 11),
            state="readonly",
            width=40,
        )
        category_combo.pack(padx=20, pady=(0, 10), fill="x")

        categories = self.get_categories()
        category_dict = {cat["name"]: cat["id"] for cat in categories}
        category_combo["values"] = list(category_dict.keys())

        current_cat = product.get("category", "") or product.get("category_name", "")
        matched = False
        if current_cat:
            for display_name, cat_id in list(category_dict.items()):
                if display_name.lower() == current_cat.lower():
                    category_combo.set(display_name)
                    matched = True
                    break
            if not matched:
                category_dict[current_cat] = product.get("category_id")
                values = list(category_dict.keys())
                category_combo["values"] = values
                category_combo.set(current_cat)
        if not matched and not current_cat and categories:
            category_combo.current(0)

        tk.Label(
            form_frame,
            text="Product Code:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        code_entry = tk.Entry(form_frame, font=("Arial", 11), width=40)
        code_entry.insert(0, product.get("product_code", "") or "")
        code_entry.pack(padx=20, pady=(0, 10))

        tk.Label(
            form_frame,
            text="Product Name:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        name_entry = tk.Entry(form_frame, font=("Arial", 11), width=40)
        name_entry.insert(0, product["name"])
        name_entry.pack(padx=20, pady=(0, 10))

        tk.Label(
            form_frame,
            text="Description:",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        desc_text = tk.Text(form_frame, font=("Arial", 11), width=40, height=4)
        desc_text.insert("1.0", product.get("description", ""))
        desc_text.pack(padx=20, pady=(0, 10))

        price_frame = tk.Frame(form_frame, bg=self.card_bg)
        price_frame.pack(padx=20, pady=(10, 10), fill="x")
        price_frame.columnconfigure(0, weight=1)
        price_frame.columnconfigure(1, weight=1)

        tk.Label(
            price_frame,
            text="Price Regular (₱):",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            price_frame,
            text="Price Large (₱):",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).grid(row=0, column=1, sticky="w", padx=(20, 0))

        price_regular_entry = tk.Entry(price_frame, font=("Arial", 11))
        price_regular_entry.insert(0, str(product.get("price_regular", 0)))
        price_regular_entry.grid(row=1, column=0, sticky="we", pady=(3, 0))

        price_large_entry = tk.Entry(price_frame, font=("Arial", 11))
        price_large_entry.insert(0, str(product.get("price_large", product.get("price_regular", 0))))
        price_large_entry.grid(row=1, column=1, sticky="we", padx=(20, 0), pady=(3, 0))

        image_path_var = tk.StringVar(value=product.get("image_path", ""))

        def browse_image():
            filename = filedialog.askopenfilename(
                title="Select Product Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")],
            )
            if filename:
                image_path_var.set(filename)

        tk.Label(
            form_frame,
            text="Image Path (Optional):",
            font=("Arial", 11, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w", padx=20, pady=(10, 5))

        image_frame = tk.Frame(form_frame, bg=self.card_bg)
        image_frame.pack(padx=20, pady=(0, 10), fill="x")

        image_entry = tk.Entry(
            image_frame, textvariable=image_path_var, font=("Arial", 11), width=30
        )
        image_entry.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(
            image_frame,
            text="Browse",
            font=("Arial", 10),
            bg="#6C757D",
            fg="white",
            relief="flat",
            command=browse_image,
            width=10,
        )
        browse_btn.pack(side="right", padx=(5, 0))

        button_frame = tk.Frame(form_frame, bg=self.card_bg)
        button_frame.pack(pady=20)

        def update_product():
            try:
                category_name = category_var.get()
                if not category_name:
                    messagebox.showerror("Error", "Please select a category")
                    return

                name = name_entry.get().strip()
                product_code = code_entry.get().strip() or None
                description = desc_text.get("1.0", tk.END).strip()
                price_regular_value = price_regular_entry.get().strip()
                price_large_value = price_large_entry.get().strip()
                price_regular = float(price_regular_value)
                price_large = float(price_large_value) if price_large_value else price_regular
                image_path = image_path_var.get().strip() or None
                image_blob = None
                if image_path:
                    if not os.path.isfile(image_path):
                        messagebox.showerror("Error", "Selected image file does not exist")
                        return
                    try:
                        with open(image_path, "rb") as img_file:
                            image_blob = img_file.read()
                    except OSError as exc:
                        messagebox.showerror("Error", f"Failed to read image: {exc}")
                        return

                if not name:
                    messagebox.showerror("Error", "Product name is required")
                    return

                if price_regular < 0:
                    messagebox.showerror("Error", "Regular price cannot be negative")
                    return

                if price_large < 0:
                    messagebox.showerror("Error", "Large price cannot be negative")
                    return

                category_id = category_dict.get(category_name)
                success = ProductRepository.update_product(
                    product_id=product_id,
                    category_id=category_id,
                    product_name=name,
                    product_code=product_code,
                    description=description or "",
                    price=price_regular,
                    price_regular=price_regular,
                    price_large=price_large,
                    image_path=image_path,
                    image_blob=image_blob,
                )

                if not success:
                    messagebox.showerror(
                        "Error", f"Failed to update product '{name}'."
                    )
                    return

                messagebox.showinfo(
                    "Success", f"Product '{name}' updated successfully!"
                )
                self._products_cache = []
                edit_window.destroy()
                self.refresh_products_list()
                self._refresh_inventory_view()

            except ValueError:
                messagebox.showerror("Error", "Invalid price value")
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to update product: {exc}")

        save_btn = tk.Button(
            button_frame,
            text="Update Product",
            font=("Arial", 12, "bold"),
            bg=self.button_color,
            fg=self.text_color,
            relief="flat",
            command=update_product,
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
            command=edit_window.destroy,
            width=15,
            padx=10,
        )
        cancel_btn.pack(side="left", padx=5)

    def delete_product(self):
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning(
                "No Selection", "Please select a product to delete"
            )
            return

        item = self.products_tree.item(selection[0])
        product_id = item["values"][0]
        product_name = item["values"][1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{product_name}'?\n\n"
            "This action cannot be undone and will also remove inventory records.",
        )

        if confirm:
            try:
                success = ProductRepository.delete_product(product_id)
                if success:
                    messagebox.showinfo(
                        "Success", f"Product '{product_name}' deleted successfully!"
                    )
                    self._products_cache = []
                    self.refresh_products_list()
                    self._refresh_inventory_view()
                else:
                    messagebox.showerror("Error", "Failed to delete product")
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to delete product: {exc}")

