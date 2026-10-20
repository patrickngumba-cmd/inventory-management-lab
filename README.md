# Supermarket Inventory Management System

A Flask REST API and interactive Command-Line Interface (CLI) for managing retail supermarket inventory. The system supports full CRUD operations in Kenyan Shillings (KES) and integrates with the OpenFoodFacts API to look up product details by barcode or product name.

## Installation and Setup Instructions

1. Clone the repository and navigate to the project folder:
   ```bash
   git clone <your-github-repo-url>
   cd inventory-management-lab
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install the required packages:
   ```bash
   pip install flask requests pytest
   ```

## Running the Application

1. Start the Flask server in your first terminal window:
   ```bash
   python app.py
   ```
   The API will run at `http://127.0.0.1:5000`.

2. Open a second terminal window, activate the virtual environment, and run the CLI:
   ```bash
   .\venv\Scripts\Activate.ps1
   python cli.py
   ```

## API Endpoint Details

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/inventory` | Fetch all items in the inventory|
| `GET` | `/inventory/<id>` | Fetch a single item by its ID |
| `POST` | `/inventory` | Add a new item (fetches product info from OpenFoodFacts) |
| `PATCH` | `/inventory/<id>` | Update an item's price, stock, name, or brand|
| `DELETE` | `/inventory/<id>` | Remove an item from the inventory by ID |
| `GET` | `/inventory/search` | Query OpenFoodFacts directly using `?barcode=` or `?name=`|

## Example Usage of CLI Commands

When you run `python cli.py`, an interactive menu appears:

```text
=== Supermarket Inventory CLI ===
1. View Inventory
2. Add New Item
3. Update Price or Stock
4. Delete Item
5. Search Item on OpenFoodFacts
6. Exit
Choose an option (1-6): 1

--- Supermarket Inventory ---
ID: 1 | Jogoo Fortified Maize Meal 2kg (Unga Limited) | Barcode: 6161100160024 | Price: KES 210.00 | Stock: 50
ID: 2 | KCC Gold Crown Fresh Milk 500ml (New KCC) | Barcode: 6161101650012 | Price: KES 65.00 | Stock: 80
ID: 3 | Ketepa Pride Tea Bags 100s (Ketepa) | Barcode: 6161100040012 | Price: KES 280.00 | Stock: 35
```

**Adding an item (Option 2):**
```text
Choose an option (1-6): 2

--- Add Product ---
Enter barcode (or press Enter to skip): 3017620422003
Enter product name (or press Enter to fetch from barcode): 
Enter price in KES (e.g. 150): 450
Enter stock quantity: 15
Added: Nutella (ID: 4)
```

**Updating stock or price (Option 3):**
```text
Choose an option (1-6): 3

--- Update Product ---
Enter item ID to update: 1
Enter new price in KES (press Enter to skip): 220
Enter new stock count (press Enter to skip): 45
Updated ID 1 -> Price: KES 220.00, Stock: 45
```

## Running Unit Tests

To run the automated unit tests for the API routes, external API mocking, and CLI functions[cite: 18]:
```bash
pytest
```