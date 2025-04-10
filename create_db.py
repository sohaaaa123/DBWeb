import sqlite3 

# Connect to your existing grocery.db file (or it will be created if it doesn't exist)
conn = sqlite3.connect('grocery.db')  
cursor = conn.cursor()

# Create the Categories table
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
''')

# Create the Suppliers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT NOT NULL,
    phone TEXT NOT NULL
);
''')

# Create the Products table with a foreign key reference to the categories and suppliers tables
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

# Create the Stock Overview table (Optional)
# This can be used to track the stock information separately if needed, for now it's integrated into the `products` table
cursor.execute('''
CREATE TABLE IF NOT EXISTS stock_overview (
    product_id INTEGER PRIMARY KEY,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
''')

# Commit the changes to the database
conn.commit()

# Close the database connection
conn.close()

# Print a success message
print("Tables created successfully!")
