# Sistema de Inventario (Python + SQLite)

Proyecto de portfolio inspirado en operaciones reales de warehouse (control de
inventario, entradas/salidas de stock, alertas de stock bajo). Construido para
practicar Python + SQL aplicados a un caso de uso real.

## Funcionalidades

- Alta, baja y consulta de productos
- Registro de movimientos de stock (entradas / salidas) con transacciones
  seguras (si algo falla, no se modifica el stock)
- **Recepción de mercadería ("Goods In")**: reemplaza el registro en papel,
  guardando proveedor, número de remito/PO, lote y fecha de vencimiento.
  Si el producto recibido no existe todavía, se crea automáticamente.
- **Alertas de productos próximos a vencer** (rotación FEFO: First Expired,
  First Out), basado en las fechas de vencimiento registradas en cada recepción
- Alertas automáticas de stock bajo (cuando el stock llega al mínimo definido)
- Historial de movimientos por producto o general, e historial específico de
  recepciones (goods in)
- Reportes:
  - Stock total agrupado por categoría
  - Productos con más movimientos (entradas vs salidas)
  - Productos que nunca tuvieron movimiento
  - Stock promedio general

## Stack

- Python 3 (sin dependencias externas, solo librería estándar)
- SQLite (vía `sqlite3`, incluido en Python)

## Cómo correrlo

**Versión de línea de comandos (menú de texto):**
```bash
python main.py
```

**Versión con interfaz gráfica (ventana de escritorio, Tkinter):**
```bash
python app.py
```

Ambas comparten la misma lógica de negocio (`database.py`, `products.py`,
`movements.py`, `goods_in.py`, `reports.py`) — `app.py` es solo una capa
visual sobre el mismo sistema.

Esto crea automáticamente el archivo `inventory.db` la primera vez que se
ejecuta, junto con las tablas necesarias.

## Estructura del proyecto

```
inventory_project/
├── database.py    # Conexión y creación de tablas (schema)
├── products.py     # CRUD de productos
├── movements.py     # Registro de movimientos de stock + historial
├── goods_in.py       # Flujo de recepción de mercadería (proveedor, remito, lote, vencimiento)
├── reports.py       # Reportes agregados (GROUP BY, JOIN, subqueries)
├── main.py           # Interfaz de línea de comandos (menú)
├── app.py             # Interfaz gráfica de escritorio (Tkinter)
├── .gitignore
└── README.md
```

## Conceptos de SQL practicados

- `CREATE TABLE` con `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, `DEFAULT`
- `INSERT`, `SELECT`, `UPDATE`, `DELETE`
- `JOIN` entre tablas relacionadas
- `GROUP BY` + funciones agregadas (`SUM`, `COUNT`, `AVG`)
- Subqueries (`NOT IN (SELECT ...)`)
- Transacciones (`commit` / `rollback`) para mantener consistencia de datos
- Parámetros (`?`) para prevenir SQL injection

## Posibles mejoras futuras

- Exportar reportes a CSV o Excel
- Migrar a PostgreSQL para un entorno más cercano a producción
- Agregar una interfaz web simple (Flask) sobre la misma lógica
- Agregar tests automatizados con `pytest`
