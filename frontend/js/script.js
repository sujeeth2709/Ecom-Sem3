const API_BASE_URL = "/api";
let allProducts = []; // Store products globally for the search bar

/* ---------------- Session & UI Helpers ---------------- */

function currentUser() {
    const s = localStorage.getItem("session");
    return s ? JSON.parse(s) : null;
}

function requireLogin(role) {
    const u = currentUser();
    if (!u) { window.location.href = "index.html"; return null; }
    if (role && u.role !== role) {
        window.location.href = u.role === "admin" ? "shop.html" : "admin.html";
        return null;
    }
    return u;
}

function logout() {
    localStorage.removeItem("session");
    window.location.href = "index.html";
}

function toast(msg) {
    let t = document.getElementById("toast");
    if (!t) {
        t = document.createElement("div"); t.id = "toast"; t.className = "toast"; document.body.appendChild(t);
    }
    t.textContent = msg; t.style.display = "block";
    clearTimeout(window._toastTimer);
    window._toastTimer = setTimeout(() => (t.style.display = "none"), 1800);
}

/* ---------------- Client Cart Buffer Functions ---------------- */

// NEW: Generates a unique cart key for each specific user
function getCartKey() {
    const user = currentUser();
    return user ? `cart_${user.id}` : "cart";
}

function getCart() { 
    return JSON.parse(localStorage.getItem(getCartKey()) || "[]"); 
}

function saveCart(c) { 
    // Saves to the user-specific cart key
    localStorage.setItem(getCartKey(), JSON.stringify(c)); 
    updateCartPill(); 

    const user = currentUser();
    if (user && user.role === "customer") {
        fetch(`${API_BASE_URL}/cart/sync`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                userId: user.id,
                items: c.map(i => ({ productId: i.productId, qty: i.qty }))
            })
        }).catch(err => console.error("Failed to sync cart to database:", err));
    }
}

function updateCartPill() {
    const count = getCart().reduce((sum, item) => sum + item.qty, 0);
    const pill = document.getElementById("cart-count");
    if (pill) pill.textContent = count;
}

/* ---------------- 1. Auth Page API Calls ---------------- */

function initAuthPage() {
    const loginForm = document.getElementById("login-form");
    const regForm = document.getElementById("register-form");
    const tabLogin = document.getElementById("tab-login");
    const tabRegister = document.getElementById("tab-register");

    if (tabLogin && tabRegister && loginForm && regForm) {
        tabLogin.onclick = () => {
            loginForm.style.display = "";
            regForm.style.display = "none";
            tabLogin.classList.add("active");
            tabRegister.classList.remove("active");
        };
        tabRegister.onclick = () => {
            regForm.style.display = "";
            loginForm.style.display = "none";
            tabRegister.classList.add("active");
            tabLogin.classList.remove("active");
        };
    }

    if (loginForm) {
        loginForm.onsubmit = async (e) => {
            e.preventDefault();
            const res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: document.getElementById("login-email").value,
                    password: document.getElementById("login-pass").value
                })
            });

            if (res.ok) {
                const user = await res.json();
                localStorage.setItem("session", JSON.stringify(user));
                // Sync cart instantly on login to self-heal database discrepancies
                saveCart(getCart());
                window.location.href = user.role === "admin" ? "admin.html" : "shop.html";
            } else {
                const err = await res.json();
                alert(err.detail || "Login failed");
            }
        };
    }

    if (regForm) {
        regForm.onsubmit = async (e) => {
            e.preventDefault();
            const res = await fetch(`${API_BASE_URL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: document.getElementById("reg-name").value,
                    email: document.getElementById("reg-email").value,
                    password: document.getElementById("reg-pass").value
                })
            });

            if (res.ok) {
                const user = await res.json();
                localStorage.setItem("session", JSON.stringify(user));
                window.location.href = "shop.html";
            } else {
                const err = await res.json();
                alert(err.detail || "Registration failed");
            }
        };
    }
}

/* ---------------- 2. Shop Page API Calls ---------------- */

async function initShopPage() {
    const user = requireLogin("customer");
    if (!user) return;
    document.getElementById("who").textContent = user.name;

    const res = await fetch(`${API_BASE_URL}/products`);
    allProducts = await res.json();

    const searchBar = document.getElementById("search-bar");
    if (searchBar) {
        searchBar.addEventListener("input", (e) => {
            renderProducts(e.target.value);
        });
    }

    renderProducts("");
}

function renderProducts(searchQuery) {
    const wrap = document.getElementById("products");
    if (!wrap) return;
    wrap.innerHTML = "";

    const filtered = allProducts.filter(p => 
        p.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    filtered.forEach((p) => {
        const el = document.createElement("div");
        el.className = "product";
        el.innerHTML = `
            <div class="swatch"><img src="${p.image}" alt="${p.name}"></div>
            <h4>${p.name}</h4>
            <div class="muted">${p.category}</div>
            <div class="price">₹${p.price}</div>
            <div class="stock">${p.stock > 0 ? p.stock + " in stock" : "Out of stock"}</div>
            <button class="btn small" ${p.stock === 0 ? "disabled" : ""}>Add to cart</button>
        `;
        el.querySelector("button").onclick = () => {
            let cart = getCart();
            let line = cart.find((i) => i.productId === p.id);
            if (line) line.qty += 1;
            else cart.push({ productId: p.id, name: p.name, price: p.price, qty: 1 });
            saveCart(cart); 
            toast("Added to cart");
        };
        wrap.appendChild(el);
    });
    updateCartPill();
}

/* ---------------- 3. Checkout Page API Calls ---------------- */

window.removeFromCart = function(productId) {
    let cart = getCart();
    cart = cart.filter(item => item.productId !== productId);
    saveCart(cart); 
    initCheckoutPage(); 
    toast("Item removed");
};

async function initCheckoutPage() {
    const user = requireLogin("customer");
    if (!user) return;
    document.getElementById("who").textContent = user.name;
    
    updateCartPill(); 

    const cart = getCart();
    const tbody = document.getElementById("cart-body");
    let total = 0;

    if (tbody) {
        tbody.innerHTML = "";
        cart.forEach((item) => {
            total += item.price * item.qty;
            tbody.innerHTML += `
            <tr>
                <td>${item.name}</td>
                <td>₹${item.price}</td>
                <td>${item.qty}</td>
                <td>₹${item.price * item.qty}</td>
                <td><button class="btn danger small" onclick="removeFromCart(${item.productId})">Remove</button></td>
            </tr>`;
        });
        document.getElementById("cart-total").textContent = "₹" + total;
    }

    const historyRes = await fetch(`${API_BASE_URL}/orders/user/${user.id}`);
    const orders = await historyRes.json();
    const historyWrap = document.getElementById("order-history");
    if (historyWrap) {
        historyWrap.innerHTML = "";
        orders.forEach((o) => {
            historyWrap.innerHTML += `<tr><td>#${o.id}</td><td>${o.date}</td><td>₹${o.total}</td><td><span class="badge ${o.status.toLowerCase()}">${o.status}</span></td></tr>`;
        });
    }

    const orderBtn = document.getElementById("place-order");
    if (orderBtn) {
        orderBtn.onclick = async () => {
            if (cart.length === 0) {
                alert("Your cart is empty!");
                return;
            }
            
            const res = await fetch(`${API_BASE_URL}/orders`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    userId: user.id,
                    items: cart.map((i) => ({ productId: i.productId, qty: i.qty }))
                })
            });

            if (res.ok) {
                toast("Order Placed Successfully!");
                saveCart([]); 
                window.location.href = "shop.html";
            } else {
                const err = await res.json();
                alert(err.detail || "Order submission failed.");
            }
        };
    }
}

/* ---------------- 4. Admin Page API Calls ---------------- */

async function initAdminPage() {
    const user = requireLogin("admin");
    if (!user) return;
    document.getElementById("who").textContent = user.name;

    const res = await fetch(`${API_BASE_URL}/admin/dashboard`);
    const data = await res.json();

    document.getElementById("stat-products").textContent = data.stats.total_products;
    document.getElementById("stat-orders").textContent = data.stats.total_orders;
    document.getElementById("stat-lowstock").textContent = data.stats.low_stock;
    document.getElementById("stat-revenue").textContent = "₹" + data.stats.revenue;

    const pTable = document.getElementById("admin-products");
    pTable.innerHTML = "";
    data.products.forEach((p) => {
        pTable.innerHTML += `
            <tr>
                <td>${p.name}</td><td>${p.category}</td>
                <td>₹<input type="number" id="p-price-${p.id}" value="${p.price}" style="width:80px"></td>
                <td><input type="number" id="p-stock-${p.id}" value="${p.stock}" style="width:70px"></td>
                <td><button onclick="updateProduct(${p.id})">Save</button></td>
            </tr>`;
    });

    const oTable = document.getElementById("admin-orders");
    oTable.innerHTML = "";
    data.orders.forEach((o) => {
        oTable.innerHTML += `
            <tr>
                <td>#${o.id}</td><td>${o.customer_name}</td><td>${o.date}</td><td>₹${o.total}</td>
                <td>
                    <select onchange="updateOrderStatus(${o.id}, this.value)">
                        <option ${o.status === "Pending" ? "selected" : ""}>Pending</option>
                        <option ${o.status === "Paid" ? "selected" : ""}>Paid</option>
                        <option ${o.status === "Shipped" ? "selected" : ""}>Shipped</option>
                    </select>
                </td>
            </tr>`;
    });

    const addProductForm = document.getElementById("add-product-form");
    if (addProductForm) {
        addProductForm.onsubmit = async (e) => {
            e.preventDefault();
            const imageFile = document.getElementById("np-image").files[0];
            const image = imageFile ? await imageToDataUrl(imageFile) : null;
            const res = await fetch(`${API_BASE_URL}/admin/products`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: document.getElementById("np-name").value,
                    category: document.getElementById("np-cat").value,
                    price: Number(document.getElementById("np-price").value),
                    stock: Number(document.getElementById("np-stock").value),
                    image: image
                })
            });

            if (res.ok) {
                toast("Product Added");
                e.target.reset();
                initAdminPage();
            } else {
                const err = await res.json();
                alert(err.detail || "Failed to add product");
            }
        };
    }
}

function imageToDataUrl(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onerror = () => reject(new Error("Could not read image"));
        reader.onload = () => {
            const img = new Image();
            img.onerror = () => reject(new Error("Invalid image file"));
            img.onload = () => {
                const scale = Math.min(1, 400 / Math.max(img.width, img.height));
                const canvas = document.createElement("canvas");
                canvas.width = Math.round(img.width * scale);
                canvas.height = Math.round(img.height * scale);
                canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
                resolve(canvas.toDataURL("image/jpeg", 0.85));
            };
            img.src = reader.result;
        };
        reader.readAsDataURL(file);
    });
}

async function updateProduct(id) {
    const price = Number(document.getElementById(`p-price-${id}`).value);
    const stock = Number(document.getElementById(`p-stock-${id}`).value);

    const res = await fetch(`${API_BASE_URL}/admin/products/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ price, stock })
    });

    if (res.ok) toast("Product Updated");
}

async function updateOrderStatus(id, status) {
    const res = await fetch(`${API_BASE_URL}/admin/orders/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
    });

    if (res.ok) toast("Order Status Updated");
}