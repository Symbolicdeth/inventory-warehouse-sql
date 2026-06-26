"""
goods_in.py
Flujo dedicado a la recepción de mercadería ("Goods In"), pensado para
reemplazar el registro en papel. Permite:
- Recibir stock de un producto ya existente, con datos de remito/proveedor/lote.
- Dar de alta un producto nuevo "sobre la marcha" si llega algo que todavía
  no estaba registrado en el sistema, y recibir su stock inicial en el mismo paso.
"""

from products import get_product_by_name, add_product
from movements import record_movement


def receive_goods(product_name, quantity, supplier=None, po_number=None,
                   batch_lot=None, expiry_date=None, note="",
                   category="General", min_stock=5, unit="unidades"):
    """
    Registra una recepción de mercadería ("goods in").

    Si el producto no existe todavía, lo crea automáticamente con stock 0
    y categoría/mínimo/unidad por defecto (o los que se pasen), y después
    registra la entrada de stock normalmente.
    """
    product = get_product_by_name(product_name)

    if product is None:
        print(f"'{product_name}' no estaba registrado. Creándolo ahora...")
        add_product(product_name, category=category, stock=0,
                    min_stock=min_stock, unit=unit)

    record_movement(
        product_name=product_name,
        movement_type="IN",
        quantity=quantity,
        note=note,
        supplier=supplier,
        po_number=po_number,
        batch_lot=batch_lot,
        expiry_date=expiry_date,
    )


def goods_in_history(limit=20):
    """Devuelve el historial de recepciones (solo movimientos IN), con remito/proveedor/lote."""
    from database import get_connection
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.name, m.quantity, m.supplier, m.po_number, m.batch_lot,
               m.expiry_date, m.note, m.timestamp
        FROM movements m
        JOIN products p ON m.product_id = p.id
        WHERE m.movement_type = 'IN'
        ORDER BY m.timestamp DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows


def expiring_soon(days=7):
    """
    Productos recibidos con fecha de vencimiento dentro de los próximos N días.
    Útil para rotación de stock (FEFO: First Expired, First Out).
    """
    from database import get_connection
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.name, m.batch_lot, m.expiry_date, m.quantity, m.supplier
        FROM movements m
        JOIN products p ON m.product_id = p.id
        WHERE m.movement_type = 'IN'
          AND m.expiry_date IS NOT NULL
          AND m.expiry_date != ''
          AND date(m.expiry_date) <= date('now', ? || ' days')
        ORDER BY date(m.expiry_date) ASC
    """, (f"+{days}",)).fetchall()
    conn.close()
    return rows
