from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import sqlite3
import os

# Import from your other files
from database import init_db, get_db
from models import UserRegister, UserLogin, ProductCreate, ProductUpdate, OrderCreate, OrderStatusUpdate, CartSync

app = FastAPI(title="E-Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

# --- Auth Endpoints ---
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

# --- Product Endpoints ---
@app.get("/api/products")
def fetch_products(category: str = "All"):
    conn = get_db()
    cursor = conn.cursor()
    query = """
        SELECT p.id, p.name, c.name as category, p.price, p.stock, p.image 
        FROM products p
        JOIN categories c ON p.category_id = c.id
    """
    if category and category != "All":
        query += " WHERE c.name = ?"
        cursor.execute(query, (category,))
    else:
        cursor.execute(query)
    
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

@app.post("/api/admin/products")
def create_product(data: ProductCreate):
    if not data.name.strip() or data.price <= 0 or data.stock < 0:
        raise HTTPException(status_code=400, detail="Invalid product details provided.")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Lookup or create category ID
    cursor.execute("SELECT id FROM categories WHERE name = ?", (data.category,))
    cat = cursor.fetchone()
    if not cat:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (data.category,))
        cat_id = cursor.lastrowid
    else:
        cat_id = cat["id"]

    placeholder_image = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80"
    image = data.image if data.image and data.image.startswith("data:image/") and len(data.image) < 2_000_000 else placeholder_image
    
    cursor.execute("INSERT INTO products (name, category_id, price, stock, image) VALUES (?, ?, ?, ?, ?)",
                   (data.name.strip(), cat_id, data.price, data.stock, image))
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

# --- Cart Endpoints ---
@app.post("/api/cart/sync")
def sync_cart(data: CartSync):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart_items WHERE user_id = ?", (data.userId,))
    for item in data.items:
        cursor.execute("INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
                       (data.userId, item.productId, item.qty))
    conn.commit()
    conn.close()
    return {"message": "Cart synced to database"}

# --- Order Endpoints ---
@app.post("/api/orders")
def process_order(data: OrderCreate):
    if not data.items:
        raise HTTPException(status_code=400, detail="Cart is empty.")
        
    conn = get_db()
    cursor = conn.cursor()
    total_amount = 0.0
    validated_items = []

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
        validated_items.append((item, prod["price"]))

    order_date = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Insert Master Order
    cursor.execute("INSERT INTO orders (user_id, total, status, date) VALUES (?, ?, 'Paid', ?)",
                   (data.userId, total_amount, order_date))
    order_id = cursor.lastrowid
    
    # 2. Insert Order Items & Deduct Stock
    for item, unit_price in validated_items:
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                       (order_id, item.productId, item.qty, unit_price))
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item.qty, item.productId))

    # 3. Clear database cart after successful order
    cursor.execute("DELETE FROM cart_items WHERE user_id = ?", (data.userId,))

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

# --- Admin Dashboard ---
@app.get("/api/admin/dashboard")
def get_admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.id, p.name, c.name as category, p.price, p.stock, p.image 
        FROM products p
        JOIN categories c ON p.category_id = c.id
    """)
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

# --- Frontend Routing ---
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{page_name}.html")
    def serve_html_pages(page_name: str):
        page_path = os.path.join(FRONTEND_DIR, f"{page_name}.html")
        if os.path.exists(page_path):
            return FileResponse(page_path)
        raise HTTPException(status_code=404, detail="Page not found")