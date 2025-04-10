import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('grocery.db')
    conn.row_factory = sqlite3.Row  # This allows column names to be used as keys
    return conn

# Home page route
@app.route('/')
def home():
    return render_template('home.html')

# Manage Products page route
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form['category']
        quantity = int(request.form['quantity'])

        # Insert into the database without the 'id' (it will auto-increment)
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, price, category, quantity) VALUES (?, ?, ?, ?)',
                     (name, price, category, quantity))
        conn.commit()
        conn.close()

        return redirect(url_for('products'))
    
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('products.html', products=products)

# Delete a product
@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products'))

# Edit a product
@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form['category']
        quantity = int(request.form['quantity'])

        conn.execute('UPDATE products SET name = ?, price = ?, category = ?, quantity = ? WHERE id = ?',
                     (name, price, category, quantity, product_id))
        conn.commit()
        conn.close()
        return redirect(url_for('products'))
    
    conn.close()
    return render_template('edit_product.html', product=product)

# Search products
@app.route('/search_product', methods=['GET'])
def search_product():
    query = request.args.get('search_query')
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products WHERE name LIKE ?', ('%' + query + '%',)).fetchall()
    conn.close()
    return render_template('products.html', products=products)

# Show stock overview
@app.route('/stock_overview')
def stock_overview():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('stock_overview.html', products=products)

# Manage Suppliers page route
@app.route('/suppliers')
def suppliers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM suppliers')
        suppliers_list = cursor.fetchall()
        conn.close()
        return render_template('suppliers.html', suppliers=suppliers_list)
    except Exception as e:
        return f"Error fetching suppliers: {e}"

# Add Supplier page route
@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        contact = request.form['contact']
        phone = request.form['phone']

        try:
            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert the supplier into the database
            cursor.execute("INSERT INTO suppliers (name, contact, phone) VALUES (?, ?, ?)", (name, contact, phone))
            conn.commit()
            conn.close()

            # Redirect to the suppliers list page after successful insert
            return redirect(url_for('suppliers'))
        except Exception as e:
            # Handle any exceptions (e.g., database issues)
            return f"Error adding supplier: {e}"
    
    return render_template('add_supplier.html')

# Delete a supplier
@app.route('/delete_supplier/<int:supplier_id>')
def delete_supplier(supplier_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('suppliers'))  # Redirect to suppliers page after deletion


if __name__ == '__main__':
    app.run(debug=True)
