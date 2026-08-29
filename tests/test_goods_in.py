import goods_in
import products
import movements

from database import get_connection


def test_receive_goods_existing_product(test_db, monkeypatch):

    monkeypatch.setattr(
        goods_in,
        "get_product_by_name",
        lambda name: products.get_product_by_name(name)
    )

    monkeypatch.setattr(
        goods_in,
        "record_movement",
        lambda **kwargs: movements.record_movement(**kwargs)
    )

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    products.add_product(
        "Salmon",
        "Fish",
        10,
        5,
        "kg"
    )

    goods_in.receive_goods(
        product_name="Salmon",
        quantity=5,
        supplier="Fresh Fish Ltd",
        po_number="PO-1001",
        batch_lot="LOT-001",
        expiry_date="2026-09-15",
        note="First reception"
    )

    product = products.get_product_by_name("Salmon")

    assert product["stock"] == 15

def test_receive_goods_creates_new_product(test_db, monkeypatch):

    monkeypatch.setattr(
        goods_in,
        "get_product_by_name",
        lambda name: products.get_product_by_name(name)
    )

    monkeypatch.setattr(
        goods_in,
        "add_product",
        lambda name, **kwargs: products.add_product(name, **kwargs)
    )

    monkeypatch.setattr(
        goods_in,
        "record_movement",
        lambda **kwargs: movements.record_movement(**kwargs)
    )

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    goods_in.receive_goods(
        product_name="Tuna",
        quantity=20,
        category="Fish",
        min_stock=5,
        unit="kg"
    )

    product = products.get_product_by_name("Tuna")

    assert product is not None
    assert product["category"] == "Fish"
    assert product["stock"] == 20
    assert product["min_stock"] == 5
    assert product["unit"] == "kg"
def test_receive_goods_saves_receiving_details(test_db, monkeypatch):

    monkeypatch.setattr(
        goods_in,
        "get_product_by_name",
        lambda name: products.get_product_by_name(name)
    )

    monkeypatch.setattr(
        goods_in,
        "record_movement",
        lambda **kwargs: movements.record_movement(**kwargs)
    )

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    products.add_product(
        "Salmon",
        "Fish",
        10,
        5,
        "kg"
    )

    goods_in.receive_goods(
        product_name="Salmon",
        quantity=8,
        supplier="Atlantic Seafood Ltd",
        po_number="PO-2026-001",
        batch_lot="SAL-0826-A",
        expiry_date="2026-09-20",
        note="Morning delivery"
    )

    conn = get_connection(test_db)

    movement = conn.execute(
        """
        SELECT *
        FROM movements
        WHERE product_id = (
            SELECT id FROM products WHERE name = ?
        )
        ORDER BY id DESC
        LIMIT 1
        """,
        ("Salmon",)
    ).fetchone()

    conn.close()

    assert movement["movement_type"] == "IN"
    assert movement["quantity"] == 8
    assert movement["supplier"] == "Atlantic Seafood Ltd"
    assert movement["po_number"] == "PO-2026-001"
    assert movement["batch_lot"] == "SAL-0826-A"
    assert movement["expiry_date"] == "2026-09-20"
    assert movement["note"] == "Morning delivery"

def test_goods_in_history_returns_receiving_records(test_db, monkeypatch):

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        "database.get_connection",
        lambda: get_connection(test_db)
    )

    products.add_product(
        "Salmon",
        "Fish",
        10,
        5,
        "kg"
    )

    movements.record_movement(
        "Salmon",
        "IN",
        8,
        supplier="Atlantic Seafood Ltd",
        po_number="PO-001",
        batch_lot="SAL-001",
        expiry_date="2026-09-20",
        note="Morning delivery"
    )

    history = goods_in.goods_in_history()

    assert len(history) == 1

    row = history[0]

    assert row["name"] == "Salmon"
    assert row["quantity"] == 8
    assert row["supplier"] == "Atlantic Seafood Ltd"
    assert row["po_number"] == "PO-001"
    assert row["batch_lot"] == "SAL-001"
    assert row["expiry_date"] == "2026-09-20"
    assert row["note"] == "Morning delivery"

def test_goods_in_history_ignores_out_movements(test_db, monkeypatch):

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        "database.get_connection",
        lambda: get_connection(test_db)
    )

    products.add_product(
        "Salmon",
        "Fish",
        20,
        5,
        "kg"
    )

    movements.record_movement(
        "Salmon",
        "IN",
        10
    )

    movements.record_movement(
        "Salmon",
        "OUT",
        3
    )

    movements.record_movement(
        "Salmon",
        "IN",
        5
    )

    history = goods_in.goods_in_history()

    assert len(history) == 2

    quantities = {
        row["quantity"]
        for row in history
    }

    assert quantities == {10, 5}

def test_goods_in_history_respects_limit(test_db, monkeypatch):

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        "database.get_connection",
        lambda: get_connection(test_db)
    )

    products.add_product(
        "Salmon",
        "Fish",
        0,
        5,
        "kg"
    )

    movements.record_movement("Salmon", "IN", 1)
    movements.record_movement("Salmon", "IN", 2)
    movements.record_movement("Salmon", "IN", 3)
    movements.record_movement("Salmon", "IN", 4)
    movements.record_movement("Salmon", "IN", 5)

    history = goods_in.goods_in_history(limit=2)

    assert len(history) == 2

from datetime import date, timedelta

def test_expiring_soon_returns_products_within_range(test_db, monkeypatch):

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        "database.get_connection",
        lambda: get_connection(test_db)
    )

    products.add_product(
        "Salmon",
        "Fish",
        0,
        5,
        "kg"
    )

    products.add_product(
        "Chicken",
        "Meat",
        0,
        5,
        "kg"
    )

    products.add_product(
        "Rice",
        "Dry Goods",
        0,
        5,
        "kg"
    )

    today = date.today()

    soon_date = (today + timedelta(days=3)).isoformat()
    later_date = (today + timedelta(days=20)).isoformat()

    movements.record_movement(
        "Salmon",
        "IN",
        10,
        batch_lot="SAL-001",
        expiry_date=soon_date
    )

    movements.record_movement(
        "Chicken",
        "IN",
        10,
        batch_lot="CHK-001",
        expiry_date=later_date
    )

    movements.record_movement(
        "Rice",
        "IN",
        10,
        batch_lot="RIC-001"
    )

    expiring = goods_in.expiring_soon(days=7)

    assert len(expiring) == 1

    row = expiring[0]

    assert row["name"] == "Salmon"
    assert row["batch_lot"] == "SAL-001"
    assert row["expiry_date"] == soon_date
    assert row["quantity"] == 10

def test_expiring_soon_includes_already_expired_products(test_db, monkeypatch):

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        "database.get_connection",
        lambda: get_connection(test_db)
    )

    products.add_product(
        "Salmon",
        "Fish",
        0,
        5,
        "kg"
    )

    expired_date = (
        date.today() - timedelta(days=2)
    ).isoformat()

    movements.record_movement(
        "Salmon",
        "IN",
        10,
        batch_lot="SAL-EXPIRED",
        expiry_date=expired_date
    )

    expiring = goods_in.expiring_soon(days=7)

    assert len(expiring) == 1

    row = expiring[0]

    assert row["name"] == "Salmon"
    assert row["batch_lot"] == "SAL-EXPIRED"
    assert row["expiry_date"] == expired_date