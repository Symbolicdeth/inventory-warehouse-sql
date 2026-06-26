"""
main.py
Interfaz de línea de comandos para el sistema de inventario.
Ejecutar con: python main.py
"""

from database import setup_database
from products import (
    add_product,
    list_products,
    update_min_stock,
    delete_product,
    low_stock_alert,
)
from movements import record_movement, movement_history
from goods_in import receive_goods, goods_in_history, expiring_soon
from reports import (
    total_stock_value_by_category,
    most_moved_products,
    products_never_moved,
    average_stock,
)


def print_products(rows):
    if not rows:
        print("  (sin productos)")
        return
    print(f"{'ID':<4}{'Nombre':<20}{'Categoría':<15}{'Stock':<8}{'Mínimo':<8}{'Unidad':<10}")
    for r in rows:
        print(f"{r['id']:<4}{r['name']:<20}{r['category'] or '':<15}{r['stock']:<8}{r['min_stock']:<8}{r['unit']:<10}")


def print_movements(rows):
    if not rows:
        print("  (sin movimientos)")
        return
    print(f"{'Fecha':<22}{'Producto':<18}{'Tipo':<6}{'Cant.':<7}{'Nota':<20}")
    for r in rows:
        print(f"{r['timestamp']:<22}{r['name']:<18}{r['movement_type']:<6}{r['quantity']:<7}{r['note'] or '':<20}")


def menu():
    setup_database()

    options = """
========== INVENTARIO ==========
1. Agregar producto
2. Ver todos los productos
3. Registrar entrada de stock (IN)
4. Registrar salida de stock (OUT)
5. Ver historial de movimientos
6. Ver alertas de stock bajo
7. Cambiar stock mínimo de un producto
8. Eliminar producto
9. Reportes
10. Recepción de mercadería (Goods In)
11. Historial de recepciones (Goods In)
12. Productos próximos a vencer
0. Salir
=================================
"""

    while True:
        print(options)
        choice = input("Elegí una opción: ").strip()

        if choice == "1":
            name = input("Nombre del producto: ").strip()
            category = input("Categoría (Enter para 'General'): ").strip() or "General"
            stock = int(input("Stock inicial (Enter para 0): ").strip() or 0)
            min_stock = int(input("Stock mínimo (Enter para 5): ").strip() or 5)
            unit = input("Unidad (Enter para 'unidades'): ").strip() or "unidades"
            add_product(name, category, stock, min_stock, unit)

        elif choice == "2":
            print_products(list_products())

        elif choice == "3":
            name = input("Nombre del producto: ").strip()
            qty = int(input("Cantidad que entra: ").strip())
            note = input("Nota (opcional): ").strip()
            record_movement(name, "IN", qty, note)

        elif choice == "4":
            name = input("Nombre del producto: ").strip()
            qty = int(input("Cantidad que sale: ").strip())
            note = input("Nota (opcional): ").strip()
            record_movement(name, "OUT", qty, note)

        elif choice == "5":
            name = input("Nombre del producto (Enter para ver todos): ").strip()
            print_movements(movement_history(name or None))

        elif choice == "6":
            rows = low_stock_alert()
            if rows:
                print("⚠️  Productos con stock bajo:")
                print_products(rows)
            else:
                print("Todo el stock está por encima del mínimo.")

        elif choice == "7":
            name = input("Nombre del producto: ").strip()
            new_min = int(input("Nuevo stock mínimo: ").strip())
            update_min_stock(name, new_min)
            print("Actualizado.")

        elif choice == "8":
            name = input("Nombre del producto a eliminar: ").strip()
            confirm = input(f"¿Confirmás eliminar '{name}'? (s/n): ").strip().lower()
            if confirm == "s":
                delete_product(name)
                print("Eliminado.")

        elif choice == "9":
            print("\n--- Stock total por categoría ---")
            for r in total_stock_value_by_category():
                print(f"  {r['category']}: {r['total_units']} unidades en {r['num_products']} productos")

            print("\n--- Productos con más movimiento ---")
            for r in most_moved_products():
                print(f"  {r['name']}: {r['total_movements']} movimientos (IN: {r['total_in']}, OUT: {r['total_out']})")

            print("\n--- Productos sin movimientos registrados ---")
            print_products(products_never_moved())

            avg = average_stock()
            print(f"\nStock promedio entre todos los productos: {avg:.2f}" if avg else "\nNo hay datos suficientes.")

        elif choice == "10":
            print("\n--- Recepción de mercadería (Goods In) ---")
            name = input("Producto recibido: ").strip()
            qty = int(input("Cantidad recibida: ").strip())
            supplier = input("Proveedor (opcional): ").strip() or None
            po = input("Número de remito/PO (opcional): ").strip() or None
            batch = input("Lote (opcional): ").strip() or None
            expiry = input("Fecha de vencimiento YYYY-MM-DD (opcional): ").strip() or None
            note = input("Nota (opcional): ").strip()

            existing = None
            from products import get_product_by_name
            existing = get_product_by_name(name)
            category, min_stock, unit = "General", 5, "unidades"
            if existing is None:
                print(f"'{name}' es un producto nuevo, vamos a registrarlo.")
                category = input("Categoría (Enter para 'General'): ").strip() or "General"
                min_stock = int(input("Stock mínimo (Enter para 5): ").strip() or 5)
                unit = input("Unidad (Enter para 'unidades'): ").strip() or "unidades"

            receive_goods(name, qty, supplier=supplier, po_number=po,
                          batch_lot=batch, expiry_date=expiry, note=note,
                          category=category, min_stock=min_stock, unit=unit)

        elif choice == "11":
            rows = goods_in_history()
            if not rows:
                print("  (sin recepciones registradas)")
            else:
                print(f"{'Fecha':<20}{'Producto':<18}{'Cant.':<7}{'Proveedor':<15}{'Remito':<12}{'Lote':<10}{'Vence':<12}")
                for r in rows:
                    print(f"{r['timestamp']:<20}{r['name']:<18}{r['quantity']:<7}"
                          f"{r['supplier'] or '':<15}{r['po_number'] or '':<12}"
                          f"{r['batch_lot'] or '':<10}{r['expiry_date'] or '':<12}")

        elif choice == "12":
            days = int(input("Mostrar vencimientos en los próximos N días (Enter para 7): ").strip() or 7)
            rows = expiring_soon(days)
            if not rows:
                print(f"  No hay productos venciendo en los próximos {days} días.")
            else:
                print(f"⚠️  Productos próximos a vencer (próximos {days} días):")
                for r in rows:
                    print(f"  {r['name']} | Lote: {r['batch_lot'] or '-'} | Vence: {r['expiry_date']} | Cantidad: {r['quantity']}")

        elif choice == "0":
            print("¡Hasta la próxima!")
            break

        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu()
