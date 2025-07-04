from database import connect_db, setup_database

# Run DB setup
setup_database()

def add_product():
    print("\nAdd New Product")
    name = input("Enter product name: ")
    desc = input("Enter description: ")
    try:
        qty = int(input("Enter quantity: "))
        price = float(input("Enter price: "))
    except ValueError:
        print("Invalid input. Quantity and price must be numbers.")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Products (name, description, quantity, price)
        VALUES (?, ?, ?, ?)
    """, (name, desc, qty, price))
    conn.commit()
    conn.close()
    print("Product added successfully!")


def view_products():
    print("\nInventory List:")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("Inventory is empty.")
    else:
        print(f"{'ID':<5} {'Name':<20} {'Qty':<10} {'Price':<10} {'Description'}")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[3]:<10} Rs.{row[4]:<10} {row[2]}")


def update_stock():
    print("\nUpdate Product Stock")
    product_id = input("Enter Product ID to update stock: ")
    try:
        quantity = int(input("Enter quantity to add/remove (use negative for removing): "))
    except ValueError:
        print("Invalid quantity.")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM Products WHERE product_id = ?", (product_id,))
    result = cursor.fetchone()

    if not result:
        print("Product not found.")
        conn.close()
        return

    new_quantity = result[0] + quantity
    if new_quantity < 0:
        print("Not enough stock to remove.")
        conn.close()
        return

    cursor.execute("UPDATE Products SET quantity = ? WHERE product_id = ?", (new_quantity, product_id))
    transaction_type = 'add' if quantity > 0 else 'remove'
    cursor.execute("""
        INSERT INTO Transactions (product_id, quantity_changed, transaction_type)
        VALUES (?, ?, ?)
    """, (product_id, quantity, transaction_type))

    conn.commit()
    conn.close()
    print("Stock updated successfully!")


def view_transactions():
    print("\nTransaction History:")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.transaction_id, P.name, T.quantity_changed, T.transaction_type, T.date
        FROM Transactions T
        JOIN Products P ON T.product_id = P.product_id
        ORDER BY T.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No transactions found.")
    else:
        print(f"{'ID':<5} {'Product':<20} {'Qty':<8} {'Type':<10} {'Date'}")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<8} {row[3]:<10} {row[4]}")


def show_low_stock():
    print("\nLow Stock Products (less than 5):")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE quantity < 5")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No low stock products.")
    else:
        print(f"{'ID':<5} {'Name':<20} {'Qty':<8} {'Price':<10} {'Description'}")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[3]:<8} Rs.{row[4]:<10} {row[2]}")


def menu():
    print("DEBUG: Running updated menu!")  # Add this line to confirm correct versio
    while True:
        print("\n==== Inventory Menu ====")
        print("1. Add Product")
        print("2. View Products")
        print("3. Update Stock")
        print("4. View Transaction History")
        print("5. Low Stock Alerts")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_product()
        elif choice == '2':
            view_products()
        elif choice == '3':
            update_stock()
        elif choice == '4':
            view_transactions()
        elif choice == '5':
            show_low_stock()
        elif choice == '6':
            print("Exiting Inventory Management System.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    print("Starting Inventory Management System...")
    menu()
