import sqlite3

# Connect to the grocery.db database
conn = sqlite3.connect('grocery.db')
cursor = conn.cursor()

# Check if tables exist in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:")
for table in tables:
    print(f"- {table[0]}")

# Optionally: Check table structure for the 'products' table
cursor.execute("PRAGMA table_info(products);")
columns = cursor.fetchall()
print("\nColumns in 'products' table:")
for column in columns:
    print(f"- {column[1]} (Type: {column[2]}, Not Null: {column[3]}, Primary Key: {column[5]})")

# Optionally: Check table structure for the 'suppliers' table
cursor.execute("PRAGMA table_info(suppliers);")
columns = cursor.fetchall()
print("\nColumns in 'suppliers' table:")
for column in columns:
    print(f"- {column[1]} (Type: {column[2]}, Not Null: {column[3]}, Primary Key: {column[5]})")

# Optionally: Check table structure for the 'categories' table
cursor.execute("PRAGMA table_info(categories);")
columns = cursor.fetchall()
print("\nColumns in 'categories' table:")
for column in columns:
    print(f"- {column[1]} (Type: {column[2]}, Not Null: {column[3]}, Primary Key: {column[5]})")

# Close the connection
conn.close()
