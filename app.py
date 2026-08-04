"""
Application entry point.
Run with:  python app.py
First run automatically creates the SQLite DB and seeds demo data.
"""
import os
import random
from datetime import datetime, timedelta

from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from config import Config
from models import (
    db, User, Category, Supplier, Product, Purchase, PurchaseItem, StockAdjustment
)

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Make sure required folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if db_uri.startswith("sqlite:///"):
        db_path = db_uri.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprint containing all routes
    from routes import main_bp
    app.register_blueprint(main_bp)

    # Template filters
    @app.template_filter("currency")
    def currency_filter(value):
        try:
            return f"\u20b9{value:,.2f}"
        except (TypeError, ValueError):
            return value

    with app.app_context():
        db.create_all()
        seed_demo_data()

    return app


def seed_demo_data():
    """Populate the database with demo data on first run only."""
    if User.query.first():
        return  # Already seeded

    print("Seeding demo data ...")

    admin = User(username="admin", email="admin@inventory.local", role="admin")
    admin.set_password("admin123")
    staff = User(username="staff", email="staff@inventory.local", role="staff")
    staff.set_password("staff123")
    db.session.add_all([admin, staff])

    categories = [
        Category(name="Electronics", description="Electronic gadgets and devices"),
        Category(name="Groceries", description="Everyday grocery items"),
        Category(name="Stationery", description="Office and school supplies"),
        Category(name="Furniture", description="Home and office furniture"),
        Category(name="Apparel", description="Clothing and accessories"),
    ]
    db.session.add_all(categories)

    suppliers = [
        Supplier(name="Rajesh Kumar", company="Kumar Electronics Pvt Ltd",
                 phone="9876543210", email="rajesh@kumarelec.in",
                 address="MG Road, Pune, Maharashtra", gst_number="27ABCDE1234F1Z5"),
        Supplier(name="Anita Sharma", company="Sharma Wholesale Traders",
                 phone="9823456789", email="anita@sharmatrade.in",
                 address="Sector 18, Noida, UP", gst_number="09XYZAB5678C1Z2"),
        Supplier(name="Vikram Patel", company="Patel Stationery House",
                 phone="9765432109", email="vikram@patelstationery.in",
                 address="CG Road, Ahmedabad, Gujarat", gst_number="24LMNOP4321Q1Z8"),
        Supplier(name="Sunita Reddy", company="Reddy Furniture Mart",
                 phone="9654321098", email="sunita@reddyfurniture.in",
                 address="Banjara Hills, Hyderabad, Telangana", gst_number="36QRSTU8765V1Z3"),
    ]
    db.session.add_all(suppliers)
    db.session.commit()

    product_data = [
        ("Wireless Mouse", 0, "Logitech", 450, 699, 85),
        ("Mechanical Keyboard", 0, "HP", 1800, 2599, 40),
        ("27-inch Monitor", 0, "Dell", 9500, 12999, 12),
        ("USB-C Hub", 0, "Anker", 900, 1399, 6),
        ("Bluetooth Speaker", 0, "boAt", 1200, 1899, 0),
        ("Basmati Rice 5kg", 1, "India Gate", 450, 599, 120),
        ("Cooking Oil 1L", 1, "Fortune", 130, 165, 200),
        ("Wheat Flour 10kg", 1, "Aashirvaad", 380, 449, 75),
        ("A4 Paper Ream", 2, "JK Copier", 220, 289, 150),
        ("Ballpoint Pens (Pack of 10)", 2, "Cello", 40, 65, 8),
        ("Notebook Set", 2, "Classmate", 90, 130, 5),
        ("Office Chair", 3, "Nilkamal", 3200, 4599, 18),
        ("Study Table", 3, "Godrej Interio", 5400, 7299, 9),
        ("Cotton T-Shirt", 4, "Allen Solly", 550, 899, 60),
        ("Formal Shirt", 4, "Van Heusen", 900, 1399, 0),
    ]

    products = []
    for idx, (name, cat_idx, brand, pp, sp, qty) in enumerate(product_data, start=1):
        p = Product(
            product_code=f"PRD{1000 + idx}",
            name=name,
            category_id=categories[cat_idx].id,
            brand=brand,
            purchase_price=pp,
            selling_price=sp,
            quantity=qty,
            description=f"{name} - quality product sourced from a trusted brand.",
        )
        products.append(p)
    db.session.add_all(products)
    db.session.commit()

    # Create a few demo purchase records
    for i in range(5):
        supplier = random.choice(suppliers)
        purchase = Purchase(
            invoice_number=f"INV-2026-{1000 + i}",
            supplier_id=supplier.id,
            purchase_date=datetime.utcnow().date() - timedelta(days=random.randint(1, 60)),
            total_amount=0,
        )
        db.session.add(purchase)
        db.session.flush()

        total = 0
        chosen = random.sample(products, k=random.randint(1, 3))
        for prod in chosen:
            qty = random.randint(5, 30)
            item = PurchaseItem(
                purchase_id=purchase.id,
                product_id=prod.id,
                quantity=qty,
                cost_price=prod.purchase_price,
            )
            total += qty * prod.purchase_price
            db.session.add(item)
        purchase.total_amount = round(total, 2)

    db.session.commit()
    print("Demo data seeded successfully.")
    print("Login with -> username: admin / password: admin123")


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
