import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- DATABASE SETUP FUNCTIONS ---

def create_database():
    conn = sqlite3.connect('grocery.db')
    cursor = conn.cursor()

    # Create Categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    ''')

    # Create Suppliers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT NOT NULL,
        phone TEXT NOT NULL
    );
    ''')

    # Create Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category_id INTEGER NOT NULL,
        supplier_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    );
    ''')

    # Create Stock Overview table (Optional)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_overview (
        product_id INTEGER PRIMARY KEY,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    ''')

    conn.commit()
    conn.close()
    print("Tables created successfully!")

def check_database():
    conn = sqlite3.connect('grocery.db')
    cursor = conn.cursor()

    # Print tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")

    # Print columns of each table
    for tbl in ['products', 'suppliers', 'categories']:
        cursor.execute(f"PRAGMA table_info({tbl});")
        columns = cursor.fetchall()
        print(f"\nColumns in '{tbl}' table:")
        for column in columns:
            print(f"- {column[1]} (Type: {column[2]}, Not Null: {column[3]}, Primary Key: {column[5]})")

    conn.close()

def update_database_schema():
    conn = sqlite3.connect('grocery.db')
    cursor = conn.cursor()

    try:
        # Add new columns if not present (this may throw an error if they already exist)
        cursor.execute('ALTER TABLE products ADD COLUMN category_id INTEGER;')
        cursor.execute('ALTER TABLE products ADD COLUMN supplier_id INTEGER;')
    except:
        pass  # Ignore if columns already exist

    try:
        # Migrate data (only if `category` and `supplier` columns existed)
        cursor.execute('''
        UPDATE products
        SET category_id = (SELECT id FROM categories WHERE categories.name = products.category);
        ''')

        cursor.execute('''
        UPDATE products
        SET supplier_id = (SELECT id FROM suppliers WHERE suppliers.name = products.supplier);
        ''')
    except:
        pass

    # Recreate products table properly
    cursor.execute('PRAGMA foreign_keys=off;')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS new_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category_id INTEGER NOT NULL,
        supplier_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    );
    ''')

    cursor.execute('''
    INSERT INTO new_products (id, name, price, category_id, supplier_id, quantity)
    SELECT id, name, price, category_id, supplier_id, quantity FROM products;
    ''')

    cursor.execute('DROP TABLE products;')
    cursor.execute('ALTER TABLE new_products RENAME TO products;')
    cursor.execute('PRAGMA foreign_keys=on;')

    conn.commit()
    conn.close()
    print("Database schema updated.")

# Call setup functions
create_database()
check_database()
update_database_schema()

# --- DATABASE CONNECTION ---
def get_db_connection():
    conn = sqlite3.connect('grocery.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category_id = int(request.form['category_id'])
        supplier_id = int(request.form['supplier_id'])
        quantity = int(request.form['quantity'])

        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, price, category_id, supplier_id, quantity) VALUES (?, ?, ?, ?, ?)',
                     (name, price, category_id, supplier_id, quantity))
        conn.commit()
        conn.close()

        return redirect(url_for('products'))

    conn = get_db_connection()
    products = conn.execute('''
    SELECT p.id, p.name, p.price, p.quantity, c.name AS category, s.name AS supplier
    FROM products p
    JOIN categories c ON p.category_id = c.id
    JOIN suppliers s ON p.supplier_id = s.id;
    ''').fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products'))

@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category_id = int(request.form['category_id'])
        supplier_id = int(request.form['supplier_id'])
        quantity = int(request.form['quantity'])

        conn.execute('''
        UPDATE products SET name = ?, price = ?, category_id = ?, supplier_id = ?, quantity = ?
        WHERE id = ?
        ''', (name, price, category_id, supplier_id, quantity, product_id))
        conn.commit()
        conn.close()
        return redirect(url_for('products'))

    conn.close()
    return render_template('edit_product.html', product=product)

@app.route('/search_product', methods=['GET'])
def search_product():
    query = request.args.get('search_query')
    conn = get_db_connection()
    products = conn.execute('''
    SELECT p.id, p.name, p.price, p.quantity, c.name AS category, s.name AS supplier
    FROM products p
    JOIN categories c ON p.category_id = c.id
    JOIN suppliers s ON p.supplier_id = s.id
    WHERE p.name LIKE ?
    ''', ('%' + query + '%',)).fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/stock_overview')
def stock_overview():
    conn = get_db_connection()
    products = conn.execute('''
    SELECT p.name, p.quantity, c.name AS category
    FROM products p
    JOIN categories c ON p.category_id = c.id
    ''').fetchall()
    conn.close()
    return render_template('stock_overview.html', products=products)

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

@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        phone = request.form['phone']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO suppliers (name, contact, phone) VALUES (?, ?, ?)", (name, contact, phone))
            conn.commit()
            conn.close()
            return redirect(url_for('suppliers'))
        except Exception as e:
            return f"Error adding supplier: {e}"

    return render_template('add_supplier.html')

@app.route('/delete_supplier/<int:supplier_id>')
def delete_supplier(supplier_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('suppliers'))

if __name__ == '__main__':
    app.run(debug=True)
