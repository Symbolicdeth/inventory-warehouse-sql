"""
app.py
Interfaz de escritorio (Tkinter) para el sistema de inventario.
Reutiliza toda la lógica ya existente en database.py, products.py,
movements.py, goods_in.py y reports.py — esto es solo la capa visual.

Ejecutar con: python app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

from database import setup_database
from products import (
    add_product,
    list_products,
    update_min_stock,
    delete_product,
    low_stock_alert,
)
from movements import movement_history
from goods_in import receive_goods, goods_in_history, expiring_soon
from reports import (
    total_stock_value_by_category,
    most_moved_products,
    products_never_moved,
    average_stock,
)


# ---------------------------------------------------------------------------
# Ventana principal
# ---------------------------------------------------------------------------

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Inventario")
        self.geometry("950x600")
        self.minsize(800, 500)

        setup_database()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.products_tab = ProductsTab(notebook)
        self.goods_in_tab = GoodsInTab(notebook)
        self.movements_tab = MovementsTab(notebook)
        self.alerts_tab = AlertsTab(notebook)
        self.reports_tab = ReportsTab(notebook)

        notebook.add(self.products_tab, text="Productos")
        notebook.add(self.goods_in_tab, text="Goods In (Recepción)")
        notebook.add(self.movements_tab, text="Movimientos")
        notebook.add(self.alerts_tab, text="Alertas")
        notebook.add(self.reports_tab, text="Reportes")

        # Refrescar pestañas dependientes cuando se cambia de tab
        notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_all())

    def refresh_all(self):
        self.products_tab.refresh()
        self.alerts_tab.refresh()
        self.reports_tab.refresh()
        self.movements_tab.refresh()


# ---------------------------------------------------------------------------
# Pestaña: Productos
# ---------------------------------------------------------------------------

class ProductsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Agregar producto nuevo")
        form.pack(fill="x", padx=10, pady=10)

        labels = ["Nombre", "Categoría", "Stock inicial", "Stock mínimo", "Unidad"]
        self.entries = {}
        for i, label in enumerate(labels):
            ttk.Label(form, text=label).grid(row=0, column=i, padx=5, pady=5)
            entry = ttk.Entry(form, width=14)
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.entries[label] = entry

        ttk.Button(form, text="Agregar", command=self.add_product_clicked).grid(
            row=1, column=len(labels), padx=10
        )

    def _build_table(self):
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "name", "category", "stock", "min_stock", "unit")
        headers = ("ID", "Nombre", "Categoría", "Stock", "Mínimo", "Unidad")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, head in zip(columns, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=120 if col != "id" else 50)
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Eliminar seleccionado", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Actualizar", command=self.refresh).pack(side="left", padx=5)

    def add_product_clicked(self):
        name = self.entries["Nombre"].get().strip()
        if not name:
            messagebox.showwarning("Falta info", "El nombre del producto es obligatorio.")
            return
        category = self.entries["Categoría"].get().strip() or "General"
        unit = self.entries["Unidad"].get().strip() or "unidades"
        try:
            stock = int(self.entries["Stock inicial"].get().strip() or 0)
            min_stock = int(self.entries["Stock mínimo"].get().strip() or 5)
        except ValueError:
            messagebox.showerror("Error", "Stock y stock mínimo deben ser números.")
            return

        add_product(name, category, stock, min_stock, unit)
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.refresh()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Nada seleccionado", "Elegí un producto de la tabla primero.")
            return
        name = self.tree.item(selected[0])["values"][1]
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{name}'?"):
            delete_product(name)
            self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in list_products():
            self.tree.insert("", "end", values=(p["id"], p["name"], p["category"], p["stock"], p["min_stock"], p["unit"]))


# ---------------------------------------------------------------------------
# Pestaña: Goods In (Recepción)
# ---------------------------------------------------------------------------

class GoodsInTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Registrar recepción de mercadería")
        form.pack(fill="x", padx=10, pady=10)

        fields = [
            ("Producto", "Producto"),
            ("Cantidad", "Cantidad"),
            ("Proveedor", "Proveedor"),
            ("Remito / PO", "PO"),
            ("Lote", "Lote"),
            ("Vencimiento (YYYY-MM-DD)", "Vencimiento"),
        ]
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            r, c = divmod(i, 3)
            ttk.Label(form, text=label).grid(row=r * 2, column=c, padx=5, pady=(5, 0), sticky="w")
            entry = ttk.Entry(form, width=22)
            entry.grid(row=r * 2 + 1, column=c, padx=5, pady=(0, 5), sticky="w")
            self.entries[key] = entry

        ttk.Button(form, text="Registrar recepción", command=self.receive_clicked).grid(
            row=4, column=0, columnspan=3, pady=10
        )

    def _build_table(self):
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("name", "quantity", "supplier", "po_number", "batch_lot", "expiry_date", "timestamp")
        headers = ("Producto", "Cant.", "Proveedor", "Remito", "Lote", "Vence", "Fecha")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, head in zip(columns, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def receive_clicked(self):
        name = self.entries["Producto"].get().strip()
        if not name:
            messagebox.showwarning("Falta info", "El nombre del producto es obligatorio.")
            return
        try:
            qty = int(self.entries["Cantidad"].get().strip())
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número.")
            return

        supplier = self.entries["Proveedor"].get().strip() or None
        po = self.entries["PO"].get().strip() or None
        batch = self.entries["Lote"].get().strip() or None
        expiry = self.entries["Vencimiento"].get().strip() or None

        receive_goods(name, qty, supplier=supplier, po_number=po,
                      batch_lot=batch, expiry_date=expiry)

        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.refresh()
        messagebox.showinfo("Listo", f"Recepción de '{name}' registrada.")

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in goods_in_history():
            self.tree.insert("", "end", values=(
                r["name"], r["quantity"], r["supplier"] or "", r["po_number"] or "",
                r["batch_lot"] or "", r["expiry_date"] or "", r["timestamp"]
            ))


# ---------------------------------------------------------------------------
# Pestaña: Movimientos (historial general)
# ---------------------------------------------------------------------------

class MovementsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(filter_frame, text="Filtrar por producto (vacío = todos):").pack(side="left", padx=5)
        self.filter_entry = ttk.Entry(filter_frame, width=25)
        self.filter_entry.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Buscar", command=self.refresh).pack(side="left", padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("name", "movement_type", "quantity", "note", "timestamp")
        headers = ("Producto", "Tipo", "Cantidad", "Nota", "Fecha")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, head in zip(columns, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        name_filter = self.filter_entry.get().strip() or None
        for m in movement_history(name_filter, limit=100):
            self.tree.insert("", "end", values=(
                m["name"], m["movement_type"], m["quantity"], m["note"] or "", m["timestamp"]
            ))


# ---------------------------------------------------------------------------
# Pestaña: Alertas (stock bajo + vencimientos)
# ---------------------------------------------------------------------------

class AlertsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        low_frame = ttk.LabelFrame(self, text="⚠️ Stock bajo")
        low_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("name", "stock", "min_stock", "unit")
        self.low_tree = ttk.Treeview(low_frame, columns=columns, show="headings", height=6)
        for col, head in zip(columns, ("Producto", "Stock", "Mínimo", "Unidad")):
            self.low_tree.heading(col, text=head)
            self.low_tree.column(col, width=140)
        self.low_tree.pack(fill="both", expand=True, padx=5, pady=5)

        exp_frame = ttk.LabelFrame(self, text="⏳ Próximos a vencer (7 días)")
        exp_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns2 = ("name", "batch_lot", "expiry_date", "quantity", "supplier")
        self.exp_tree = ttk.Treeview(exp_frame, columns=columns2, show="headings", height=6)
        for col, head in zip(columns2, ("Producto", "Lote", "Vence", "Cantidad", "Proveedor")):
            self.exp_tree.heading(col, text=head)
            self.exp_tree.column(col, width=140)
        self.exp_tree.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(self, text="Actualizar alertas", command=self.refresh).pack(pady=5)

        self.refresh()

    def refresh(self):
        for row in self.low_tree.get_children():
            self.low_tree.delete(row)
        for p in low_stock_alert():
            self.low_tree.insert("", "end", values=(p["name"], p["stock"], p["min_stock"], p["unit"]))

        for row in self.exp_tree.get_children():
            self.exp_tree.delete(row)
        for r in expiring_soon(7):
            self.exp_tree.insert("", "end", values=(
                r["name"], r["batch_lot"] or "", r["expiry_date"], r["quantity"], r["supplier"] or ""
            ))


# ---------------------------------------------------------------------------
# Pestaña: Reportes
# ---------------------------------------------------------------------------

class ReportsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.text = tk.Text(self, wrap="word", font=("Consolas", 10))
        self.text.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Button(self, text="Actualizar reportes", command=self.refresh).pack(pady=5)
        self.refresh()

    def refresh(self):
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)

        self.text.insert(tk.END, "--- Stock total por categoría ---\n")
        for r in total_stock_value_by_category():
            self.text.insert(tk.END, f"  {r['category']}: {r['total_units']} unidades en {r['num_products']} productos\n")

        self.text.insert(tk.END, "\n--- Productos con más movimiento ---\n")
        for r in most_moved_products():
            self.text.insert(tk.END, f"  {r['name']}: {r['total_movements']} movimientos (IN: {r['total_in']}, OUT: {r['total_out']})\n")

        self.text.insert(tk.END, "\n--- Productos sin movimientos registrados ---\n")
        rows = products_never_moved()
        if not rows:
            self.text.insert(tk.END, "  (todos los productos tuvieron al menos un movimiento)\n")
        for r in rows:
            self.text.insert(tk.END, f"  {r['name']} (stock: {r['stock']})\n")

        avg = average_stock()
        self.text.insert(tk.END, f"\nStock promedio entre todos los productos: {avg:.2f}\n" if avg else "\nNo hay datos suficientes.\n")

        self.text.config(state="disabled")


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
