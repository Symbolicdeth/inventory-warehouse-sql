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

        elif choice == "0":
            print("¡Hasta la próxima!")
            break

        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu()
