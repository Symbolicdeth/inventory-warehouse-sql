"""
database.py
Maneja la conexión a SQLite y la creación de las tablas.

Conceptos SQL usados aquí:
- CREATE TABLE
- PRIMARY KEY / FOREIGN KEY
- Restricciones (NOT NULL, DEFAULT, CHECK)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "inventory.db"


def get_connection():
    """Abre una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acceder a columnas por nombre
    conn.execute("PRAGMA foreign_keys = ON;")  # SQLite no las activa por defecto
    return conn


def setup_database():
    """Crea las tablas si no existen todavía."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT,
            stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
            min_stock INTEGER NOT NULL DEFAULT 5,
            unit TEXT DEFAULT 'unidades',
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT')),
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            note TEXT,
            timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
    """)

    conn.commit()
    conn.close()
    print(f"Base de datos lista en: {DB_PATH}")


if __name__ == "__main__":
    setup_database()
