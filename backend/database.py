import sqlite3

DB_NAME = "ecommerce.db"
EARBUDS_IMAGE = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0MDAgNDAwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImJnIiB4MT0iMCIgeTE9IjAiIHgyPSIxIiB5Mj0iMSI+PHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjZjRmNWY3Ii8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjZDVkYWUzIi8+PC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImNzIiB4MT0iMCIgeTE9IjAiIHgyPSIwIiB5Mj0iMSI+PHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjZmZmZmZmIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjZTNlNmVjIi8+PC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImViIiB4MT0iMCIgeTE9IjAiIHgyPSIxIiB5Mj0iMSI+PHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjZmZmZmZmIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjY2ZkNGRlIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSI0MDAiIGZpbGw9InVybCgjYmcpIi8+PGVsbGlwc2UgY3g9IjIwMCIgY3k9IjMzOCIgcng9IjEyMCIgcnk9IjE0IiBmaWxsPSIjMDAwIiBvcGFjaXR5PSIuMTIiLz48cmVjdCB4PSI5NSIgeT0iMjE1IiB3aWR0aD0iMjEwIiBoZWlnaHQ9IjExNSIgcng9IjQyIiBmaWxsPSJ1cmwoI2NzKSIgc3Ryb2tlPSIjYzNjOWQ1IiBzdHJva2Utd2lkdGg9IjIiLz48cGF0aCBkPSJNOTcgMjYyIEgzMDMiIHN0cm9rZT0iI2MzYzlkNSIgc3Ryb2tlLXdpZHRoPSIyIi8+PGNpcmNsZSBjeD0iMjAwIiBjeT0iMjkyIiByPSI1IiBmaWxsPSIjZjVhNjIzIi8+PGcgZmlsbD0idXJsKCNlYikiIHN0cm9rZT0iI2I5YzBjZCIgc3Ryb2tlLXdpZHRoPSIyIj48ZyB0cmFuc2Zvcm09InJvdGF0ZSgtMTQgMTQ4IDE1MCkiPjxlbGxpcHNlIGN4PSIxNDgiIGN5PSIxMTgiIHJ4PSIzNCIgcnk9IjM4Ii8+PHJlY3QgeD0iMTM0IiB5PSIxMzIiIHdpZHRoPSIyNiIgaGVpZ2h0PSI4MiIgcng9IjEzIi8+PC9nPjxnIHRyYW5zZm9ybT0icm90YXRlKDE0IDI1MiAxNTApIj48ZWxsaXBzZSBjeD0iMjUyIiBjeT0iMTE4IiByeD0iMzQiIHJ5PSIzOCIvPjxyZWN0IHg9IjI0MCIgeT0iMTMyIiB3aWR0aD0iMjYiIGhlaWdodD0iODIiIHJ4PSIxMyIvPjwvZz48L2c+PGcgZmlsbD0iIzJiMmYzYSIgb3BhY2l0eT0iLjg1Ij48Y2lyY2xlIGN4PSIxMzYiIGN5PSIxMjAiIHI9IjEyIiB0cmFuc2Zvcm09InJvdGF0ZSgtMTQgMTQ4IDE1MCkiLz48Y2lyY2xlIGN4PSIyNjQiIGN5PSIxMjAiIHI9IjEyIiB0cmFuc2Zvcm09InJvdGF0ZSgxNCAyNTIgMTUwKSIvPjwvZz48L3N2Zz4K"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer'
        )
    ''')

    # 2. Categories Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # 3. Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            image TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # 4. Cart Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            PRIMARY KEY (user_id, product_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # 5. Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Paid',
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 6. Order Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            PRIMARY KEY (order_id, product_id),
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # Seed Users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                       ("Sujeeth S", "admin@store.com", "admin123", "admin"))
        cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                       ("Test Customer", "customer@store.com", "pass123", "customer"))

    # Seed Categories
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cats = [("Electronics",), ("Fashion",), ("Home & Kitchen",), ("Books",)]
        cursor.executemany("INSERT INTO categories (name) VALUES (?)", cats)

    # Seed Products
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        seed_products = [
            ("Wireless Earbuds", 1, 1999, 34, EARBUDS_IMAGE),
            ("Smart Watch", 1, 3499, 12, "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400&q=80"),
            ("Cotton T-Shirt", 2, 499, 80, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80"),
            ("Running Shoes", 2, 2299, 0, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"),
            ("Non-stick Pan", 3, 899, 25, "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400&q=80"),
            ("Table Lamp", 3, 749, 18, "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&q=80"),
            ("DBMS Textbook", 4, 599, 40, "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&q=80"),
            ("Novel: The Silent Patient", 4, 349, 22, "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=400&q=80")
        ]
        cursor.executemany("INSERT INTO products (name, category_id, price, stock, image) VALUES (?, ?, ?, ?, ?)", seed_products)

    conn.commit()
    conn.close()