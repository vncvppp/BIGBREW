import os
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
import webbrowser
from app.db.connection import get_db_connection


class SalesManagementMixin:
    def _get_table_columns(self, table_name):
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

    def _get_product_id_column(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DESCRIBE products")
            columns = cursor.fetchall()
            cursor.close()
            conn.close()

            column_names = [col[0] for col in columns]
            if "id" in column_names:
                return "id"
            if "product_id" in column_names:
                return "product_id"
            return "id"
        except Exception:
            return "id"

    def _get_schema(self):
        prod_cols = self._get_table_columns("products")
        cat_cols = self._get_table_columns("categories")
        inv_cols = self._get_table_columns("inventory")

        prod_id = (
            "id"
            if "id" in prod_cols
            else ("product_id" if "product_id" in prod_cols else self._get_product_id_column())
        )
        prod_name = (
            "name"
            if "name" in prod_cols
            else ("product_name" if "product_name" in prod_cols else "name")
        )
        prod_price = (
            "price"
            if "price" in prod_cols
            else ("unit_price" if "unit_price" in prod_cols else "price")
        )
        prod_desc = "description" if "description" in prod_cols else None
        prod_image = "image_path" if "image_path" in prod_cols else None
        prod_cat_fk = (
            "category_id"
            if "category_id" in prod_cols
            else next((c for c in prod_cols if "category" in c and "id" in c), "category_id")
        )

        cat_id = "id" if "id" in cat_cols else ("category_id" if "category_id" in cat_cols else "id")
        cat_name = "name" if "name" in cat_cols else ("category_name" if "category_name" in cat_cols else "name")

        inv_qty = (
            "quantity"
            if "quantity" in inv_cols
            else ("current_stock" if "current_stock" in inv_cols else "quantity")
        )
        inv_prod_fk = "product_id" if "product_id" in inv_cols else "product_id"

        return {
            "prod_id": prod_id,
            "prod_name": prod_name,
            "prod_price": prod_price,
            "prod_desc": prod_desc,
            "prod_image": prod_image,
            "prod_cat_fk": prod_cat_fk,
            "cat_id": cat_id,
            "cat_name": cat_name,
            "inv_qty": inv_qty,
            "inv_prod_fk": inv_prod_fk,
        }

    def _get_sales_schema(self):
        sales_cols = self._get_table_columns("sales")
        sale_items_cols = self._get_table_columns("sale_items")
        customer_cols = self._get_table_columns("customers")
        product_cols = self._get_table_columns("products")

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
            exact=("id", "sale_id"),
            contains=(("sale", "id"),),
        )
        sale_date = find_col(
            sales_cols,
            exact=("sale_date", "date", "created_at", "transaction_date"),
            contains=(("sale", "date"), ("trans", "date"), ("order", "date"), ("date",),),
        )
        total_amount = find_col(
            sales_cols,
            exact=("total_amount", "grand_total", "amount", "total"),
            contains=(("total", "amount"), ("grand", "total"), ("amount",),),
        )
        payment_method = find_col(
            sales_cols,
            exact=("payment_method", "payment_type", "paymentmode"),
            contains=(("payment", "method"), ("payment", "type"), ("pay",),),
        )
        proof_path = find_col(
            sales_cols,
            exact=("proof_of_payment_path", "receipt_path", "attachment_path"),
            contains=(("proof", "path"), ("receipt", "path"), ("payment", "path")),
        )
        proof_blob = find_col(
            sales_cols,
            exact=("proof_of_payment_blob", "receipt_blob", "payment_blob"),
            contains=(("proof", "blob"), ("payment", "blob")),
        )
        status_col = find_col(
            sales_cols,
            exact=("status",),
            contains=(("status",),),
        )
        customer_fk = find_col(
            sales_cols,
            exact=("customer_id", "client_id", "customer"),
            contains=(("customer", "id"), ("client", "id"), ("cust",),),
        )

        customer_id = find_col(
            customer_cols,
            exact=("id", "customer_id"),
            contains=(("customer", "id"), ("client", "id"),),
        )
        customer_first = find_col(
            customer_cols,
            exact=("first_name", "firstname", "given_name"),
            contains=(("first",), ("given",),),
        )
        customer_last = find_col(
            customer_cols,
            exact=("last_name", "lastname", "surname", "family_name"),
            contains=(("last",), ("sur", "name"), ("family",),),
        )

        sale_item_sale_fk = find_col(
            sale_items_cols,
            exact=("sale_id", "sales_id", "order_id"),
            contains=(("sale", "id"), ("order", "id"),),
        )
        sale_item_product_fk = find_col(
            sale_items_cols,
            exact=("product_id", "item_id"),
            contains=(("product", "id"), ("item", "id"),),
        )
        sale_item_qty = find_col(
            sale_items_cols,
            exact=("quantity", "qty", "amount"),
            contains=(("qty",), ("quantity",),),
        )
        sale_item_price = find_col(
            sale_items_cols,
            exact=("price", "unit_price", "amount"),
            contains=(("price",), ("amount",),),
        )

        product_name = find_col(
            product_cols,
            exact=("name", "product_name"),
            contains=(("product", "name"),),
        )
        product_id = find_col(
            product_cols,
            exact=("id", "product_id"),
            contains=(("product", "id"),),
        )

        return {
            "sale_id": sale_id or "id",
            "sale_date": sale_date or "sale_date",
            "total_amount": total_amount or "total_amount",
            "payment_method": payment_method or "payment_method",
            "proof_of_payment_path": proof_path,
            "proof_of_payment_blob": proof_blob,
            "status": status_col or "status",
            "customer_fk": customer_fk or "customer_id",
            "customer_pk": customer_id or "id",
            "customer_first": customer_first or "first_name",
            "customer_last": customer_last or "last_name",
            "sale_item_sale_fk": sale_item_sale_fk or "sale_id",
            "sale_item_product_fk": sale_item_product_fk or "product_id",
            "sale_item_qty": sale_item_qty or "quantity",
            "sale_item_price": sale_item_price or "price",
            "product_name": product_name or "name",
            "product_id": product_id or "id",
        }

    def manage_sales(self, parent=None):
        embedded = parent is not None

        if embedded:
            container = parent
            for child in container.winfo_children():
                child.destroy()
            container.configure(bg=self.bg_color)
            self.sales_window = self.window
        else:
            self.sales_window = tk.Toplevel(self.window)
            self.sales_window.title("Sales Management")
            self.sales_window.geometry("1400x800")
            self.sales_window.configure(bg=self.bg_color)

            self.sales_window.update_idletasks()
            width, height = 1400, 800
            screen_width = self.sales_window.winfo_screenwidth()
            screen_height = self.sales_window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.sales_window.geometry(f"{width}x{height}+{x}+{y}")

            container = self.sales_window

        pad = 0 if embedded else 0
        frame_bg = self.card_bg if embedded else self.bg_color

        top_frame = tk.Frame(container, bg=frame_bg, bd=0, highlightthickness=0)
        top_frame.pack(fill="x", padx=pad, pady=(pad, 8))

        if not embedded:
            title_label = tk.Label(
                top_frame,
                text="Sales Management - View and Manage Transactions",
                font=("Arial", 18, "bold"),
                bg=frame_bg,
                fg=self.accent_color,
            )
            title_label.pack(side="left")

        filter_frame = tk.Frame(top_frame, bg=frame_bg)
        filter_frame.pack(side="right")

        tk.Label(
            filter_frame,
            text="Date Range:",
            font=("Arial", 10),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(side="left", padx=5)

        date_filter_var = tk.StringVar(value="All")
        date_filter = ttk.Combobox(
            filter_frame,
            textvariable=date_filter_var,
            values=["All", "Today", "Last 7 Days", "Last 30 Days", "This Month", "Last Month"],
            state="readonly",
            width=15,
        )
        date_filter.pack(side="left", padx=5)
        date_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_sales_list())

        main_frame = tk.Frame(container, bg=frame_bg, bd=0, highlightthickness=0)
        main_frame.pack(fill="both", expand=True, padx=pad, pady=(0 if embedded else pad, pad))

        list_frame = tk.Frame(main_frame, bg=self.card_bg, relief="flat", bd=0)
        list_frame.pack(fill="both", expand=True, padx=0, pady=0)

        inner_wrapper = tk.Frame(list_frame, bg=self.card_bg, bd=0, highlightthickness=0)
        inner_wrapper.pack(fill="both", expand=True, padx=0, pady=0)

        tree_frame = tk.Frame(inner_wrapper, bg=self.card_bg, bd=0, highlightthickness=0)
        tree_frame.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        scrollbar_y = tk.Scrollbar(tree_frame, orient="vertical")
        scrollbar_x = tk.Scrollbar(tree_frame, orient="horizontal")

        self.sales_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Date", "Customer", "Total Amount", "Payment Method", "Status", "Items"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=20,
        )

        scrollbar_y.config(command=self.sales_tree.yview)
        scrollbar_x.config(command=self.sales_tree.xview)

        self.sales_tree.heading("ID", text="Sale ID")
        self.sales_tree.heading("Date", text="Date & Time")
        self.sales_tree.heading("Customer", text="Customer")
        self.sales_tree.heading("Total Amount", text="Total (₱)")
        self.sales_tree.heading("Payment Method", text="Payment")
        self.sales_tree.heading("Status", text="Status")
        self.sales_tree.heading("Items", text="Items")

        self.sales_tree.column("ID", width=60, anchor="center", stretch=False)
        self.sales_tree.column("Date", width=155, anchor="w", stretch=False)
        self.sales_tree.column("Customer", width=140, anchor="w", stretch=False)
        self.sales_tree.column("Total Amount", width=95, anchor="center", stretch=False)
        self.sales_tree.column("Payment Method", width=95, anchor="center", stretch=False)
        self.sales_tree.column("Status", width=95, anchor="center", stretch=False)
        self.sales_tree.column("Items", width=3200, anchor="w", stretch=True)

        self.sales_tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        button_frame = tk.Frame(inner_wrapper, bg=self.card_bg, bd=0, highlightthickness=0)
        button_frame.pack(fill="x", pady=(6, 8))

        view_details_btn = tk.Button(
            button_frame,
            text="📋 View Details",
            font=("Arial", 11),
            bg=self.button_color,
            fg=self.text_color,
            relief="flat",
            bd=0,
            command=self.view_sale_details,
            width=15,
            padx=10,
        )
        view_details_btn.pack(side="left", padx=5)

        delete_sale_btn = tk.Button(
            button_frame,
            text="❌ Delete Sale",
            font=("Arial", 11),
            bg="#DC3545",
            fg="white",
            relief="flat",
            bd=0,
            command=self.delete_sale,
            width=15,
            padx=10,
        )
        delete_sale_btn.pack(side="left", padx=5)

        refresh_sales_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#6C757D",
            fg="white",
            relief="flat",
            bd=0,
            command=self.refresh_sales_list,
            width=15,
            padx=10,
        )
        refresh_sales_btn.pack(side="left", padx=5)

        update_status_btn = tk.Button(
            button_frame,
            text="✅ Update Status",
            font=("Arial", 11),
            bg="#28A745",
            fg="white",
            relief="flat",
            bd=0,
            command=self.update_sale_status,
            width=15,
            padx=10,
        )
        update_status_btn.pack(side="left", padx=5)

        self.date_filter_var = date_filter_var
        self.refresh_sales_list()

    def refresh_sales_list(self):
        tree = getattr(self, "sales_tree", None)
        if tree is None:
            return
        try:
            if not tree.winfo_exists():
                return
        except tk.TclError:
            return

        for item in tree.get_children():
            tree.delete(item)

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            schema = self._get_sales_schema()
            sale_id_col = schema["sale_id"]
            sale_date_col = schema["sale_date"]
            total_amount_col = schema["total_amount"]
            payment_method_col = schema["payment_method"]
            proof_path_col = schema.get("proof_of_payment_path")
            proof_blob_col = schema.get("proof_of_payment_blob")
            status_col = schema.get("status")
            customer_fk_col = schema["customer_fk"]
            customer_pk_col = schema["customer_pk"]
            customer_first_col = schema["customer_first"]
            customer_last_col = schema["customer_last"]
            sale_item_sale_fk = schema["sale_item_sale_fk"]
            sale_item_qty = schema["sale_item_qty"]
            sale_item_product_fk = schema["sale_item_product_fk"]
            product_name_col = schema["product_name"]
            product_id_col = schema["product_id"]

            date_filter = getattr(self, "date_filter_var", tk.StringVar(value="All")).get()
            date_condition = ""

            if date_filter == "Today":
                date_condition = f"DATE(s.{sale_date_col}) = CURDATE()"
            elif date_filter == "Last 7 Days":
                date_condition = f"s.{sale_date_col} >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
            elif date_filter == "Last 30 Days":
                date_condition = f"s.{sale_date_col} >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
            elif date_filter == "This Month":
                date_condition = (
                    f"MONTH(s.{sale_date_col}) = MONTH(NOW()) AND YEAR(s.{sale_date_col}) = YEAR(NOW())"
                )
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
                       {('s.' + status_col) if status_col else "'pending'"} AS sale_status,
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

            cursor.execute(query, [])
            sales = cursor.fetchall()

            for sale in sales:
                customer_name = f"{sale['customer_first']} {sale['customer_last']}".strip() or "Walk-in"
                sale_date = sale["sale_date"]
                if isinstance(sale_date, str):
                    sale_date_str = sale_date
                elif sale_date is not None:
                    sale_date_str = sale_date.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    sale_date_str = "N/A"

                payment_method = sale.get("payment_method") or "Unknown"
                payment_display = payment_method.title() if isinstance(payment_method, str) else str(payment_method)

                total_amount = sale.get("total_amount") or 0
                status_value = sale.get("sale_status") or "pending"
                status_display = status_value.title() if isinstance(status_value, str) else str(status_value)

                tree.insert(
                    "",
                    tk.END,
                    values=(
                        sale["sale_id"],
                        sale_date_str,
                        customer_name,
                        f"₱{total_amount:.2f}",
                        payment_display,
                        status_display,
                        sale.get("items") or "N/A",
                    ),
                )

            cursor.close()
            conn.close()
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load sales: {exc}")

    def view_sale_details(self):
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sale to view details")
            return

        item = self.sales_tree.item(selection[0])
        sale_id = item["values"][0]

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            schema = self._get_sales_schema()
            sale_id_col = schema["sale_id"]
            sale_date_col = schema["sale_date"]
            total_amount_col = schema["total_amount"]
            payment_method_col = schema["payment_method"]
            proof_path_col = schema.get("proof_of_payment_path")
            proof_blob_col = schema.get("proof_of_payment_blob")
            status_col = schema.get("status")
            customer_fk_col = schema["customer_fk"]
            customer_pk_col = schema["customer_pk"]
            customer_first_col = schema["customer_first"]
            customer_last_col = schema["customer_last"]
            sale_item_sale_fk = schema["sale_item_sale_fk"]
            sale_item_product_fk = schema["sale_item_product_fk"]
            sale_item_qty = schema["sale_item_qty"]
            sale_item_price = schema["sale_item_price"]
            product_schema = self._get_schema()
            product_name_col = product_schema["prod_name"]
            product_id_col = product_schema["prod_id"]

            sale_query = f"""
                SELECT s.{sale_id_col} AS sale_id,
                       s.{sale_date_col} AS sale_date,
                       s.{total_amount_col} AS total_amount,
                       s.{payment_method_col} AS payment_method,
                       {('s.' + proof_path_col) if proof_path_col else 'NULL'} AS proof_path,
                       {('s.' + proof_blob_col) if proof_blob_col else 'NULL'} AS proof_blob,
                       {('s.' + status_col) if status_col else "'pending'"} AS sale_status,
                       COALESCE(c.{customer_first_col}, '') AS customer_first,
                       COALESCE(c.{customer_last_col}, '') AS customer_last
                FROM sales s
                LEFT JOIN customers c ON s.{customer_fk_col} = c.{customer_pk_col}
                WHERE s.{sale_id_col} = %s
            """
            cursor.execute(sale_query, (sale_id,))
            sale = cursor.fetchone()

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

            details_window = tk.Toplevel(self.sales_window)
            details_window.title(f"Sale Details - #{sale_id}")
            details_window.geometry("600x500")
            details_window.configure(bg=self.bg_color)

            details_window.update_idletasks()
            width, height = 600, 500
            screen_width = details_window.winfo_screenwidth()
            screen_height = details_window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            details_window.geometry(f"{width}x{height}+{x}+{y}")

            form_frame = tk.Frame(details_window, bg=self.card_bg, relief="raised", bd=2)
            form_frame.pack(fill="both", expand=True, padx=20, pady=20)

            tk.Label(
                form_frame,
                text=f"Sale Details - #{sale_id}",
                font=("Arial", 16, "bold"),
                bg=self.card_bg,
                fg="#4A3728",
            ).pack(pady=20)

            payment_method = sale.get("payment_method") or "Unknown"
            payment_display = payment_method.title() if isinstance(payment_method, str) else str(payment_method)

            total_amount = sale.get("total_amount") or 0
            sale_date_value = sale.get("sale_date")
            if hasattr(sale_date_value, "strftime"):
                sale_date_display = sale_date_value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                sale_date_display = str(sale_date_value or "N/A")

            status_value = sale.get("sale_status") or "pending"
            status_display = status_value.title() if isinstance(status_value, str) else str(status_value)

            info_text = f"""
Sale ID: {sale['sale_id']}
Date: {sale_date_display}
Customer: {f"{sale['customer_first']} {sale['customer_last']}".strip() or 'Walk-in'}
Payment Method: {payment_display}
Status: {status_display}
Total Amount: ₱{total_amount:.2f}

Items:
"""
            tk.Label(
                form_frame,
                text=info_text,
                font=("Arial", 11),
                bg=self.card_bg,
                fg="#4A3728",
                justify="left",
                anchor="w",
            ).pack(padx=20, pady=10, anchor="w")

            items_text = ""
            for line_item in items:
                quantity = line_item.get("quantity") or 0
                price = line_item.get("price") or 0
                items_text += (
                    f"  • {quantity}x {line_item.get('product_name', 'Unknown')} @ ₱{price:.2f} = ₱{quantity * price:.2f}\n"
                )

            items_label = tk.Label(
                form_frame,
                text=items_text,
                font=("Arial", 10),
                bg=self.card_bg,
                fg="#666666",
                justify="left",
                anchor="w",
            )
            items_label.pack(padx=20, pady=10, anchor="w")

            proof_path = sale.get("proof_path")
            proof_blob = sale.get("proof_blob")
            if proof_path or proof_blob:
                proof_btn = tk.Button(
                    form_frame,
                    text="View Proof of Payment",
                    font=("Arial", 12),
                    bg=self.button_color,
                    fg=self.text_color,
                    relief="flat",
                    command=lambda: self._open_proof_of_payment(proof_path, proof_blob),
                    width=20,
                    padx=10,
                )
                proof_btn.pack(pady=(10, 5))

            close_btn = tk.Button(
                form_frame,
                text="Close",
                font=("Arial", 12),
                bg="#6C757D",
                fg="white",
                relief="flat",
                command=details_window.destroy,
                width=15,
                padx=10,
            )
            close_btn.pack(pady=20)

        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load sale details: {exc}")

    def delete_sale(self):
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sale to delete")
            return

        item = self.sales_tree.item(selection[0])
        sale_id = item["values"][0]
        sale_date = item["values"][1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete sale #{sale_id} from {sale_date}?\n\n"
            "This action cannot be undone and will also remove all associated sale items.",
        )

        if confirm:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                schema = self._get_sales_schema()
                sale_id_col = schema["sale_id"]

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
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to delete sale: {exc}")

    def update_sale_status(self):
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a sale to update")
            return

        item = self.sales_tree.item(selection[0])
        sale_id = item["values"][0]
        current_status = (item["values"][5] or "Pending").lower()

        status_window = tk.Toplevel(self.sales_window)
        status_window.title("Update Sale Status")
        status_window.configure(bg=self.bg_color)
        status_window.resizable(False, False)

        status_window.update_idletasks()
        width, height = 320, 200
        screen_width = status_window.winfo_screenwidth()
        screen_height = status_window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        status_window.geometry(f"{width}x{height}+{x}+{y}")

        form_frame = tk.Frame(status_window, bg=self.card_bg, relief="raised", bd=2)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            form_frame,
            text=f"Update Status for Sale #{sale_id}",
            font=("Arial", 14, "bold"),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(pady=(10, 15))

        tk.Label(
            form_frame,
            text="Select new status:",
            font=("Arial", 11),
            bg=self.card_bg,
            fg="#4A3728",
        ).pack(anchor="w")

        status_var = tk.StringVar(value=current_status.title())
        status_combo = ttk.Combobox(
            form_frame,
            textvariable=status_var,
            values=["Pending", "Paid", "Refunded", "Cancelled"],
            state="readonly",
            width=20,
        )
        status_combo.pack(pady=(0, 15))

        def apply_status_update():
            new_status = status_var.get().lower()
            if new_status == current_status:
                messagebox.showinfo("No Change", "Status is already set to the selected value.")
                status_window.destroy()
                return

            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                schema = self._get_sales_schema()
                sale_id_col = schema["sale_id"]
                status_col = schema.get("status") or "status"

                cursor.execute(
                    f"UPDATE sales SET {status_col} = %s WHERE {sale_id_col} = %s",
                    (new_status, sale_id),
                )

                if new_status == "paid" and current_status != "paid":
                    total_amount_col = schema["total_amount"]
                    customer_fk_col = schema["customer_fk"]
                    sale_item_sale_fk = schema["sale_item_sale_fk"]
                    sale_item_product_fk = schema["sale_item_product_fk"]
                    sale_item_qty = schema["sale_item_qty"]

                    cursor.execute(
                        f"""
                        SELECT {customer_fk_col} AS customer_id,
                               {total_amount_col} AS total_amount
                        FROM sales
                        WHERE {sale_id_col} = %s
                        """,
                        (sale_id,),
                    )
                    sale_row = cursor.fetchone() or {}
                    customer_id = sale_row.get("customer_id")
                    total_amount = sale_row.get("total_amount") or 0

                    if customer_id:
                        try:
                            total_amount_value = float(total_amount)
                        except (TypeError, ValueError):
                            total_amount_value = 0.0

                        cursor.execute(
                            """
                            UPDATE customers
                            SET total_spent = COALESCE(total_spent, 0) + %s,
                                loyalty_points = COALESCE(loyalty_points, 0) + CEIL(%s / 10)
                            WHERE customer_id = %s
                            """,
                            (total_amount_value, total_amount_value, customer_id),
                        )

                    cursor.execute(
                        f"""
                        SELECT si.{sale_item_product_fk} AS product_key,
                               si.{sale_item_qty} AS qty_value
                        FROM sale_items si
                        WHERE si.{sale_item_sale_fk} = %s
                        """,
                        (sale_id,),
                    )
                    sale_items = cursor.fetchall() or []

                    inventory_schema = self._get_schema()
                    inv_qty_col = inventory_schema["inv_qty"]
                    inv_prod_fk = inventory_schema["inv_prod_fk"]
                    inv_cols = self._get_table_columns("inventory")

                    deductions = {}
                    for item_row in sale_items:
                        product_key = item_row.get("product_key")
                        if product_key is None:
                            continue
                        try:
                            qty_value = int(item_row.get("qty_value") or 0)
                        except (TypeError, ValueError):
                            qty_value = 0
                        if qty_value <= 0:
                            continue
                        deductions[product_key] = deductions.get(product_key, 0) + qty_value

                    for product_key, qty_value in deductions.items():
                        set_clauses = [
                            f"{inv_qty_col} = GREATEST(0, COALESCE({inv_qty_col}, 0) - %s)"
                        ]
                        params = [qty_value]

                        if "current_stock" in inv_cols and inv_qty_col != "current_stock":
                            set_clauses.append(
                                "current_stock = GREATEST(0, COALESCE(current_stock, 0) - %s)"
                            )
                            params.append(qty_value)

                        params.append(product_key)

                        cursor.execute(
                            f"""
                            UPDATE inventory
                            SET {', '.join(set_clauses)}
                            WHERE {inv_prod_fk} = %s
                            """,
                            tuple(params),
                        )

                conn.commit()
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                cursor = None
                conn = None

                messagebox.showinfo("Success", f"Sale #{sale_id} status updated to {new_status.title()}")
                status_window.destroy()
                self.refresh_sales_list()
            except Exception as exc:
                try:
                    if cursor:
                        cursor.close()
                    if conn:
                        conn.rollback()
                        conn.close()
                except Exception:
                    pass
                messagebox.showerror("Error", f"Failed to update status: {exc}")

        button_container = tk.Frame(form_frame, bg=self.card_bg)
        button_container.pack(pady=(5, 10))

        tk.Button(
            button_container,
            text="Update",
            font=("Arial", 11, "bold"),
            bg="#28A745",
            fg="white",
            relief="flat",
            width=10,
            command=apply_status_update,
        ).pack(side="left", padx=5)

        tk.Button(
            button_container,
            text="Cancel",
            font=("Arial", 11),
            bg="#6C757D",
            fg="white",
            relief="flat",
            width=10,
            command=status_window.destroy,
        ).pack(side="left", padx=5)




    def _open_proof_of_payment(self, proof_path, proof_blob):
        """Open proof of payment attachment if available."""
        # Prefer existing file path
        if proof_path:
            try:
                normalized = Path(proof_path).expanduser().resolve()
                if normalized.exists():
                    if os.name == "nt":
                        os.startfile(normalized)  # nosec
                    else:
                        webbrowser.open(normalized.as_uri())
                    return
            except Exception:
                pass

        if proof_blob:
            try:
                suffix = Path(proof_path).suffix if proof_path else ".png"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(proof_blob)
                    temp_path = Path(tmp.name)
                if os.name == "nt":
                    os.startfile(temp_path)  # nosec
                else:
                    webbrowser.open(temp_path.as_uri())
                return
            except Exception as exc:
                messagebox.showerror("Proof of Payment", f"Unable to open attachment: {exc}")
                return

        messagebox.showinfo("Proof of Payment", "No proof of payment attachment is available for this sale.")
