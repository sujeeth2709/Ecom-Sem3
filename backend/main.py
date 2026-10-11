from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import sqlite3
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="E-Commerce API")



# Enable CORS for frontend client calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "ecommerce.db"

EARBUDS_IMAGE = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0MDAgNDAwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImJnIiB4MT0iMCIgeTE9IjAiIHgyPSIxIiB5Mj0iMSI+PHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjZjRmNWY3Ii8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjZDVkYWUzIi8+PC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImNzIiB4MT0iMCIgeTE9IjAiIHgyPSIwIiB5Mj0iMSI+PHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjZmZmZmZmIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjZTNlNmVjIi8+PC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImViIiB4MT0iMCIgeTE9IjAiIHgyPSIxIiB5Mj0iMSI+PHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjZmZmZmZmIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjY2ZkNGRlIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSI0MDAiIGZpbGw9InVybCgjYmcpIi8+PGVsbGlwc2UgY3g9IjIwMCIgY3k9IjMzOCIgcng9IjEyMCIgcnk9IjE0IiBmaWxsPSIjMDAwIiBvcGFjaXR5PSIuMTIiLz48cmVjdCB4PSI5NSIgeT0iMjE1IiB3aWR0aD0iMjEwIiBoZWlnaHQ9IjExNSIgcng9IjQyIiBmaWxsPSJ1cmwoI2NzKSIgc3Ryb2tlPSIjYzNjOWQ1IiBzdHJva2Utd2lkdGg9IjIiLz48cGF0aCBkPSJNOTcgMjYyIEgzMDMiIHN0cm9rZT0iI2MzYzlkNSIgc3Ryb2tlLXdpZHRoPSIyIi8+PGNpcmNsZSBjeD0iMjAwIiBjeT0iMjkyIiByPSI1IiBmaWxsPSIjZjVhNjIzIi8+PGcgZmlsbD0idXJsKCNlYikiIHN0cm9rZT0iI2I5YzBjZCIgc3Ryb2tlLXdpZHRoPSIyIj48ZyB0cmFuc2Zvcm09InJvdGF0ZSgtMTQgMTQ4IDE1MCkiPjxlbGxpcHNlIGN4PSIxNDgiIGN5PSIxMTgiIHJ4PSIzNCIgcnk9IjM4Ii8+PHJlY3QgeD0iMTM0IiB5PSIxMzIiIHdpZHRoPSIyNiIgaGVpZ2h0PSI4MiIgcng9IjEzIi8+PC9nPjxnIHRyYW5zZm9ybT0icm90YXRlKDE0IDI1MiAxNTApIj48ZWxsaXBzZSBjeD0iMjUyIiBjeT0iMTE4IiByeD0iMzQiIHJ5PSIzOCIvPjxyZWN0IHg9IjI0MCIgeT0iMTMyIiB3aWR0aD0iMjYiIGhlaWdodD0iODIiIHJ4PSIxMyIvPjwvZz48L2c+PGcgZmlsbD0iIzJiMmYzYSIgb3BhY2l0eT0iLjg1Ij48Y2lyY2xlIGN4PSIxMzYiIGN5PSIxMjAiIHI9IjEyIiB0cmFuc2Zvcm09InJvdGF0ZSgtMTQgMTQ4IDE1MCkiLz48Y2lyY2xlIGN4PSIyNjQiIGN5PSIxMjAiIHI9IjEyIiB0cmFuc2Zvcm09InJvdGF0ZSgxNCAyNTIgMTUwKSIvPjwvZz48L3N2Zz4K"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- Database Initialization ----------------

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer'
        )
    ''')

    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            image TEXT
        )
    ''')

    # Orders Table
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

    # Seed Default Data if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                       ("Sujeeth S", "admin@store.com", "admin123", "admin"))
        cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                       ("Test Customer", "customer@store.com", "pass123", "customer"))

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        seed_products = [
            ("Wireless Earbuds", "Electronics", 1999, 34, EARBUDS_IMAGE),
            ("Smart Watch", "Electronics", 3499, 12, "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400&q=80"),
            ("Cotton T-Shirt", "Fashion", 499, 80, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80"),
            ("Running Shoes", "Fashion", 2299, 0, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"),
            ("Non-stick Pan", "Home & Kitchen", 899, 25, "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400&q=80"),
            ("Table Lamp", "Home & Kitchen", 749, 18, "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&q=80"),
            ("DBMS Textbook", "Books", 599, 40, "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&q=80"),
            ("Novel: The Silent Patient", "Books", 349, 22, "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=400&q=80")
        ]
        cursor.executemany("INSERT INTO products (name, category, price, stock, image) VALUES (?, ?, ?, ?, ?)", seed_products)

    # Replace the broken Wireless Earbuds picture in existing databases
    cursor.execute("UPDATE products SET image = ? WHERE name = 'Wireless Earbuds' AND image LIKE '%photo-1572569432755%'",
                   (EARBUDS_IMAGE,))

    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

# ---------------- Pydantic Request Schemas ----------------

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    stock: int
    image: Optional[str] = None

class ProductUpdate(BaseModel):
    price: float
    stock: int

class CartItem(BaseModel):
    productId: int
    qty: int

class OrderCreate(BaseModel):
    userId: int
    items: List[CartItem]

class OrderStatusUpdate(BaseModel):
    status: str

# ---------------- API Endpoints (All Business Logic Lives Here) ----------------

# 1. Authentication Logic
@app.post("/api/auth/register")
def register_user(data: UserRegister):
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'customer')",
                       (data.name.strip(), data.email.strip(), data.password))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"id": user_id, "name": data.name, "email": data.email, "role": "customer"}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

@app.post("/api/auth/login")
def login_user(data: UserLogin):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role FROM users WHERE email = ? AND password = ?", 
                   (data.email.strip(), data.password))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    return dict(user)

# 2. Product Management Logic
@app.get("/api/products")
def fetch_products(category: str = "All"):
    conn = get_db()
    cursor = conn.cursor()
    if category and category != "All":
        cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

@app.post("/api/admin/products")
def create_product(data: ProductCreate):
    if not data.name.strip() or data.price <= 0 or data.stock < 0:
        raise HTTPException(status_code=400, detail="Invalid product details provided.")
    
    conn = get_db()
    cursor = conn.cursor()
    placeholder_image = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80"
    image = data.image if data.image and data.image.startswith("data:image/") and len(data.image) < 2_000_000 else placeholder_image
    cursor.execute("INSERT INTO products (name, category, price, stock, image) VALUES (?, ?, ?, ?, ?)",
                   (data.name.strip(), data.category, data.price, data.stock, image))
    conn.commit()
    conn.close()
    return {"message": "Product successfully added."}

@app.put("/api/admin/products/{product_id}")
def modify_product(product_id: int, data: ProductUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET price = ?, stock = ? WHERE id = ?", (data.price, data.stock, product_id))
    conn.commit()
    conn.close()
    return {"message": "Product successfully updated."}

# 3. Order Processing Logic (Server-side validation & calculations)
@app.post("/api/orders")
def process_order(data: OrderCreate):
    if not data.items:
        raise HTTPException(status_code=400, detail="Cart is empty.")
        
    conn = get_db()
    cursor = conn.cursor()
    total_amount = 0.0

    # Validate stock & compute total dynamically on the server
    for item in data.items:
        cursor.execute("SELECT price, stock, name FROM products WHERE id = ?", (item.productId,))
        prod = cursor.fetchone()
        if not prod:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Product with ID {item.productId} not found.")
        if prod["stock"] < item.qty:
            conn.close()
            raise HTTPException(status_code=400, detail=f"Insufficient stock for '{prod['name']}'.")
        
        total_amount += prod["price"] * item.qty

    # Record order and decrement database stock
    order_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO orders (user_id, total, status, date) VALUES (?, ?, 'Paid', ?)",
                   (data.userId, total_amount, order_date))
    
    for item in data.items:
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item.qty, item.productId))

    conn.commit()
    conn.close()
    return {"message": "Order placed successfully", "total": total_amount}

@app.get("/api/orders/user/{user_id}")
def fetch_user_orders(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,))
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

# 4. Admin Analytics Logic (Computed entirely on the server)
@app.get("/api/admin/dashboard")
def get_admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT orders.id, users.name as customer_name, orders.date, orders.total, orders.status 
        FROM orders 
        JOIN users ON orders.user_id = users.id 
        ORDER BY orders.id DESC
    """)
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {
        "stats": {
            "total_products": len(products),
            "total_orders": len(orders),
            "low_stock": sum(1 for p in products if p["stock"] < 15),
            "revenue": sum(o["total"] for o in orders)
        },
        "products": products,
        "orders": orders
    }

@app.put("/api/admin/orders/{order_id}")
def modify_order_status(order_id: int, data: OrderStatusUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (data.status, order_id))
    conn.commit()
    conn.close()
    return {"message": "Order status updated."}

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    # Mount static assets (CSS, JS, images)
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

    # Serve HTML pages directly
    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{page_name}.html")
    def serve_html_pages(page_name: str):
        page_path = os.path.join(FRONTEND_DIR, f"{page_name}.html")
        if os.path.exists(page_path):
            return FileResponse(page_path)
        raise HTTPException(status_code=404, detail="Page not found")