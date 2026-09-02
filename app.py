import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import products
import movements
import goods_in
import reports
import products
import movements
import goods_in

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Inventory System")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        self.create_layout()

    def create_layout(self):
        # =========================
        # MAIN CONTAINER
        # =========================
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True)

        # =========================
        # SIDEBAR
        # =========================
        sidebar = ttk.Frame(main, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # =========================
        # CONTENT AREA
        # =========================
        self.content = ttk.Frame(main)
        self.content.pack(side="right", fill="both", expand=True)

        # =========================
        # SIDEBAR TITLE
        # =========================
        title = ttk.Label(
            sidebar,
            text="INVENTORY SYSTEM",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=(25, 30))

        # =========================
        # NAVIGATION
        # =========================
        buttons = [
            "Dashboard",
            "Products",
            "Goods In",
            "Movements",
            "Alerts",
            "Reports",
        ]

        for name in buttons:
            button = ttk.Button(
                sidebar,
                text=name,
                command=lambda n=name: self.show_page(n)
            )
            button.pack(fill="x", padx=15, pady=5)

        # =========================
        # INITIAL PAGE
        # =========================
        self.show_page("Dashboard")

    def show_page(self, page_name):
        # Remove current content
        for widget in self.content.winfo_children():
            widget.destroy()

        if page_name == "Dashboard":
            self.show_dashboard()

        elif page_name == "Products":
            self.show_products()

        elif page_name == "Goods In":
            self.show_goods_in()
            
        elif page_name == "Movements":
            self.show_movements()
        
        elif page_name == "Alerts":
            self.show_alerts()
        
        elif page_name == "Reports":
            self.show_reports()        

        else:
            title = ttk.Label(
                self.content,
                text=page_name,
                font=("Segoe UI", 24, "bold")
            )
            title.pack(anchor="nw", padx=30, pady=30)

    def show_products(self):
        # =========================
        # HEADER
        # =========================
        header = ttk.Frame(self.content)
        header.pack(
            fill="x",
            padx=30,
            pady=(30, 20)
        )

        ttk.Label(
            header,
            text="Products",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Manage inventory products",
            font=("Segoe UI", 11)
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # =========================
        # TOOLBAR
        # =========================
        toolbar = ttk.Frame(self.content)
        toolbar.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        ttk.Label(
            toolbar,
            text="Search:"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.product_search = ttk.Entry(
            toolbar,
            width=35
        )

        self.product_search.pack(
            side="left"
        )

        ttk.Button(
            toolbar,
            text="+ Add Product",
            command=self.show_add_product_dialog
        ).pack(
            side="right"
        )
        
        ttk.Button(
            toolbar,
            text="Edit Product",
            command=self.edit_selected_product
        ).pack(
            side="right",
            padx=(0, 5)
        )
        ttk.Button(
            toolbar,
            text="Delete Product",
            command=self.delete_selected_product
        ).pack(
            side="right",
            padx=(0, 5)
        )
        # =========================
        # TABLE
        # =========================
        table_frame = ttk.Frame(self.content)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 20)
        )

        columns = (
            "name",
            "category",
            "stock",
            "min_stock",
            "unit"
        )

        self.products_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.products_tree.heading(
            "name",
            text="Name"
        )

        self.products_tree.heading(
            "category",
            text="Category"
        )

        self.products_tree.heading(
            "stock",
            text="Stock"
        )

        self.products_tree.heading(
            "min_stock",
            text="Min Stock"
        )

        self.products_tree.heading(
            "unit",
            text="Unit"
        )

        self.products_tree.column(
            "name",
            width=220
        )

        self.products_tree.column(
            "category",
            width=180
        )

        self.products_tree.column(
            "stock",
            width=100
        )

        self.products_tree.column(
            "min_stock",
            width=120
        )

        self.products_tree.column(
            "unit",
            width=120
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.products_tree.yview
        )

        self.products_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.products_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Search while typing
        self.product_search.bind(
            "<KeyRelease>",
            lambda event: self.refresh_products()
        )

        self.refresh_products()

    def refresh_products(self):
        if not hasattr(self, "products_tree"):
            return

        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        search_text = self.product_search.get().strip().lower()

        product_list = products.list_products()
        
        print("PRODUCTOS CARGADOS:", len(product_list))

        for product in product_list:
            name = str(product["name"] or "")
            category = str(product["category"] or "")

            if (
                search_text == ""
                or search_text in name.lower()
                or search_text in category.lower()
            ):
                self.products_tree.insert(
                    "",
                    "end",
                    values=(
                        product["name"],
                        product["category"],
                        product["stock"],
                        product["min_stock"],
                        product["unit"]
                    )
                )
    def show_add_product_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Product")
        dialog.geometry("450x520")
        dialog.resizable(False, False)

        dialog.transient(self)
        dialog.grab_set()

        frame = ttk.Frame(
            dialog,
            padding=25
        )
        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text="Add Product",
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w",
            pady=(0, 20)
        )

        fields = {}

        field_data = [
            ("Name", "name"),
            ("Category", "category"),
            ("Stock", "stock"),
            ("Minimum Stock", "min_stock"),
            ("Unit", "unit"),
        ]

        for label, key in field_data:
            ttk.Label(
                frame,
                text=label
            ).pack(
                anchor="w",
                pady=(8, 3)
            )

            entry = ttk.Entry(frame)
            entry.pack(
                fill="x"
            )

            fields[key] = entry

        def save_product():
            name = fields["name"].get().strip()
            category = fields["category"].get().strip() or "General"
            unit = fields["unit"].get().strip() or "unidades"

            if not name:
                messagebox.showwarning(
                    "Missing information",
                    "Product name is required.",
                    parent=dialog
                )
                return

            try:
                stock = int(fields["stock"].get().strip() or 0)
                min_stock = int(
                    fields["min_stock"].get().strip() or 5
                )
            except ValueError:
                messagebox.showerror(
                    "Invalid value",
                    "Stock values must be numbers.",
                    parent=dialog
                )
                return

            if stock < 0 or min_stock < 0:
                messagebox.showerror(
                    "Invalid value",
                    "Stock values cannot be negative.",
                    parent=dialog
                )
                return

            products.add_product(
                name,
                category,
                stock,
                min_stock,
                unit
            )

            dialog.destroy()
            self.show_page("Products")

        button_frame = ttk.Frame(frame)
        button_frame.pack(
            fill="x",
            side="bottom",
            pady=(25, 0)
        )

        ttk.Button(
            button_frame,
            text="Save Product",
            command=save_product
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5)
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(
            side="right",
            fill="x",
            expand=True,
            padx=(5, 0)
        ) 
    def delete_selected_product(self):
        selected = self.products_tree.selection()

        if not selected:
            messagebox.showinfo(
                "No selection",
                "Select a product from the table first."
            )
            return

        values = self.products_tree.item(
            selected[0],
            "values"
        )

        name = values[0]

        confirmed = messagebox.askyesno(
            "Delete Product",
            f"Are you sure you want to delete '{name}'?"
        )

        if not confirmed:
            return

        success, message = products.delete_product(name)

        if success:
            messagebox.showinfo(
                "Product Deleted",
                message
            )
            self.refresh_products()

        else:
            messagebox.showwarning(
                "Cannot Delete Product",
                message
            )
    def edit_selected_product(self):
        selected = self.products_tree.selection()

        if not selected:
            messagebox.showinfo(
                "No selection",
                "Select a product from the table first."
            )
            return

        values = self.products_tree.item(
            selected[0],
            "values"
        )

        name = values[0]
        category = values[1]
        stock = values[2]
        min_stock = values[3]
        unit = values[4]

        dialog = tk.Toplevel(self)
        dialog.title("Edit Product")
        dialog.geometry("450x520")
        dialog.resizable(False, False)

        dialog.transient(self)
        dialog.grab_set()

        frame = ttk.Frame(
            dialog,
            padding=25
        )
        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text="Edit Product",
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w",
            pady=(0, 20)
        )

        fields = {}

        field_data = [
            ("Name", "name", name),
            ("Category", "category", category),
            ("Stock", "stock", stock),
            ("Minimum Stock", "min_stock", min_stock),
            ("Unit", "unit", unit),
        ]

        for label, key, value in field_data:
            ttk.Label(
                frame,
                text=label
            ).pack(
                anchor="w",
                pady=(8, 3)
            )

            entry = ttk.Entry(frame)
            entry.pack(
                fill="x"
            )

            entry.insert(
                0,
                str(value or "")
            )

            fields[key] = entry

        def save_changes():
            new_name = fields["name"].get().strip()
            new_category = (
                fields["category"].get().strip()
                or "General"
            )
            new_unit = (
                fields["unit"].get().strip()
                or "unidades"
            )

            if not new_name:
                messagebox.showwarning(
                    "Missing information",
                    "Product name is required.",
                    parent=dialog
                )
                return

            try:
                new_stock = int(
                    fields["stock"].get().strip()
                )

                new_min_stock = int(
                    fields["min_stock"].get().strip()
                )

            except ValueError:
                messagebox.showerror(
                    "Invalid value",
                    "Stock values must be numbers.",
                    parent=dialog
                )
                return

            if new_stock < 0 or new_min_stock < 0:
                messagebox.showerror(
                    "Invalid value",
                    "Stock values cannot be negative.",
                    parent=dialog
                )
                return

            products.update_product(
                name,
                new_name,
                new_category,
                new_stock,
                new_min_stock,
                new_unit
            )

            dialog.destroy()
            self.show_page("Products")

        button_frame = ttk.Frame(frame)
        button_frame.pack(
            fill="x",
            side="bottom",
            pady=(25, 0)
        )

        ttk.Button(
            button_frame,
            text="Save Changes",
            command=save_changes
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5)
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(
            side="right",
            fill="x",
            expand=True,
            padx=(5, 0)
        )
    def show_goods_in(self):
        # =========================
        # HEADER
        # =========================
        header = ttk.Frame(self.content)
        header.pack(
            fill="x",
            padx=30,
            pady=(30, 20)
        )

        ttk.Label(
            header,
            text="Goods In",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Receive incoming stock",
            font=("Segoe UI", 11)
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # =========================
        # FORM CONTAINER
        # =========================
        form = ttk.LabelFrame(
            self.content,
            text="Receiving Information"
        )

        form.pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        # Make four columns expand
        for column in range(4):
            form.columnconfigure(
                column,
                weight=1
            )

        # =========================
        # PRODUCT
        # =========================
        ttk.Label(
            form,
            text="Product"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=(15, 5),
            sticky="w"
        )

        product_names = [
            product["name"]
            for product in products.list_products()
        ]

        product_entry = ttk.Combobox(
            form,
            values=product_names,
            state="normal"
        )

        product_entry.grid(
            row=1,
            column=0,
            padx=10,
            pady=(0, 15),
            sticky="ew"
        )

        # =========================
        # QUANTITY
        # =========================
        ttk.Label(
            form,
            text="Quantity"
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=(15, 5),
            sticky="w"
        )

        quantity_entry = ttk.Entry(form)
        quantity_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=(0, 15),
            sticky="ew"
        )

        # =========================
        # SUPPLIER
        # =========================
        ttk.Label(
            form,
            text="Supplier"
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=(15, 5),
            sticky="w"
        )

        supplier_entry = ttk.Entry(form)
        supplier_entry.grid(
            row=1,
            column=2,
            padx=10,
            pady=(0, 15),
            sticky="ew"
        )

        # =========================
        # PO NUMBER
        # =========================
        ttk.Label(
            form,
            text="PO Number"
        ).grid(
            row=0,
            column=3,
            padx=10,
            pady=(15, 5),
            sticky="w"
        )

        po_entry = ttk.Entry(form)
        po_entry.grid(
            row=1,
            column=3,
            padx=10,
            pady=(0, 15),
            sticky="ew"
        )

        # =========================
        # BATCH / LOT
        # =========================
        ttk.Label(
            form,
            text="Batch / Lot"
        ).grid(
            row=2,
            column=0,
            padx=10,
            pady=(5, 5),
            sticky="w"
        )

        batch_entry = ttk.Entry(form)
        batch_entry.grid(
            row=3,
            column=0,
            padx=10,
            pady=(0, 15),
            sticky="ew"
        )

        # =========================
        # EXPIRY DATE
        # =========================
        ttk.Label(
            form,
            text="Expiry Date"
        ).grid(
            row=2,
            column=1,
            padx=10,
            pady=(5, 5),
            sticky="w"
        )

        expiry_entry = ttk.Entry(form)
        expiry_entry.grid(
            row=3,
            column=1,
            padx=10,
            pady=(0, 15),
            sticky="ew"
        )

        # =========================
        # CATEGORY
        # =========================
        ttk.Label(
            form,
            text="Category"
        ).grid(
            row=2,
            column=2,
            padx=10,
            pady=(5, 5),
            sticky="w"
        )

        category_entry = ttk.Entry(form)
        category_entry.grid(
            row=3,
            column=2,
            padx=10,
            pady=(0, 15),
            sticky="ew"
        )

        # =========================
        # UNIT
        # =========================
        ttk.Label(
            form,
            text="Unit"
        ).grid(
            row=2,
            column=3,
            padx=10,
            pady=(5, 5),
            sticky="w"
        )

        unit_entry = ttk.Entry(form)
        unit_entry.grid(
            row=3,
            column=3,
            padx=10,
            pady=(0, 15),
            sticky="ew"
        )
        def fill_product_details(event=None):
            selected_name = product_entry.get().strip()

            if not selected_name:
                return

            product = products.get_product_by_name(selected_name)

            if product is None:
                return 

            category_entry.delete(0, tk.END)
            category_entry.insert(0, product["category"] or "")

            unit_entry.delete(0, tk.END)
            unit_entry.insert(0, product["unit"] or "")    
        product_entry.bind(
            "<<ComboboxSelected>>",
            fill_product_details
        )
        # =========================
        # NOTE
        # =========================
        ttk.Label(
            form,
            text="Note"
        ).grid(
            row=4,
            column=0,
            padx=10,
            pady=(5, 5),
            sticky="w"
        )

        note_entry = ttk.Entry(form)
        note_entry.grid(
            row=5,
            column=0,
            columnspan=4,
            padx=10,
            pady=(0, 15),
            sticky="ew"
        )
        product_entry.bind(
            "<<ComboboxSelected>>",
            fill_product_details
        )

        # =========================
        # RECEIVE BUTTON
        # =========================
        ttk.Button(
            form,
            text="Receive Goods",
            command=lambda: self.receive_goods_clicked(
                product_entry,
                quantity_entry,
                supplier_entry,
                po_entry,
                batch_entry,
                expiry_entry,
                category_entry,
                unit_entry,
                note_entry
            )
        ).grid(
            row=6,
            column=3,
            padx=10,
            pady=(0, 20),
            sticky="e"
        )
            # =========================
        # RECENT RECEIPTS
        # =========================
        history_frame = ttk.LabelFrame(
            self.content,
            text="Recent Receipts"
        )

        history_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 30)
        )

        columns = (
            "name",
            "quantity",
            "supplier",
            "po_number",
            "batch_lot",
            "expiry_date",
            "timestamp"
        )

        self.goods_in_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings"
        )

        headers = (
            "Product",
            "Quantity",
            "Supplier",
            "PO Number",
            "Batch / Lot",
            "Expiry",
            "Date"
        )

        for column, header_text in zip(columns, headers):
            self.goods_in_tree.heading(
                column,
                text=header_text
            )

        self.goods_in_tree.column("name", width=150)
        self.goods_in_tree.column("quantity", width=80)
        self.goods_in_tree.column("supplier", width=150)
        self.goods_in_tree.column("po_number", width=120)
        self.goods_in_tree.column("batch_lot", width=120)
        self.goods_in_tree.column("expiry_date", width=110)
        self.goods_in_tree.column("timestamp", width=150)

        scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=self.goods_in_tree.yview
        )

        self.goods_in_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.goods_in_tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        scrollbar.pack(
            side="right",
            fill="y",
            pady=10
        )

        self.refresh_goods_in_history()
    def refresh_goods_in_history(self):
        for item in self.goods_in_tree.get_children():
            self.goods_in_tree.delete(item)

        for row in goods_in.goods_in_history(limit=100):
            self.goods_in_tree.insert(
                "",
                "end",
                values=(
                    row["name"],
                    row["quantity"],
                    row["supplier"] or "",
                    row["po_number"] or "",
                    row["batch_lot"] or "",
                    row["expiry_date"] or "",
                    row["timestamp"]
                )
            )        
    def receive_goods_clicked(
        self,
        product_entry,
        quantity_entry,
        supplier_entry,
        po_entry,
        batch_entry,
        expiry_entry,
        category_entry,
        unit_entry,
        note_entry
    ):
        product_name = product_entry.get().strip()

        if not product_name:
            messagebox.showwarning(
                "Missing information",
                "Product name is required."
            )
            return

        quantity_text = quantity_entry.get().strip()

        if not quantity_text:
            messagebox.showerror(
                "Invalid quantity",
                "Please enter a quantity."
            )
            return

        try:
            quantity = int(quantity_text)
        except ValueError:
            messagebox.showerror(
                "Invalid quantity",
                "Quantity must be a whole number."
            )
            return

        if quantity <= 0:
            messagebox.showerror(
                "Invalid quantity",
                "Quantity must be greater than 0."
            )
            return

        supplier = supplier_entry.get().strip() or None
        po_number = po_entry.get().strip() or None
        batch_lot = batch_entry.get().strip() or None
        expiry_date = expiry_entry.get().strip() or None
            
        if expiry_date:
            try:
                datetime.strptime(
                    expiry_date,
                    "%Y-%m-%d"
                )
            except ValueError:
                messagebox.showerror(
                     "Invalid expiry date",
                     "Expiry date must use YYYY-MM-DD format."
                )
                return
        
        category = category_entry.get().strip() or "General"
        unit = unit_entry.get().strip() or "unidades"
        note = note_entry.get().strip()

        goods_in.receive_goods(
           product_name=product_name,
           quantity=quantity,
           supplier=supplier,
           po_number=po_number,
           batch_lot=batch_lot,
           expiry_date=expiry_date,
           note=note,
           category=category,
           unit=unit
        )

        messagebox.showinfo(
            "Goods received",
            f"{quantity} unit(s) of '{product_name}' received successfully."
        )
        self.show_page("Goods In")
    
    def show_movements(self):
        # =========================
        # HEADER
        # =========================
        header = ttk.Frame(self.content)
        header.pack(
            fill="x",
            padx=30,
            pady=(30, 20)
        )

        ttk.Label(
            header,
            text="Movements",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Record inventory IN and OUT movements",
            font=("Segoe UI", 11)
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # =========================
        # FORM
        # =========================
        form_frame = ttk.LabelFrame(
            self.content,
            text="New Movement"
        )
        form_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        # Row 1
        row1 = ttk.Frame(form_frame)
        row1.pack(
            fill="x",
            padx=15,
            pady=(15, 8)
        )

        ttk.Label(
            row1,
            text="Product:"
        ).grid(
            row=0,
            column=0,
            padx=(0, 8),
            sticky="w"
        )

        product_entry = ttk.Combobox(
            row1,
            state="normal",
            width=28
        )
        product_entry.grid(
            row=0,
            column=1,
            padx=(0, 20),
            sticky="ew"
        )

        product_entry["values"] = [
            row["name"]
            for row in products.list_products()
        ]

        ttk.Label(
            row1,
            text="Type:"
        ).grid(
            row=0,
            column=2,
            padx=(0, 8),
            sticky="w"
        )

        movement_type = ttk.Combobox(
            row1,
            state="readonly",
            values=("IN", "OUT"),
            width=12
        )
        movement_type.set("OUT")
        movement_type.grid(
            row=0,
            column=3,
            padx=(0, 20),
            sticky="w"
        )

        ttk.Label(
            row1,
            text="Quantity:"
        ).grid(
            row=0,
            column=4,
            padx=(0, 8),
            sticky="w"
        )

        quantity_entry = ttk.Entry(
            row1,
            width=15
        )
        quantity_entry.grid(
            row=0,
            column=5,
            sticky="w"
        )

        row1.columnconfigure(1, weight=1)

        # Row 2
        row2 = ttk.Frame(form_frame)
        row2.pack(
            fill="x",
            padx=15,
            pady=8
        )

        ttk.Label(
            row2,
            text="Note:"
        ).grid(
            row=0,
            column=0,
            padx=(0, 8),
            sticky="w"
        )

        note_entry = ttk.Entry(row2)
        note_entry.grid(
            row=0,
            column=1,
            columnspan=5,
            sticky="ew"
        )

        row2.columnconfigure(1, weight=1)

        # =========================
        # BUTTON
        # =========================
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(
            fill="x",
            padx=15,
            pady=(8, 15)
        )

        ttk.Button(
            button_frame,
            text="Record Movement",
            command=lambda: self.record_movement_clicked(
                product_entry,
                movement_type,
                quantity_entry,
                note_entry
            )
        ).pack(
            side="right"
        )
        # =========================
        # HISTORY FILTERS
        # =========================
        filter_frame = ttk.Frame(self.content)
        filter_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 10)
        )

        ttk.Label(
            filter_frame,
            text="Type:"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        movement_filter = ttk.Combobox(
            filter_frame,
            state="readonly",
            values=("All", "IN", "OUT"),
            width=10
        )
        movement_filter.set("All")
        movement_filter.pack(
            side="left",
            padx=(0, 25)
        )

        ttk.Label(
            filter_frame,
            text="Search product:"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        search_entry = ttk.Entry(
            filter_frame,
            width=30
        )
        search_entry.pack(
            side="left"
        )
        # =========================
        # HISTORY
        # =========================
        history_frame = ttk.LabelFrame(
            self.content,
            text="Movement History"
        )
        history_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 30)
        )

        columns = (
            "Product",
            "Type",
            "Quantity",
            "Note",
            "Date"
        )

        self.movements_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings"
        )

        for column in columns:
            self.movements_tree.heading(
                column,
                text=column
            )

        self.movements_tree.column(
            "Product",
            width=180
        )
        self.movements_tree.column(
            "Type",
            width=80,
            anchor="center"
        )
        self.movements_tree.column(
            "Quantity",
            width=90,
            anchor="center"
        )
        self.movements_tree.column(
            "Note",
            width=300
        )
        self.movements_tree.column(
            "Date",
            width=180
        )

        scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=self.movements_tree.yview
        )

        self.movements_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.movements_tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=10
        )

        scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 10),
            pady=10
        )

        # =========================
        # LOAD HISTORY
        # =========================
        def refresh_movement_history(*args):
            for item in self.movements_tree.get_children():
                self.movements_tree.delete(item)

            selected_type = movement_filter.get()
            search_text = search_entry.get().strip().lower()

            for row in movements.movement_history(limit=100):
                product_name = row["name"]
                movement_type_value = row["movement_type"]

                if selected_type != "All":
                    if movement_type_value != selected_type:
                        continue

                if search_text:
                    if search_text not in product_name.lower():
                        continue

                self.movements_tree.insert(
                    "",
                    "end",
                    values=(
                        product_name,
                        movement_type_value,
                        row["quantity"],
                        row["note"] or "",
                        row["timestamp"]
                    )
                )

        movement_filter.bind(
            "<<ComboboxSelected>>",
            refresh_movement_history
        )

        search_entry.bind(
            "<KeyRelease>",
            refresh_movement_history
        )

        refresh_movement_history()
    def record_movement_clicked(
        self,
        product_entry,
        movement_type,
        quantity_entry,
        note_entry
    ):
        product_name = product_entry.get().strip()

        if not product_name:
            messagebox.showwarning(
                "Missing information",
                "Product name is required."
            )
            return

        movement = movement_type.get().strip().upper()

        if movement not in ("IN", "OUT"):
            messagebox.showerror(
                "Invalid movement",
                "Movement type must be IN or OUT."
            )
            return

        quantity_text = quantity_entry.get().strip()

        if not quantity_text:
            messagebox.showerror(
                "Invalid quantity",
                "Please enter a quantity."
            )
            return

        try:
            quantity = int(quantity_text)
        except ValueError:
            messagebox.showerror(
                "Invalid quantity",
                "Quantity must be a whole number."
            )
            return

        if quantity <= 0:
            messagebox.showerror(
                "Invalid quantity",
                "Quantity must be greater than 0."
            )
            return

        note = note_entry.get().strip()

        success, message = movements.record_movement(
            product_name=product_name,
            movement_type=movement,
            quantity=quantity,
            note=note
        )

        if success:
            messagebox.showinfo(
                "Movement recorded",
                message
            )
            self.show_page("Movements")
        else:
            messagebox.showerror(
                "Movement not recorded",
                message
            )
    def show_alerts(self):
        # =========================
        # HEADER
        # =========================
        header = ttk.Frame(self.content)
        header.pack(
            fill="x",
            padx=30,
            pady=(30, 20)
        )

        ttk.Label(
            header,
            text="Alerts",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Low stock and expiry alerts",
            font=("Segoe UI", 11)
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # =========================
        # GET DATA
        # =========================
        low_stock = products.low_stock_alert()
        expiring = goods_in.expiring_soon()

        # =========================
        # LOW STOCK
        # =========================
        low_stock_frame = ttk.LabelFrame(
            self.content,
            text=f"Low Stock ({len(low_stock)})"
        )
        low_stock_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 15)
        )

        low_columns = (
            "Product",
            "Stock",
            "Minimum",
            "Unit"
        )

        low_tree = ttk.Treeview(
            low_stock_frame,
            columns=low_columns,
            show="headings",
            height=6
        )

        for column in low_columns:
            low_tree.heading(
                column,
                text=column
            )

        low_tree.column(
            "Product",
            width=250
        )
        low_tree.column(
            "Stock",
            width=100,
            anchor="center"
        )
        low_tree.column(
            "Minimum",
            width=100,
            anchor="center"
        )
        low_tree.column(
            "Unit",
            width=150
        )

        for row in low_stock:
            low_tree.insert(
                "",
                "end",
                values=(
                    row["name"],
                    row["stock"],
                    row["min_stock"],
                    row["unit"]
                )
            )

        low_tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # =========================
        # EXPIRING SOON
        # =========================
        expiring_frame = ttk.LabelFrame(
            self.content,
            text=f"Expiring Soon ({len(expiring)})"
        )
        expiring_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 30)
        )

        exp_columns = (
            "Product",
            "Quantity",
            "Batch/Lot",
            "Expiry Date"
        )

        exp_tree = ttk.Treeview(
            expiring_frame,
            columns=exp_columns,
            show="headings",
            height=6
        )

        for column in exp_columns:
            exp_tree.heading(
                column,
                text=column
            )

        exp_tree.column(
            "Product",
            width=250
        )
        exp_tree.column(
            "Quantity",
            width=100,
            anchor="center"
        )
        exp_tree.column(
            "Batch/Lot",
            width=180
        )
        exp_tree.column(
            "Expiry Date",
            width=150,
            anchor="center"
        )

        for row in expiring:
            exp_tree.insert(
                "",
                "end",
                values=(
                    row["name"],
                    row["quantity"],
                    row["batch_lot"] or "",
                    row["expiry_date"]
                )
            )

        exp_tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        ) 
    def show_reports(self):
        # =========================
        # HEADER
        # =========================
        header = ttk.Frame(self.content)
        header.pack(
            fill="x",
            padx=30,
            pady=(30, 20)
        )

        ttk.Label(
            header,
            text="Reports",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Inventory and movement reports",
            font=("Segoe UI", 11)
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # =========================
        # GET DATA
        # =========================
        product_list = products.list_products()
        avg_stock = reports.average_stock()
        movement_summary = reports.movement_summary()
        category_data = reports.total_stock_value_by_category()
        product_totals = reports.movement_totals_by_product()

        # =========================
        # KPI CARDS
        # =========================
        cards = ttk.Frame(self.content)
        cards.pack(
            fill="x",
            padx=30,
            pady=10
        )

        self.create_card(
            cards,
            "PRODUCTS",
            len(product_list),
            0
        )

        self.create_card(
            cards,
            "AVERAGE STOCK",
            round(avg_stock or 0, 1),
            1
        )

        self.create_card(
            cards,
            "TOTAL MOVEMENTS",
            movement_summary["total_movements"] or 0,
            2
        )

        self.create_card(
            cards,
            "IN / OUT",
            f"{movement_summary['in_movements'] or 0} / "
            f"{movement_summary['out_movements'] or 0}",
            3
        )

        # =========================
        # STOCK BY CATEGORY
        # =========================
        category_frame = ttk.LabelFrame(
            self.content,
            text="Stock by Category"
        )
        category_frame.pack(
            fill="x",
            padx=30,
            pady=(15, 10)
        )

        category_columns = (
            "Category",
            "Total Units",
            "Products"
        )

        category_tree = ttk.Treeview(
            category_frame,
            columns=category_columns,
            show="headings",
            height=5
        )

        for column in category_columns:
            category_tree.heading(
                column,
                text=column
            )

        category_tree.column(
            "Category",
            width=250
        )
        category_tree.column(
            "Total Units",
            width=150,
            anchor="center"
        )
        category_tree.column(
            "Products",
            width=150,
            anchor="center"
        )

        for row in category_data:
            category_tree.insert(
                "",
                "end",
                values=(
                    row["category"],
                    row["total_units"],
                    row["num_products"]
                )
            )

        category_tree.pack(
            fill="x",
            padx=10,
            pady=10
        )

        # =========================
        # MOVEMENT SUMMARY
        # =========================
        summary_frame = ttk.LabelFrame(
            self.content,
            text="Movement Summary"
        )
        summary_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        summary_columns = (
            "IN Movements",
            "OUT Movements",
            "Total IN",
            "Total OUT"
        )

        summary_tree = ttk.Treeview(
            summary_frame,
            columns=summary_columns,
            show="headings",
            height=2
        )

        for column in summary_columns:
            summary_tree.heading(
                column,
                text=column
            )
            summary_tree.column(
                column,
                width=180,
                anchor="center"
            )

        summary_tree.insert(
            "",
            "end",
            values=(
                movement_summary["in_movements"] or 0,
                movement_summary["out_movements"] or 0,
                movement_summary["total_in"] or 0,
                movement_summary["total_out"] or 0
            )
        )

        summary_tree.pack(
            fill="x",
            padx=10,
            pady=10
        )

        # =========================
        # MOVEMENT TOTALS
        # =========================
        totals_frame = ttk.LabelFrame(
            self.content,
            text="Movement Totals by Product"
        )
        totals_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(10, 30)
        )

        totals_columns = (
            "Product",
            "Category",
            "Total IN",
            "Total OUT",
            "Movements"
        )

        totals_tree = ttk.Treeview(
            totals_frame,
            columns=totals_columns,
            show="headings"
        )

        for column in totals_columns:
            totals_tree.heading(
                column,
                text=column
            )

        totals_tree.column(
            "Product",
            width=200
        )
        totals_tree.column(
            "Category",
            width=150
        )
        totals_tree.column(
            "Total IN",
            width=120,
            anchor="center"
        )
        totals_tree.column(
            "Total OUT",
            width=120,
            anchor="center"
        )
        totals_tree.column(
            "Movements",
            width=120,
            anchor="center"
        )

        for row in product_totals:
            totals_tree.insert(
                "",
                "end",
                values=(
                    row["name"],
                    row["category"],
                    row["total_in"] or 0,
                    row["total_out"] or 0,
                    row["total_movements"] or 0
                )
            )

        totals_tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )       
    def show_dashboard(self):
        # =========================
        # DASHBOARD HEADER
        # =========================
        header = ttk.Frame(self.content)
        header.pack(fill="x", padx=30, pady=(30, 20))

        title = ttk.Label(
            header,
            text="Dashboard",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            header,
            text="Inventory overview",
            font=("Segoe UI", 11)
        )
        subtitle.pack(anchor="w", pady=(5, 0))

        # =========================
        # GET DATA
        # =========================
        product_list = products.list_products()
        low_stock = products.low_stock_alert()
        expiring = goods_in.expiring_soon()
        recent_movements = movements.movement_history(limit=5)

        total_products = len(product_list)
        total_stock = sum(product["stock"] for product in product_list)

        # =========================
        # KPI CARDS
        # =========================
        cards = ttk.Frame(self.content)
        cards.pack(fill="x", padx=30, pady=10)

        self.create_card(
            cards,
            "PRODUCTS",
            total_products,
            0)
        

        self.create_card(
            cards,
            "TOTAL STOCK",
            total_stock,
            1)
        

        self.create_card(
            cards,
            "LOW STOCK",
            len(low_stock),
            2)
        

        self.create_card(
            cards,
            "EXPIRING SOON",
            len(expiring),
            3)
        

        # =========================
        # RECENT MOVEMENTS
        # =========================
        movements_frame = ttk.LabelFrame(
            self.content,
            text="Recent Movements"
        )
        movements_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(20, 30)
        )

        columns = (
            "product",
            "type",
            "quantity",
            "note",
            "timestamp"
        )

        tree = ttk.Treeview(
            movements_frame,
            columns=columns,
            show="headings"
        )

        tree.heading("product", text="Product")
        tree.heading("type", text="Type")
        tree.heading("quantity", text="Quantity")
        tree.heading("note", text="Note")
        tree.heading("timestamp", text="Date")

        tree.column("product", width=180)
        tree.column("type", width=100)
        tree.column("quantity", width=100)
        tree.column("note", width=250)
        tree.column("timestamp", width=180)

        for movement in recent_movements:
            tree.insert(
                "",
                "end",
                values=(
                    movement["name"],
                    movement["movement_type"],
                    movement["quantity"],
                    movement["note"],
                    movement["timestamp"]
                )
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    def create_card(self, parent, label, value, column):
        card = ttk.Frame(
            parent,
            relief="solid",
            borderwidth=1,
        )

        card.grid(
            row=0,
            column=column,
            padx=5,
            sticky="nsew"
        )

        parent.columnconfigure(column, weight=1)

        label_widget = ttk.Label(
            card,
            text=label,
            font=("Segoe UI", 10, "bold")
        )
        label_widget.pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        value_widget = ttk.Label(
            card,
            text=str(value),
            font=("Segoe UI", 22, "bold")
        )
        value_widget.pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()