import requests

API_URL = "http://127.0.0.1:5000/inventory"

def view_all_items():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            items = response.json()
            if len(items) == 0:
                print("\nInventory is empty.")
                return
            print("\n--- Supermarket Inventory ---")
            for item in items:
                print(f"ID: {item['id']} | {item['product_name']} ({item['brands']}) | Barcode: {item['barcode']} | Price: KES {item['price']:.2f} | Stock: {item['stock']}")
        else:
            print("Failed to load inventory.")
    except requests.ConnectionError:
        print("\nCannot connect to server. Please make sure app.py is running.")

def add_new_item():
    print("\n--- Add Product ---")
    barcode = input("Enter barcode (or press Enter to skip): ").strip()
    name = input("Enter product name (or press Enter to fetch from barcode): ").strip()

    if barcode == "" and name == "":
        print("You must enter either a barcode or a product name.")
        return

    try:
        price = float(input("Enter price in KES (e.g. 150): ").strip())
        stock = int(input("Enter stock quantity: ").strip())
    except ValueError:
        print("Invalid number entered for price or stock.")
        return

    new_data = {
        "barcode": barcode if barcode != "" else None,
        "product_name": name if name != "" else None,
        "price": price,
        "stock": stock
    }

    try:
        response = requests.post(API_URL, json=new_data)
        if response.status_code == 201:
            created = response.json()
            print(f"Added: {created['product_name']} (ID: {created['id']})")
        else:
            print("Error adding item:", response.text)
    except requests.ConnectionError:
        print("\nCannot connect to server.")

def update_existing_item():
    print("\n--- Update Product ---")
    try:
        item_id = int(input("Enter item ID to update: ").strip())
    except ValueError:
        print("ID must be a number.")
        return

    price_str = input("Enter new price in KES (press Enter to skip): ").strip()
    stock_str = input("Enter new stock count (press Enter to skip): ").strip()

    updates = {}
    try:
        if price_str != "":
            updates["price"] = float(price_str)
        if stock_str != "":
            updates["stock"] = int(stock_str)
    except ValueError:
        print("Invalid number entered.")
        return

    if len(updates) == 0:
        print("Nothing to update.")
        return

    try:
        response = requests.patch(f"{API_URL}/{item_id}", json=updates)
        if response.status_code == 200:
            updated = response.json()
            print(f"Updated ID {item_id} -> Price: KES {updated['price']:.2f}, Stock: {updated['stock']}")
        elif response.status_code == 404:
            print("Item ID not found.")
        else:
            print("Update failed.")
    except requests.ConnectionError:
        print("\nCannot connect to server.")

def remove_item():
    print("\n--- Delete Product ---")
    try:
        item_id = int(input("Enter item ID to delete: ").strip())
    except ValueError:
        print("ID must be a number.")
        return

    try:
        response = requests.delete(f"{API_URL}/{item_id}")
        if response.status_code == 200:
            print(f"Item {item_id} removed from inventory.")
        elif response.status_code == 404:
            print("Item ID not found.")
        else:
            print("Failed to delete item.")
    except requests.ConnectionError:
        print("\nCannot connect to server.")

def search_openfoodfacts():
    print("\n--- Search OpenFoodFacts ---")
    barcode = input("Enter barcode (or press Enter to search by name): ").strip()
    name = ""
    if barcode == "":
        name = input("Enter product name: ").strip()

    if barcode == "" and name == "":
        print("Please enter a barcode or name to search.")
        return

    params = {}
    if barcode != "":
        params["barcode"] = barcode
    if name != "":
        params["name"] = name

    try:
        response = requests.get(f"{API_URL}/search", params=params)
        if response.status_code == 200:
            info = response.json()
            print("\nProduct Found:")
            print("Name:       ", info.get("product_name"))
            print("Brand:      ", info.get("brands"))
            print("Barcode:    ", info.get("barcode"))
            print("Ingredients:", info.get("ingredients_text"))

            save_choice = input("\nAdd this item to inventory? (y/n): ").strip().lower()
            if save_choice == "y":
                try:
                    price = float(input("Enter price in KES: ").strip())
                    stock = int(input("Enter stock quantity: ").strip())
                    new_item = {
                        "barcode": info.get("barcode"),
                        "product_name": info.get("product_name"),
                        "brands": info.get("brands"),
                        "ingredients_text": info.get("ingredients_text"),
                        "price": price,
                        "stock": stock
                    }
                    post_resp = requests.post(API_URL, json=new_item)
                    if post_resp.status_code == 201:
                        added = post_resp.json()
                        print(f"Successfully added '{added['product_name']}' to inventory with ID {added['id']}!")
                except ValueError:
                    print("Invalid number entered for price or stock.")
        else:
            print("Product not found on OpenFoodFacts.")
    except requests.ConnectionError:
        print("\nCannot connect to server.")

def start_cli():
    while True:
        print("\n=== Supermarket Inventory CLI ===")
        print("1. View Inventory")
        print("2. Add New Item")
        print("3. Update Price or Stock")
        print("4. Delete Item")
        print("5. Search Item on OpenFoodFacts")
        print("6. Exit")

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            view_all_items()
        elif choice == "2":
            add_new_item()
        elif choice == "3":
            update_existing_item()
        elif choice == "4":
            remove_item()
        elif choice == "5":
            search_openfoodfacts()
        elif choice == "6":
            print("Closing CLI.")
            break
        else:
            print("Invalid option, please pick 1 to 6.")

if __name__ == "__main__":
    start_cli()