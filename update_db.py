import sqlite3

# Connect to the database
conn = sqlite3.connect('grocery.db')
cursor = conn.cursor()

# Step 1: Add the new columns (category_id, supplier_id)
cursor.execute('''
ALTER TABLE products ADD COLUMN category_id INTEGER;
''')

cursor.execute('''
ALTER TABLE products ADD COLUMN supplier_id INTEGER;
''')

# Step 2: Update the new columns based on the existing 'category' and 'supplier' (this may need to be modified to use the correct references)
cursor.execute('''
UPDATE products
SET category_id = (SELECT id FROM categories WHERE categories.name = products.category);
''')

cursor.execute('''
UPDATE products
SET supplier_id = (SELECT id FROM suppliers WHERE suppliers.name = products.supplier);
''')

# Step 3: Remove the old category and supplier columns from the 'products' table (this requires creating a new table)
cursor.execute('''
PRAGMA foreign_keys=off;
''')

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

cursor.execute('''
DROP TABLE products;
''')

cursor.execute('''
ALTER TABLE new_products RENAME TO products;
''')

cursor.execute('''
PRAGMA foreign_keys=on;
''')

# Commit and close the connection
conn.commit()
conn.close()

print("Products table updated successfully!")
