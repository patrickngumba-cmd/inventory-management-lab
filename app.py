from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Mock database using a list of dictionaries
inventory = [
    {
        "id": 1,
        "barcode": "6161100160024",
        "product_name": "Jogoo Fortified Maize Meal 2kg",
        "brands": "Unga Limited",
        "ingredients_text": "Whole white maize, vitamins and mineral premix",
        "price": 210.0,
        "stock": 50
    },
    {
        "id": 2,
        "barcode": "6161101650012",
        "product_name": "KCC Gold Crown Fresh Milk 500ml",
        "brands": "New KCC",
        "ingredients_text": "Pasteurized homogenized cow milk",
        "price": 65.0,
        "stock": 80
    },
    {
        "id": 3,
        "barcode": "6161100040012",
        "product_name": "Ketepa Pride Tea Bags 100s",
        "brands": "Ketepa",
        "ingredients_text": "100% pure Kenyan black tea leaves",
        "price": 280.0,
        "stock": 35
    }
]

# Find an item in the inventory list by id
def find_item_by_id(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None

# Generate a new id by finding the highest existing id
def get_next_id():
    if len(inventory) == 0:
        return 1
    highest = 0
    for item in inventory:
        if item["id"] > highest:
            highest = item["id"]
    return highest + 1

# Fetch product info from OpenFoodFacts API
def get_openfoodfacts_data(barcode=None, name=None):
    try:
        if barcode:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1:
                    product = data.get("product", {})
                    return {
                        "barcode": barcode,
                        "product_name": product.get("product_name", "Unknown Item"),
                        "brands": product.get("brands", "Unknown Brand"),
                        "ingredients_text": product.get("ingredients_text", "Not listed")
                    }
        elif name:
            url = "https://world.openfoodfacts.org/cgi/search.pl"
            params = {
                "search_terms": name,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 1
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                if len(products) > 0:
                    product = products[0]
                    return {
                        "barcode": product.get("code", "N/A"),
                        "product_name": product.get("product_name", name),
                        "brands": product.get("brands", "Unknown Brand"),
                        "ingredients_text": product.get("ingredients_text", "Not listed")
                    }
    except Exception:
        return None
    return None

# GET all items
@app.route("/inventory", methods=["GET"])
def get_all_inventory():
    return jsonify(inventory), 200

# GET single item by ID
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_single_item(item_id):
    item = find_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200

# POST new item
@app.route("/inventory", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    barcode = data.get("barcode")
    product_name = data.get("product_name")

    api_details = {}
    if barcode or product_name:
        fetched = get_openfoodfacts_data(barcode=barcode, name=product_name)
        if fetched is not None:
            api_details = fetched

    new_item = {
        "id": get_next_id(),
        "barcode": barcode or api_details.get("barcode", "N/A"),
        "product_name": product_name or api_details.get("product_name", "Unnamed Item"),
        "brands": data.get("brands") or api_details.get("brands", "Unknown Brand"),
        "ingredients_text": data.get("ingredients_text") or api_details.get("ingredients_text", "N/A"),
        "price": float(data.get("price", 0.0)),
        "stock": int(data.get("stock", 0))
    }

    inventory.append(new_item)
    return jsonify(new_item), 201

# PATCH update item price or stock
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    if "product_name" in data:
        item["product_name"] = data["product_name"]
    if "brands" in data:
        item["brands"] = data["brands"]
    if "price" in data:
        item["price"] = float(data["price"])
    if "stock" in data:
        item["stock"] = int(data["stock"])

    return jsonify(item), 200

# DELETE item
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": "Item deleted"}), 200

# Search external API endpoint for the CLI
@app.route("/inventory/search", methods=["GET"])
def search_external_api():
    barcode = request.args.get("barcode")
    name = request.args.get("name")
    result = get_openfoodfacts_data(barcode=barcode, name=name)
    if result is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5000)