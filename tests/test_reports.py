import reports
import products

from database import get_connection


def test_total_stock_value_by_category(test_db, monkeypatch):

    monkeypatch.setattr(
        reports,
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
        "Tuna",
        "Fish",
        5,
        5,
        "kg"
    )

    products.add_product(
        "Chicken",
        "Meat",
        20,
        5,
        "kg"
    )

    report = reports.total_stock_value_by_category()

    assert len(report) == 2

    assert report[0]["category"] == "Meat"
    assert report[0]["total_units"] == 20
    assert report[0]["num_products"] == 1

    assert report[1]["category"] == "Fish"
    assert report[1]["total_units"] == 15
    assert report[1]["num_products"] == 2

import movements


def test_most_moved_products(test_db, monkeypatch):

    monkeypatch.setattr(
        reports,
        "get_connection",
        lambda: get_connection(test_db)
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
        0,
        5,
        "kg"
    )

    products.add_product(
        "Tuna",
        "Fish",
        0,
        5,
        "kg"
    )

    movements.record_movement("Salmon", "IN", 10)
    movements.record_movement("Salmon", "OUT", 3)
    movements.record_movement("Salmon", "IN", 5)

    movements.record_movement("Tuna", "IN", 8)

    report = reports.most_moved_products()

    assert len(report) == 2

    assert report[0]["name"] == "Salmon"
    assert report[0]["total_movements"] == 3
    assert report[0]["total_in"] == 15
    assert report[0]["total_out"] == 3

def test_products_never_moved(test_db, monkeypatch):

    monkeypatch.setattr(
        reports,
        "get_connection",
        lambda: get_connection(test_db)
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

    products.add_product(
        "Tuna",
        "Fish",
        5,
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
        "Tuna",
        "OUT",
        2
    )

    report = reports.products_never_moved()

    assert len(report) == 1
    assert report[0]["name"] == "Rice"

def test_low_stock_products(test_db, monkeypatch):

    monkeypatch.setattr(
        reports,
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
        2,
        5,
        "kg"
    )

    products.add_product(
        "Tuna",
        "Fish",
        5,
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

    report = reports.low_stock_products()

    assert len(report) == 2
    assert report[0]["name"] == "Salmon"
    assert report[0]["stock"] == 2
    assert report[1]["name"] == "Tuna"
    assert report[1]["stock"] == 5

def test_movement_summary(test_db, monkeypatch):

    monkeypatch.setattr(
        reports,
        "get_connection",
        lambda: get_connection(test_db)
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
        "OUT",
        2
    )

    summary = reports.movement_summary()

    assert summary["total_movements"] == 3
    assert summary["in_movements"] == 1
    assert summary["out_movements"] == 2
    assert summary["total_in"] == 10
    assert summary["total_out"] == 5

def test_movement_totals_by_product(test_db, monkeypatch):

    monkeypatch.setattr(
        reports,
        "get_connection",
        lambda: get_connection(test_db)
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
        10
    )

    movements.record_movement(
        "Salmon",
        "OUT",
        4
    )

    movements.record_movement(
        "Rice",
        "OUT",
        5
    )

    report = reports.movement_totals_by_product()

    assert len(report) == 2

    assert report[0]["name"] == "Salmon"
    assert report[0]["total_in"] == 10
    assert report[0]["total_out"] == 4
    assert report[0]["total_movements"] == 2

    assert report[1]["name"] == "Rice"
    assert report[1]["total_in"] == 0
    assert report[1]["total_out"] == 5
    assert report[1]["total_movements"] == 1