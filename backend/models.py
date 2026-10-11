from pydantic import BaseModel
from typing import List, Optional

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

class CartSync(BaseModel):
    userId: int
    items: List[CartItem]

class OrderCreate(BaseModel):
    userId: int
    items: List[CartItem]

class OrderStatusUpdate(BaseModel):
    status: str