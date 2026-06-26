"""
movements.py
Registra entradas/salidas de stock y mantiene el historial.

Conceptos SQL usados aquí:
- Transacciones (commit/rollback)
- JOIN entre movements y products
- ORDER BY, LIMIT
"""

from database import get_connection


def record_movement(product_name, movement_type, quantity, note="",
                     supplier=None, po_number=None, batch_lot=None, expiry_date=None):
    """
    Registra un movimiento de stock (IN o OUT) y actualiza el stock del producto.
    Usa una transacción: si algo falla, no se aplica ningún cambio.

    Los campos supplier, po_number, batch_lot y expiry_date son opcionales y
    pensados principalmente para movimientos IN (recepción de mercadería /
    "goods in"), replicando los datos que hoy se anotan en papel.
    """
    movement_type = movement_type.upper()
    if movement_type not in ("IN", "OUT"):
        print("Tipo de movimiento inválido. Usá 'IN' o 'OUT'.")
        return

    conn = get_connection()
    try:
        product = conn.execute(
            "SELECT * FROM products WHERE name = ?", (product_name,)
        ).fetchone()

        if product is None:
            print(f"Producto '{product_name}' no encontrado.")
            return

        current_stock = product["stock"]

        if movement_type == "OUT" and quantity > current_stock:
            print(
                f"No hay suficiente stock de '{product_name}'. "
                f"Stock actual: {current_stock}, solicitado: {quantity}."
            )
            return

        new_stock = (
            current_stock + quantity if movement_type == "IN" else current_stock - quantity
        )

        conn.execute(
            "UPDATE products SET stock = ? WHERE id = ?",
            (new_stock, product["id"]),
        )
        conn.execute(
            """
            INSERT INTO movements
                (product_id, movement_type, quantity, note, supplier, po_number, batch_lot, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (product["id"], movement_type, quantity, note, supplier, po_number, batch_lot, expiry_date),
        )

        conn.commit()
        print(
            f"Movimiento registrado: {movement_type} {quantity} {product['unit']} "
            f"de '{product_name}'. Nuevo stock: {new_stock}."
        )

    except Exception as e:
        conn.rollback()
        print(f"Error al registrar movimiento, se revirtió el cambio: {e}")
    finally:
        conn.close()


def movement_history(product_name=None, limit=20):
    """
    Devuelve el historial de movimientos, opcionalmente filtrado por producto.
    Usa un JOIN para mostrar el nombre del producto en lugar de solo el ID.
    """
    conn = get_connection()
    if product_name:
        query = """
            SELECT m.id, p.name, m.movement_type, m.quantity, m.note, m.timestamp
            FROM movements m
            JOIN products p ON m.product_id = p.id
            WHERE p.name = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        """
        rows = conn.execute(query, (product_name, limit)).fetchall()
    else:
        query = """
            SELECT m.id, p.name, m.movement_type, m.quantity, m.note, m.timestamp
            FROM movements m
            JOIN products p ON m.product_id = p.id
            ORDER BY m.timestamp DESC
            LIMIT ?
        """
        rows = conn.execute(query, (limit,)).fetchall()
    conn.close()
    return rows
