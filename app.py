from flask import Flask, render_template, request, redirect, url_for, flash
from database import connect_db, setup_database

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Used for flashing messages

# Set up database when app starts
setup_database()

@app.route('/')
def index():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products ORDER BY product_id ASC")
    products = cursor.fetchall()
    conn.close()
    return render_template("index.html", products=products)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        qty = int(request.form['qty'])
        price = float(request.form['price'])

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Products (name, description, quantity, price) VALUES (?, ?, ?, ?)",
                       (name, desc, qty, price))
        conn.commit()
        conn.close()
        flash('Product added successfully!')
        return redirect(url_for('index'))

    return render_template("add_product.html")

@app.route('/update_stock/<int:product_id>', methods=['GET', 'POST'])
def update_stock(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE product_id = ?", (product_id,))
    product = cursor.fetchone()

    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        new_qty = product[3] + quantity

        if new_qty < 0:
            flash("Not enough stock to remove.")
            return redirect(url_for('index'))

        cursor.execute("UPDATE Products SET quantity = ? WHERE product_id = ?", (new_qty, product_id))
        transaction_type = 'add' if quantity > 0 else 'remove'
        cursor.execute("INSERT INTO Transactions (product_id, quantity_changed, transaction_type) VALUES (?, ?, ?)",
                       (product_id, quantity, transaction_type))

        conn.commit()
        conn.close()
        flash("Stock updated successfully.")
        return redirect(url_for('index'))

    conn.close()
    return render_template("update_stock.html", product=product)

@app.route('/transactions')
def transactions():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.transaction_id, P.name, T.quantity_changed, T.transaction_type, T.date
        FROM Transactions T
        JOIN Products P ON T.product_id = P.product_id
        ORDER BY T.date DESC
    """)
    txns = cursor.fetchall()
    conn.close()
    return render_template("transactions.html", transactions=txns)

@app.route('/low_stock')
def low_stock():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE quantity <= 5")
    products = cursor.fetchall()
    conn.close()
    return render_template("low_stock.html", products=products)

@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM Transactions WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM Products WHERE product_id = ?", (product_id,))

    conn.commit()
    conn.close()
    flash("Product deleted successfully.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
