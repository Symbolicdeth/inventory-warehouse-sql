import sqlite3

import pytest


@pytest.fixture
def test_db(tmp_path):
    db_path = tmp_path / "test_inventory.db"

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    connection.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT,
            stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
            min_stock INTEGER NOT NULL DEFAULT 5,
            unit TEXT DEFAULT 'unidades',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    connection.execute("""
        CREATE TABLE movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT')),
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            note TEXT,
            supplier TEXT,
            po_number TEXT,
            batch_lot TEXT,
            expiry_date TEXT,
            timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    connection.commit()
    connection.close()

    return db_path