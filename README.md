# StockPilot &mdash; Inventory Management System

A complete, modern, responsive Inventory Management System built with **Flask**,
**SQLAlchemy**, **Flask-Login**, **Bootstrap 5**, and **Chart.js**.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **Authentication** &mdash; secure login/logout with hashed passwords (Flask-Login + Werkzeug)
- **Dashboard** &mdash; total products/suppliers/purchases, stock value, low/out-of-stock counts,
  recent purchases, and Chart.js visualizations (purchase trend, stock status, category split)
- **Product Management** &mdash; add/edit/delete, image upload, auto-generated product codes,
  search and category filter, pagination
- **Category Management** &mdash; full CRUD via modal forms
- **Supplier Management** &mdash; full CRUD with GST number, search
- **Purchase Management** &mdash; multi-line purchase entry that **automatically increases stock**,
  invoice auto-numbering, purchase detail view, delete reverses stock
- **Stock Management** &mdash; live stock levels with progress indicators, manual stock
  adjustments (add/remove) with a full audit trail
- **Reports** &mdash; Product, Purchase, Supplier, Low Stock, and Stock Summary reports,
  each exportable as **PDF** or **CSV**
- **UI/UX** &mdash; responsive sidebar layout, top navbar with quick search, dashboard cards,
  data tables with pagination, modal forms, toast notifications, dark mode toggle,
  loading spinner, and delete confirmation dialogs

---

## 🛠 Tech Stack

| Layer          | Technology                    |
|----------------|--------------------------------|
| Backend        | Python 3 + Flask               |
| ORM            | SQLAlchemy (Flask-SQLAlchemy)  |
| Auth           | Flask-Login                    |
| Forms/CSRF     | Flask-WTF + WTForms            |
| Database       | SQLite                         |
| Frontend       | HTML5, CSS3, vanilla JavaScript|
| CSS Framework  | Bootstrap 5 + Bootstrap Icons  |
| Charts         | Chart.js                       |
| PDF export     | ReportLab                      |

---

## 📁 Project Structure

```
inventory_management/
│
├── app.py                 # App factory, login manager, demo-data seeding
├── models.py               # SQLAlchemy models
├── routes.py                # All routes (Blueprint)
├── forms.py                  # WTForms form classes
├── config.py                  # App configuration
├── requirements.txt
│
├── static/
│   ├── css/style.css        # Theme (light + dark mode)
│   ├── js/main.js            # Dark mode, sidebar, toasts, validation
│   └── images/products/      # Uploaded product images
│
├── templates/
│   ├── base.html              # Sidebar + navbar + toast/layout shell
│   ├── login.html
│   ├── dashboard.html
│   ├── products.html / product_form.html
│   ├── categories.html
│   ├── suppliers.html
│   ├── purchases.html / purchase_form.html / purchase_view.html
│   ├── stock.html
│   ├── reports.html
│   ├── _pagination.html       # Reusable pagination partial
│   └── 404.html
│
└── database/
    └── inventory.db          # Auto-created SQLite DB (on first run)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9 or newer
- `pip`

### 2. Setup

```bash
# 1. Navigate into the project folder
cd inventory_management

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

The app will start at **http://127.0.0.1:5000**

On the very first run, the SQLite database is created automatically at
`database/inventory.db` and pre-populated with **demo data**: 2 users, 5
categories, 4 suppliers, 15 products, and 5 sample purchases.

### 3. Demo Login Credentials

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | `admin`  |           |
| Staff | `staff`  |           |

> ⚠️ Change these credentials (or create new users directly in the database)
> before deploying anywhere public.

---

## ⚙️ Configuration

Key settings live in `config.py` and can be overridden with environment
variables:

| Variable        | Purpose                                  | Default                        |
|-----------------|-------------------------------------------|---------------------------------|
| `SECRET_KEY`    | Session/CSRF signing key                  | dev key (change in production) |
| `DATABASE_URL`  | SQLAlchemy database URI                   | local SQLite file              |

Low-stock threshold and pagination size are also configurable in `config.py`
(`LOW_STOCK_THRESHOLD`, `ITEMS_PER_PAGE`).

---

## 🗄 Database Schema

| Table            | Key Columns                                                              |
|-------------------|----------------------------------------------------------------------------|
| `users`           | username, password_hash, role                                            |
| `categories`      | name, description                                                        |
| `products`        | product_code, name, category_id, brand, purchase_price, selling_price, quantity, image |
| `suppliers`       | name, company, phone, email, address, gst_number                         |
| `purchases`       | invoice_number, supplier_id, purchase_date, total_amount                 |
| `purchase_items`  | purchase_id, product_id, quantity, cost_price                            |
| `stock_adjustments`| product_id, change, reason, adjusted_by                                 |

Adding a purchase automatically increases the related product's `quantity`.
Deleting a purchase reverses that stock change. Manual stock corrections go
through the Stock page and are logged in `stock_adjustments` for a full audit
trail.

---

## 📤 Reports & Export

Visit **Reports** from the sidebar to generate:
- Product Report
- Purchase Report
- Supplier Report
- Low Stock Report
- Stock Summary

Every report can be downloaded as **PDF** (via ReportLab) or **CSV**.

---

## 🔒 Security Notes

- Passwords are hashed with Werkzeug's `generate_password_hash`/`check_password_hash`.
- All state-changing forms are protected with CSRF tokens (Flask-WTF).
- File uploads are restricted by extension and size (5MB max) and saved
  under randomly generated filenames.
- Product deletion is a soft-delete (`is_active=False`) so purchase history
  stays intact; category/supplier deletion is blocked while referenced by
  existing products/purchases.

---

## 📝 License

This project is provided as-is for educational and internal business use.
