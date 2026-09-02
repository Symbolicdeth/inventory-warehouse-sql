"""
movements.py
Registra entradas/salidas de stock y mantiene el historial.

Conceptos SQL usados aquí:
- Transacciones (commit/rollback)
- JOIN entre movements y products
- ORDER BY, LIMIT
"""

from database import get_connection


def record_movement(
    product_name,
    movement_type,
    quantity,
    note="",
    supplier=None,
    po_number=None,
    batch_lot=None,
    expiry_date=None
):
    """
    Registra un movimiento de stock (IN o OUT) y actualiza el stock.
    Devuelve (True, mensaje) si tiene éxito o (False, mensaje) si falla.
    """
    movement_type = movement_type.upper()

    if movement_type not in ("IN", "OUT"):
        message = "Movement type must be IN or OUT."
        print(message)
        return False, message

    if quantity <= 0:
        message = "Quantity must be greater than 0."
        print(message)
        return False, message

    conn = get_connection()

    try:
        product = conn.execute(
            "SELECT * FROM products WHERE name = ?",
            (product_name,)
        ).fetchone()

        if product is None:
            message = f"Product '{product_name}' not found."
            print(message)
            return False, message

        current_stock = product["stock"]

        if movement_type == "OUT" and quantity > current_stock:
            message = (
                f"Insufficient stock for '{product_name}'. "
                f"Current stock: {current_stock}, requested: {quantity}."
            )
            print(message)
            return False, message

        if movement_type == "IN":
            new_stock = current_stock + quantity
        else:
            new_stock = current_stock - quantity

        conn.execute(
            "UPDATE products SET stock = ? WHERE id = ?",
            (new_stock, product["id"])
        )

        conn.execute(
            """
            INSERT INTO movements
                (
                    product_id,
                    movement_type,
                    quantity,
                    note,
                    supplier,
                    po_number,
                    batch_lot,
                    expiry_date
                )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product["id"],
                movement_type,
                quantity,
                note,
                supplier,
                po_number,
                batch_lot,
                expiry_date
            )
        )

        conn.commit()

        message = (
            f"{movement_type} {quantity} {product['unit']} "
            f"recorded for '{product_name}'. "
            f"New stock: {new_stock}."
        )

        print(message)
        return True, message

    except Exception as e:
        conn.rollback()

        message = f"Error recording movement: {e}"
        print(message)

        return False, message

    finally:
        conn.close()

def movement_history(product_name=None, limit=20):
    """
    Devuelve el historial de movimientos, opcionalmente filtrado por producto.
    Usa un JOIN para mostrar el nombre del producto en lugar de solo el ID.
    """
    conn = get_connection()

    try:
        if product_name:
            query = """
                SELECT
                    m.id,
                    p.name,
                    m.movement_type,
                    m.quantity,
                    m.note,
                    m.timestamp
                FROM movements m
                JOIN products p ON m.product_id = p.id
                WHERE p.name = ?
                ORDER BY m.timestamp DESC, m.id DESC
                LIMIT ?
            """

            rows = conn.execute(
                query,
                (product_name, limit)
            ).fetchall()

        else:
            query = """
                SELECT
                    m.id,
                    p.name,
                    m.movement_type,
                    m.quantity,
                    m.note,
                    m.timestamp
                FROM movements m
                JOIN products p ON m.product_id = p.id
                ORDER BY m.timestamp DESC, m.id DESC
                LIMIT ?
            """

            rows = conn.execute(
                query,
                (limit,)
            ).fetchall()

        return rows

    finally:
        conn.close()