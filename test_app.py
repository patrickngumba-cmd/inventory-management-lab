import pytest
from unittest.mock import patch, MagicMock
from app import app, inventory
import cli

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# 1. Test GET all inventory items
def test_get_all_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1

# 2. Test GET single item by ID
def test_get_single_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1

def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404

# 3. Test POST new item with mocked OpenFoodFacts response
@patch("app.requests.get")
def test_create_item_with_mock_api(mock_get, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Dormans Coffee 250g",
            "brands": "Dormans",
            "ingredients_text": "100% Roasted Arabica Coffee"
        }
    }
    mock_get.return_value = mock_response

    new_item = {
        "barcode": "6161100099999",
        "price": 450.0,
        "stock": 20
    }
    response = client.post("/inventory", json=new_item)
    assert response.status_code == 201
    data = response.get_json()
    assert data["product_name"] == "Dormans Coffee 250g"
    assert data["brands"] == "Dormans"
    assert data["price"] == 450.0

# 4. Test PATCH update item price and stock
def test_update_item(client):
    update_data = {"price": 230.0, "stock": 45}
    response = client.patch("/inventory/1", json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 230.0
    assert data["stock"] == 45

# 5. Test DELETE item
def test_delete_item(client):
    response = client.delete("/inventory/3")
    assert response.status_code == 200
    check = client.get("/inventory/3")
    assert check.status_code == 404

# 6. Test CLI view function using mock
@patch("cli.requests.get")
def test_cli_view_items(mock_get, capsys):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": 1,
            "barcode": "6161100160024",
            "product_name": "Jogoo Maize Meal",
            "brands": "Unga Ltd",
            "price": 210.0,
            "stock": 50
        }
    ]
    mock_get.return_value = mock_response

    cli.view_all_items()
    captured = capsys.readouterr()
    assert "Jogoo Maize Meal" in captured.out
    assert "KES 210.00" in captured.out

# 7. Test external API search helper route
@patch("app.requests.get")
def test_search_external_api_route(mock_get, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "KCC Butter 250g",
            "brands": "New KCC",
            "ingredients_text": "Pasteurized cream, salt"
        }
    }
    mock_get.return_value = mock_response

    response = client.get("/inventory/search?barcode=6161101650099")
    assert response.status_code == 200
    data = response.get_json()
    assert data["product_name"] == "KCC Butter 250g"