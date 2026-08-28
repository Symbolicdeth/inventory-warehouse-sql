import products
from database import get_connection


def test_add_product(test_db, monkeypatch):

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

    connection = get_connection(test_db)

    product = connection.execute(
        "SELECT * FROM products WHERE name = ?",
        ("Salmon",)
    ).fetchone()

    connection.close()

    assert product is not None
    assert product["name"] == "Salmon"
    assert product["category"] == "Fish"
    assert product["stock"] == 10
    assert product["min_stock"] == 5
    assert product["unit"] == "kg"
def test_get_product_by_name(test_db, monkeypatch):

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

    product = products.get_product_by_name("Salmon")

    assert product is not None
    assert product["name"] == "Salmon"
    assert product["stock"] == 10

def test_get_product_that_does_not_exist(test_db, monkeypatch):

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    product = products.get_product_by_name("Producto inexistente")

    assert product is None
def test_update_min_stock(test_db, monkeypatch):

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

    products.update_min_stock("Salmon", 8)

    product = products.get_product_by_name("Salmon")

    assert product is not None
    assert product["name"] == "Salmon"
    assert product["stock"] == 10
    assert product["min_stock"] == 8
def test_delete_product(test_db, monkeypatch):

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

    products.delete_product("Salmon")

    product = products.get_product_by_name("Salmon")

    assert product is None

def test_list_products(test_db, monkeypatch):

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    products.add_product("Tuna", "Fish", 20, 5, "kg")
    products.add_product("Salmon", "Fish", 10, 5, "kg")
    products.add_product("Rice", "Dry Goods", 50, 10, "kg")

    product_list = products.list_products()

    assert len(product_list) == 3
    assert product_list[0]["name"] == "Rice"
    assert product_list[1]["name"] == "Salmon"
    assert product_list[2]["name"] == "Tuna"
def test_low_stock_alert(test_db, monkeypatch):

    monkeypatch.setattr(
        products,
        "get_connection",
        lambda: get_connection(test_db)
    )

    products.add_product("Salmon", "Fish", 3, 5, "kg")
    products.add_product("Tuna", "Fish", 10, 5, "kg")
    products.add_product("Rice", "Dry Goods", 5, 5, "kg")

    low_stock = products.low_stock_alert()

    assert len(low_stock) == 2
    assert low_stock[0]["name"] == "Salmon"
    assert low_stock[1]["name"] == "Rice"