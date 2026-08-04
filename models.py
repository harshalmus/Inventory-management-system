"""
SQLAlchemy models for the Inventory Management System.

Tables:
    User            - system users (admin / staff) who can log in
    Category        - product categories
    Supplier        - vendors that products are purchased from
    Product         - inventory items
    Purchase        - a purchase "invoice" from a supplier (header record)
    PurchaseItem    - individual product lines within a purchase
    StockAdjustment - manual stock corrections (audit trail)
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="admin", nullable=False)  # admin / staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship("Product", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)          # contact person
    company = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    gst_number = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    purchases = db.relationship("Purchase", backref="supplier", lazy=True)

    def __repr__(self):
        return f"<Supplier {self.name}>"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    brand = db.Column(db.String(100), nullable=True)
    purchase_price = db.Column(db.Float, nullable=False, default=0.0)  # unit/cost price
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)  # filename in static/images/products
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    purchase_items = db.relationship("PurchaseItem", backref="product", lazy=True)
    stock_adjustments = db.relationship("StockAdjustment", backref="product", lazy=True)

    @property
    def stock_value(self):
        return round(self.purchase_price * self.quantity, 2)

    @property
    def stock_status(self):
        from flask import current_app
        threshold = current_app.config.get("LOW_STOCK_THRESHOLD", 10)
        if self.quantity <= 0:
            return "out"
        elif self.quantity <= threshold:
            return "low"
        return "ok"

    def __repr__(self):
        return f"<Product {self.product_code} {self.name}>"


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("PurchaseItem", backref="purchase", lazy=True,
                             cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Purchase {self.invoice_number}>"


class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchases.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)

    @property
    def line_total(self):
        return round(self.quantity * self.cost_price, 2)


class StockAdjustment(db.Model):
    """Audit trail of manual stock corrections (damage, recount, return, etc.)."""
    __tablename__ = "stock_adjustments"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    change = db.Column(db.Integer, nullable=False)  # positive = add, negative = remove
    reason = db.Column(db.String(255), nullable=True)
    adjusted_by = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
