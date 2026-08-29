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

def low_stock_products():
    """Devuelve productos cuyo stock está en o por debajo del mínimo."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, name, category, stock, min_stock, unit
        FROM products
        WHERE stock <= min_stock
        ORDER BY stock ASC, name ASC
    """).fetchall()
    conn.close()
    return rows

def movement_summary():
    """Devuelve un resumen de entradas y salidas de stock."""
    conn = get_connection()

    row = conn.execute("""
        SELECT
            COUNT(*) AS total_movements,
            SUM(CASE WHEN movement_type = 'IN' THEN 1 ELSE 0 END) AS in_movements,
            SUM(CASE WHEN movement_type = 'OUT' THEN 1 ELSE 0 END) AS out_movements,
            SUM(CASE WHEN movement_type = 'IN' THEN quantity ELSE 0 END) AS total_in,
            SUM(CASE WHEN movement_type = 'OUT' THEN quantity ELSE 0 END) AS total_out
        FROM movements
    """).fetchone()

    conn.close()
    return row

def movement_totals_by_product():
    """Resume entradas y salidas acumuladas por producto."""
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            p.name,
            p.category,
            SUM(CASE
                WHEN m.movement_type = 'IN' THEN m.quantity
                ELSE 0
            END) AS total_in,
            SUM(CASE
                WHEN m.movement_type = 'OUT' THEN m.quantity
                ELSE 0
            END) AS total_out,
            COUNT(m.id) AS total_movements
        FROM products p
        LEFT JOIN movements m ON p.id = m.product_id
        GROUP BY p.id, p.name, p.category
        ORDER BY total_movements DESC, p.name ASC
    """).fetchall()

    conn.close()
    return rows