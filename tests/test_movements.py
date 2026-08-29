import movements
import products
from database import get_connection


def test_record_in_movement_updates_stock(test_db, monkeypatch):

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        products,
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

    movements.record_movement(
        "Salmon",
        "IN",
        5,
        note="Test reception"
    )

    product = products.get_product_by_name("Salmon")

    assert product["stock"] == 15

    connection = get_connection(test_db)

    movement = connection.execute(
        """
        SELECT *
        FROM movements
        WHERE product_id = ?
        """,
        (product["id"],)
    ).fetchone()

    connection.close()

    assert movement is not None
    assert movement["movement_type"] == "IN"
    assert movement["quantity"] == 5
    assert movement["note"] == "Test reception"

def test_record_out_movement_updates_stock(test_db, monkeypatch):

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        products,
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

    movements.record_movement(
        "Salmon",
        "OUT",
        4,
        note="Test dispatch"
    )

    product = products.get_product_by_name("Salmon")

    assert product["stock"] == 6

    connection = get_connection(test_db)

    movement = connection.execute(
        """
        SELECT *
        FROM movements
        WHERE product_id = ?
        """,
        (product["id"],)
    ).fetchone()

    connection.close()

    assert movement is not None
    assert movement["movement_type"] == "OUT"
    assert movement["quantity"] == 4
    assert movement["note"] == "Test dispatch"

def test_record_out_movement_cannot_exceed_stock(test_db, monkeypatch):

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        products,
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

    movements.record_movement(
        "Salmon",
        "OUT",
        15,
        note="Invalid dispatch"
    )

    product = products.get_product_by_name("Salmon")

    assert product["stock"] == 10

    connection = get_connection(test_db)

    movement_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM movements
        WHERE product_id = ?
        """,
        (product["id"],)
    ).fetchone()[0]

    connection.close()

    assert movement_count == 0

def test_record_movement_rejects_zero_quantity(test_db, monkeypatch):

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        products,
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

    movements.record_movement(
        "Salmon",
        "IN",
        0,
        note="Invalid quantity"
    )

    product = products.get_product_by_name("Salmon")

    assert product["stock"] == 10

    connection = get_connection(test_db)

    movement_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM movements
        WHERE product_id = ?
        """,
        (product["id"],)
    ).fetchone()[0]

    connection.close()

    assert movement_count == 0

def test_record_movement_rejects_negative_quantity(test_db, monkeypatch):

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        products,
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

    movements.record_movement(
        "Salmon",
        "IN",
        -5,
        note="Invalid negative quantity"
    )

    product = products.get_product_by_name("Salmon")

    assert product["stock"] == 10

    connection = get_connection(test_db)

    movement_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM movements
        WHERE product_id = ?
        """,
        (product["id"],)
    ).fetchone()[0]

    connection.close()

    assert movement_count == 0
def test_movement_history_returns_product_movements(test_db, monkeypatch):

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        products,
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

    movements.record_movement(
        "Salmon",
        "IN",
        5,
        note="First reception"
    )

    movements.record_movement(
        "Salmon",
        "OUT",
        3,
        note="Warehouse dispatch"
    )

    history = movements.movement_history("Salmon")

    assert len(history) == 2

    movement_types = {
        history[0]["movement_type"],
        history[1]["movement_type"]
    }

    assert movement_types == {"IN", "OUT"}

    quantities = {
        history[0]["quantity"],
        history[1]["quantity"]
    }

    assert quantities == {3, 5}

    assert all(
        row["name"] == "Salmon"
        for row in history
    )

def test_movement_history_respects_limit(test_db, monkeypatch):

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        products,
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

    movements.record_movement("Salmon", "IN", 1)
    movements.record_movement("Salmon", "IN", 2)
    movements.record_movement("Salmon", "IN", 3)
    movements.record_movement("Salmon", "IN", 4)
    movements.record_movement("Salmon", "IN", 5)

    history = movements.movement_history("Salmon", limit=3)

    assert len(history) == 3


def test_movement_history_returns_all_products(test_db, monkeypatch):

    monkeypatch.setattr(
        movements,
        "get_connection",
        lambda: get_connection(test_db)
    )

    monkeypatch.setattr(
        products,
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

    products.add_product(
        "Rice",
        "Dry Goods",
        20,
        5,
        "kg"
    )

    movements.record_movement(
        "Salmon",
        "IN",
        5
    )

    movements.record_movement(
        "Rice",
        "IN",
        10
    )

    history = movements.movement_history()

    assert len(history) == 2

    product_names = {
        row["name"]
        for row in history
    }

    assert product_names == {"Salmon", "Rice"}