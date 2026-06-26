"""
reports.py
Reportes agregados sobre el inventario.

Conceptos SQL usados aquí:
- GROUP BY
- Funciones agregadas: SUM, COUNT, AVG
- Subqueries
"""

from database import get_connection


def total_stock_value_by_category():
    """Cuenta cuántas unidades hay en stock, agrupado por categoría."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT category, SUM(stock) AS total_units, COUNT(*) AS num_products
        FROM products
        GROUP BY category
        ORDER BY total_units DESC
    """).fetchall()
    conn.close()
    return rows


def most_moved_products(limit=5):
    """Productos con más movimientos registrados (entradas + salidas)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.name, COUNT(m.id) AS total_movements,
               SUM(CASE WHEN m.movement_type = 'IN' THEN m.quantity ELSE 0 END) AS total_in,
               SUM(CASE WHEN m.movement_type = 'OUT' THEN m.quantity ELSE 0 END) AS total_out
        FROM movements m
        JOIN products p ON m.product_id = p.id
        GROUP BY p.name
        ORDER BY total_movements DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows


def products_never_moved():
    """Productos que nunca tuvieron un movimiento registrado (subquery)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT *
        FROM products
        WHERE id NOT IN (SELECT DISTINCT product_id FROM movements)
    """).fetchall()
    conn.close()
    return rows


def average_stock():
    """Promedio de stock entre todos los productos."""
    conn = get_connection()
    row = conn.execute("SELECT AVG(stock) AS avg_stock FROM products").fetchone()
    conn.close()
    return row["avg_stock"]
