"""
products.py
Operaciones CRUD (Create, Read, Update, Delete) sobre productos.

Conceptos SQL usados aquí:
- INSERT, SELECT, UPDATE, DELETE
- WHERE
- Parámetros (?) para evitar SQL injection
"""

from database import get_connection


def add_product(name, category="General", stock=0, min_stock=5, unit="unidades"):
    """Agrega un nuevo producto al inventario."""
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO products (name, category, stock, min_stock, unit)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, category, stock, min_stock, unit),
        )
        conn.commit()
        print(f"Producto '{name}' agregado correctamente.")
    except Exception as e:
        print(f"Error al agregar producto: {e}")
    finally:
        conn.close()


def list_products():
    """Devuelve todos los productos ordenados por nombre."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM products ORDER BY name ASC").fetchall()
    conn.close()
    return rows


def get_product_by_name(name):
    """Busca un producto por nombre exacto."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row


def update_min_stock(name, new_min_stock):
    """Actualiza el umbral de stock mínimo de un producto."""
    conn = get_connection()
    conn.execute(
        "UPDATE products SET min_stock = ? WHERE name = ?",
        (new_min_stock, name),
    )
    conn.commit()
    conn.close()


def delete_product(name):
    """Elimina un producto del inventario."""
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE name = ?", (name,))
    conn.commit()
    conn.close()


def low_stock_alert():
    """Devuelve productos cuyo stock está en o por debajo del mínimo."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM products WHERE stock <= min_stock ORDER BY stock ASC"
    ).fetchall()
    conn.close()
    return rows
