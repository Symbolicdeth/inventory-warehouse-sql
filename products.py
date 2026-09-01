"""
products.py
Operaciones CRUD (Create, Read, Update, Delete) sobre productos.

Conceptos SQL :
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
def update_product(name, new_name, new_category, new_stock,
                   new_min_stock, new_unit):
    """Actualiza todos los datos de un producto."""
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE products
            SET name = ?,
                category = ?,
                stock = ?,
                min_stock = ?,
                unit = ?
            WHERE name = ?
            """,
            (
                new_name,
                new_category,
                new_stock,
                new_min_stock,
                new_unit,
                name,
            ),
        )
        conn.commit()
        print(f"Producto '{name}' actualizado correctamente.")
    except Exception as e:
        print(f"Error al actualizar producto: {e}")
    finally:
        conn.close()

def delete_product(name):
    """Elimina un producto solo si no tiene movimientos asociados."""
    conn = get_connection()

    try:
        product = conn.execute(
            "SELECT id FROM products WHERE name = ?",
            (name,)
        ).fetchone()

        if product is None:
            return False, "Product not found."

        movement_count = conn.execute(
            "SELECT COUNT(*) FROM movements WHERE product_id = ?",
            (product["id"],)
        ).fetchone()[0]

        if movement_count > 0:
            return False, (
                f"Cannot delete '{name}' because it has "
                f"{movement_count} movement(s) in the history."
            )

        conn.execute(
            "DELETE FROM products WHERE id = ?",
            (product["id"],)
        )

        conn.commit()

        return True, f"'{name}' was deleted successfully."

    except Exception as e:
        conn.rollback()
        return False, f"Error deleting product: {e}"

    finally:
        conn.close()


def low_stock_alert():
    """Devuelve productos cuyo stock está en o por debajo del mínimo."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM products WHERE stock <= min_stock ORDER BY stock ASC"
    ).fetchall()
    conn.close()
    return rows
