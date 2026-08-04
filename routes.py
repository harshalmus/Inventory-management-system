"""
All application routes, organised as a single Blueprint for simplicity.
Grouped by feature: Auth, Dashboard, Products, Categories, Suppliers,
Purchases, Stock, Reports, and small JSON API endpoints used by the
frontend (Chart.js data, live product search, etc).
"""
import csv
import io
import os
import uuid
from datetime import datetime

from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    jsonify, send_file, current_app, abort
)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func, or_
from werkzeug.utils import secure_filename

from models import (
    db, User, Category, Supplier, Product, Purchase, PurchaseItem, StockAdjustment
)
from forms import LoginForm, CategoryForm, SupplierForm, ProductForm, StockAdjustmentForm

main_bp = Blueprint("main", __name__)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def save_product_image(file_storage):
    """Save an uploaded image with a unique filename; returns stored filename or None."""
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        flash("Invalid image type. Allowed: png, jpg, jpeg, gif, webp.", "danger")
        return None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    file_storage.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
    return filename


def generate_product_code():
    """Auto-generate the next sequential product code, e.g. PRD1016."""
    last = Product.query.order_by(Product.id.desc()).first()
    next_num = 1001
    if last and last.product_code.startswith("PRD"):
        try:
            next_num = int(last.product_code.replace("PRD", "")) + 1
        except ValueError:
            next_num = Product.query.count() + 1001
    return f"PRD{next_num}"


def generate_invoice_number():
    year = datetime.utcnow().year
    count = Purchase.query.filter(Purchase.invoice_number.like(f"INV-{year}-%")).count()
    return f"INV-{year}-{1000 + count + 1}"


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------
@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html", form=form)


@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


@main_bp.route("/")
def index():
    return redirect(url_for("main.dashboard")) if current_user.is_authenticated else redirect(url_for("main.login"))


# --------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------
@main_bp.route("/dashboard")
@login_required
def dashboard():
    threshold = current_app.config["LOW_STOCK_THRESHOLD"]

    total_products = Product.query.filter_by(is_active=True).count()
    total_suppliers = Supplier.query.count()
    total_purchases = Purchase.query.count()

    total_stock_value = db.session.query(
        func.coalesce(func.sum(Product.purchase_price * Product.quantity), 0)
    ).filter(Product.is_active == True).scalar()  # noqa: E712

    low_stock_products = Product.query.filter(
        Product.is_active == True, Product.quantity > 0, Product.quantity <= threshold
    ).order_by(Product.quantity.asc()).all()

    out_of_stock_products = Product.query.filter(
        Product.is_active == True, Product.quantity <= 0
    ).all()

    recent_purchases = Purchase.query.order_by(Purchase.created_at.desc()).limit(6).all()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_suppliers=total_suppliers,
        total_purchases=total_purchases,
        total_stock_value=total_stock_value,
        low_stock_products=low_stock_products,
        out_of_stock_products=out_of_stock_products,
        recent_purchases=recent_purchases,
    )


@main_bp.route("/api/dashboard-charts")
@login_required
def dashboard_charts():
    """JSON data consumed by Chart.js on the dashboard."""
    # Products per category
    cat_rows = (
        db.session.query(Category.name, func.count(Product.id))
        .outerjoin(Product, Product.category_id == Category.id)
        .group_by(Category.name)
        .all()
    )
    category_labels = [r[0] for r in cat_rows]
    category_counts = [r[1] for r in cat_rows]

    # Stock status breakdown
    threshold = current_app.config["LOW_STOCK_THRESHOLD"]
    ok_count = Product.query.filter(Product.quantity > threshold).count()
    low_count = Product.query.filter(Product.quantity > 0, Product.quantity <= threshold).count()
    out_count = Product.query.filter(Product.quantity <= 0).count()

    # Purchases over the last 6 months
    month_rows = (
        db.session.query(
            func.strftime("%Y-%m", Purchase.purchase_date), func.sum(Purchase.total_amount)
        )
        .group_by(func.strftime("%Y-%m", Purchase.purchase_date))
        .order_by(func.strftime("%Y-%m", Purchase.purchase_date))
        .limit(6)
        .all()
    )
    month_labels = [r[0] for r in month_rows]
    month_totals = [round(r[1] or 0, 2) for r in month_rows]

    return jsonify({
        "category_labels": category_labels,
        "category_counts": category_counts,
        "stock_status": {"ok": ok_count, "low": low_count, "out": out_count},
        "month_labels": month_labels,
        "month_totals": month_totals,
    })


# --------------------------------------------------------------------------
# Products
# --------------------------------------------------------------------------
@main_bp.route("/products")
@login_required
def products():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "", type=str).strip()
    category_id = request.args.get("category", "", type=str)

    query = Product.query.filter_by(is_active=True)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Product.name.ilike(like), Product.product_code.ilike(like),
                                  Product.brand.ilike(like)))
    if category_id:
        query = query.filter(Product.category_id == int(category_id))

    pagination = query.order_by(Product.id.desc()).paginate(
        page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False
    )
    categories = Category.query.order_by(Category.name).all()

    return render_template(
        "products.html", products=pagination.items, pagination=pagination,
        categories=categories, search=search, category_id=category_id
    )


@main_bp.route("/products/add", methods=["GET", "POST"])
@login_required
def product_add():
    form = ProductForm()
    form.category_id.choices = [(0, "-- Select Category --")] + [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]

    if form.validate_on_submit():
        image_filename = save_product_image(form.image.data)
        product = Product(
            product_code=generate_product_code(),
            name=form.name.data.strip(),
            category_id=form.category_id.data or None,
            brand=form.brand.data.strip() if form.brand.data else None,
            purchase_price=form.purchase_price.data,
            selling_price=form.selling_price.data,
            quantity=form.quantity.data,
            description=form.description.data,
            image=image_filename,
        )
        db.session.add(product)
        db.session.commit()
        flash(f"Product '{product.name}' ({product.product_code}) added successfully.", "success")
        return redirect(url_for("main.products"))

    return render_template("product_form.html", form=form, mode="add")


@main_bp.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(0, "-- Select Category --")] + [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]

    if request.method == "GET":
        form.category_id.data = product.category_id or 0

    if form.validate_on_submit():
        new_image = save_product_image(form.image.data)
        if new_image:
            # Remove old image file if it exists
            if product.image:
                old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], product.image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            product.image = new_image

        product.name = form.name.data.strip()
        product.category_id = form.category_id.data or None
        product.brand = form.brand.data.strip() if form.brand.data else None
        product.purchase_price = form.purchase_price.data
        product.selling_price = form.selling_price.data
        product.quantity = form.quantity.data
        product.description = form.description.data
        db.session.commit()
        flash(f"Product '{product.name}' updated successfully.", "success")
        return redirect(url_for("main.products"))

    return render_template("product_form.html", form=form, mode="edit", product=product)


@main_bp.route("/products/delete/<int:product_id>", methods=["POST"])
@login_required
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False  # soft delete keeps purchase history intact
    db.session.commit()
    flash(f"Product '{product.name}' deleted.", "info")
    return redirect(url_for("main.products"))


@main_bp.route("/api/products/search")
@login_required
def api_products_search():
    """Used by the purchase-entry page to look up products live."""
    q = request.args.get("q", "").strip()
    query = Product.query.filter_by(is_active=True)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Product.name.ilike(like), Product.product_code.ilike(like)))
    results = query.order_by(Product.name).limit(15).all()
    return jsonify([{
        "id": p.id, "code": p.product_code, "name": p.name,
        "purchase_price": p.purchase_price, "quantity": p.quantity
    } for p in results])


# --------------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------------
@main_bp.route("/categories")
@login_required
def categories():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "", type=str).strip()

    query = Category.query
    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))

    pagination = query.order_by(Category.name).paginate(
        page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False
    )
    form = CategoryForm()
    return render_template("categories.html", categories=pagination.items,
                            pagination=pagination, search=search, form=form)


@main_bp.route("/categories/add", methods=["POST"])
@login_required
def category_add():
    form = CategoryForm()
    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data.strip()).first():
            flash("A category with this name already exists.", "danger")
        else:
            db.session.add(Category(name=form.name.data.strip(), description=form.description.data))
            db.session.commit()
            flash("Category added successfully.", "success")
    else:
        flash("Please correct the errors and try again.", "danger")
    return redirect(url_for("main.categories"))


@main_bp.route("/categories/edit/<int:category_id>", methods=["POST"])
@login_required
def category_edit(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data.strip()
        category.description = form.description.data
        db.session.commit()
        flash("Category updated successfully.", "success")
    else:
        flash("Please correct the errors and try again.", "danger")
    return redirect(url_for("main.categories"))


@main_bp.route("/categories/delete/<int:category_id>", methods=["POST"])
@login_required
def category_delete(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products:
        flash(f"Cannot delete '{category.name}' - it has products assigned to it.", "danger")
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted.", "info")
    return redirect(url_for("main.categories"))


# --------------------------------------------------------------------------
# Suppliers
# --------------------------------------------------------------------------
@main_bp.route("/suppliers")
@login_required
def suppliers():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "", type=str).strip()

    query = Supplier.query
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Supplier.name.ilike(like), Supplier.company.ilike(like),
                                  Supplier.phone.ilike(like), Supplier.email.ilike(like)))

    pagination = query.order_by(Supplier.name).paginate(
        page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False
    )
    form = SupplierForm()
    return render_template("suppliers.html", suppliers=pagination.items,
                            pagination=pagination, search=search, form=form)


@main_bp.route("/suppliers/add", methods=["POST"])
@login_required
def supplier_add():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data.strip(), company=form.company.data,
            phone=form.phone.data, email=form.email.data,
            address=form.address.data, gst_number=form.gst_number.data,
        )
        db.session.add(supplier)
        db.session.commit()
        flash("Supplier added successfully.", "success")
    else:
        flash("Please correct the errors and try again.", "danger")
    return redirect(url_for("main.suppliers"))


@main_bp.route("/suppliers/edit/<int:supplier_id>", methods=["POST"])
@login_required
def supplier_edit(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    form = SupplierForm()
    if form.validate_on_submit():
        supplier.name = form.name.data.strip()
        supplier.company = form.company.data
        supplier.phone = form.phone.data
        supplier.email = form.email.data
        supplier.address = form.address.data
        supplier.gst_number = form.gst_number.data
        db.session.commit()
        flash("Supplier updated successfully.", "success")
    else:
        flash("Please correct the errors and try again.", "danger")
    return redirect(url_for("main.suppliers"))


@main_bp.route("/suppliers/delete/<int:supplier_id>", methods=["POST"])
@login_required
def supplier_delete(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    if supplier.purchases:
        flash(f"Cannot delete '{supplier.name}' - purchase history exists for this supplier.", "danger")
    else:
        db.session.delete(supplier)
        db.session.commit()
        flash("Supplier deleted.", "info")
    return redirect(url_for("main.suppliers"))


# --------------------------------------------------------------------------
# Purchases
# --------------------------------------------------------------------------
@main_bp.route("/purchases")
@login_required
def purchases():
    page = request.args.get("page", 1, type=int)
    supplier_id = request.args.get("supplier", "", type=str)
    date_from = request.args.get("from", "", type=str)
    date_to = request.args.get("to", "", type=str)

    query = Purchase.query
    if supplier_id:
        query = query.filter(Purchase.supplier_id == int(supplier_id))
    if date_from:
        query = query.filter(Purchase.purchase_date >= date_from)
    if date_to:
        query = query.filter(Purchase.purchase_date <= date_to)

    pagination = query.order_by(Purchase.purchase_date.desc(), Purchase.id.desc()).paginate(
        page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False
    )
    supplier_list = Supplier.query.order_by(Supplier.name).all()

    return render_template("purchases.html", purchases=pagination.items, pagination=pagination,
                            suppliers=supplier_list, supplier_id=supplier_id,
                            date_from=date_from, date_to=date_to)


@main_bp.route("/purchases/add", methods=["GET", "POST"])
@login_required
def purchase_add():
    supplier_list = Supplier.query.order_by(Supplier.name).all()
    product_list = Product.query.filter_by(is_active=True).order_by(Product.name).all()

    if request.method == "POST":
        supplier_id = request.form.get("supplier_id", type=int)
        purchase_date = request.form.get("purchase_date")
        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")
        cost_prices = request.form.getlist("cost_price[]")

        errors = []
        if not supplier_id:
            errors.append("Please select a supplier.")
        if not purchase_date:
            errors.append("Please select a purchase date.")
        if not product_ids or all(not pid for pid in product_ids):
            errors.append("Please add at least one product line item.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("purchase_form.html", suppliers=supplier_list,
                                    products=product_list, today=datetime.utcnow().date().isoformat())

        purchase = Purchase(
            invoice_number=generate_invoice_number(),
            supplier_id=supplier_id,
            purchase_date=datetime.strptime(purchase_date, "%Y-%m-%d").date(),
            notes=request.form.get("notes", ""),
        )
        db.session.add(purchase)
        db.session.flush()  # get purchase.id before commit

        total_amount = 0.0
        line_count = 0
        for pid, qty, cost in zip(product_ids, quantities, cost_prices):
            if not pid or not qty or not cost:
                continue
            pid, qty, cost = int(pid), int(qty), float(cost)
            if qty <= 0:
                continue
            product = Product.query.get(pid)
            if not product:
                continue

            item = PurchaseItem(purchase_id=purchase.id, product_id=pid,
                                 quantity=qty, cost_price=cost)
            db.session.add(item)

            # Automatically increase stock
            product.quantity += qty
            product.purchase_price = cost  # keep latest cost price

            total_amount += qty * cost
            line_count += 1

        if line_count == 0:
            db.session.rollback()
            flash("No valid product line items were submitted.", "danger")
            return render_template("purchase_form.html", suppliers=supplier_list,
                                    products=product_list, today=datetime.utcnow().date().isoformat())

        purchase.total_amount = round(total_amount, 2)
        db.session.commit()
        flash(f"Purchase {purchase.invoice_number} recorded and stock updated.", "success")
        return redirect(url_for("main.purchase_view", purchase_id=purchase.id))

    return render_template("purchase_form.html", suppliers=supplier_list, products=product_list,
                            today=datetime.utcnow().date().isoformat())


@main_bp.route("/purchases/view/<int:purchase_id>")
@login_required
def purchase_view(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    return render_template("purchase_view.html", purchase=purchase)


@main_bp.route("/purchases/delete/<int:purchase_id>", methods=["POST"])
@login_required
def purchase_delete(purchase_id):
    """Deleting a purchase reverses its stock impact, then removes the record."""
    purchase = Purchase.query.get_or_404(purchase_id)
    for item in purchase.items:
        if item.product:
            item.product.quantity = max(0, item.product.quantity - item.quantity)
    db.session.delete(purchase)
    db.session.commit()
    flash(f"Purchase {purchase.invoice_number} deleted and stock reversed.", "info")
    return redirect(url_for("main.purchases"))


# --------------------------------------------------------------------------
# Stock
# --------------------------------------------------------------------------
@main_bp.route("/stock")
@login_required
def stock():
    threshold = current_app.config["LOW_STOCK_THRESHOLD"]
    search = request.args.get("q", "", type=str).strip()

    query = Product.query.filter_by(is_active=True)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Product.name.ilike(like), Product.product_code.ilike(like)))
    products_list = query.order_by(Product.quantity.asc()).all()

    history = (StockAdjustment.query.order_by(StockAdjustment.created_at.desc()).limit(25).all())

    form = StockAdjustmentForm()
    form.product_id.choices = [(p.id, f"{p.product_code} - {p.name}") for p in
                                Product.query.filter_by(is_active=True).order_by(Product.name).all()]

    return render_template("stock.html", products=products_list, threshold=threshold,
                            history=history, form=form, search=search)


@main_bp.route("/stock/adjust", methods=["POST"])
@login_required
def stock_adjust():
    form = StockAdjustmentForm()
    form.product_id.choices = [(p.id, p.name) for p in Product.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        product = Product.query.get_or_404(form.product_id.data)
        qty = form.quantity.data
        if form.change_type.data == "remove":
            if qty > product.quantity:
                flash(f"Cannot remove {qty} units - only {product.quantity} in stock.", "danger")
                return redirect(url_for("main.stock"))
            product.quantity -= qty
            change = -qty
        else:
            product.quantity += qty
            change = qty

        adjustment = StockAdjustment(
            product_id=product.id, change=change, reason=form.reason.data or "Manual adjustment",
            adjusted_by=current_user.username
        )
        db.session.add(adjustment)
        db.session.commit()
        flash(f"Stock for '{product.name}' adjusted successfully.", "success")
    else:
        flash("Please correct the errors and try again.", "danger")
    return redirect(url_for("main.stock"))


# --------------------------------------------------------------------------
# Reports
# --------------------------------------------------------------------------
@main_bp.route("/reports")
@login_required
def reports():
    return render_template("reports.html")


def _csv_response(rows, headers, filename):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name=filename)


def _pdf_response(title, headers, rows, filename):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    elements = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    data = [headers] + [[str(c) for c in row] for row in rows]
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
    doc.build(elements)
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name=filename)


@main_bp.route("/reports/products/<fmt>")
@login_required
def report_products(fmt):
    items = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    headers = ["Code", "Name", "Category", "Brand", "Purchase Price", "Selling Price", "Quantity", "Stock Value"]
    rows = [[p.product_code, p.name, p.category.name if p.category else "-", p.brand or "-",
             p.purchase_price, p.selling_price, p.quantity, p.stock_value] for p in items]
    if fmt == "pdf":
        return _pdf_response("Product Report", headers, rows, "product_report.pdf")
    return _csv_response(rows, headers, "product_report.csv")


@main_bp.route("/reports/purchases/<fmt>")
@login_required
def report_purchases(fmt):
    items = Purchase.query.order_by(Purchase.purchase_date.desc()).all()
    headers = ["Invoice No", "Date", "Supplier", "Items", "Total Amount"]
    rows = [[p.invoice_number, p.purchase_date.isoformat(), p.supplier.name,
             len(p.items), p.total_amount] for p in items]
    if fmt == "pdf":
        return _pdf_response("Purchase Report", headers, rows, "purchase_report.pdf")
    return _csv_response(rows, headers, "purchase_report.csv")


@main_bp.route("/reports/suppliers/<fmt>")
@login_required
def report_suppliers(fmt):
    items = Supplier.query.order_by(Supplier.name).all()
    headers = ["Name", "Company", "Phone", "Email", "GST Number", "Total Purchases"]
    rows = [[s.name, s.company or "-", s.phone or "-", s.email or "-",
             s.gst_number or "-", len(s.purchases)] for s in items]
    if fmt == "pdf":
        return _pdf_response("Supplier Report", headers, rows, "supplier_report.pdf")
    return _csv_response(rows, headers, "supplier_report.csv")


@main_bp.route("/reports/low-stock/<fmt>")
@login_required
def report_low_stock(fmt):
    threshold = current_app.config["LOW_STOCK_THRESHOLD"]
    items = Product.query.filter(Product.is_active == True, Product.quantity <= threshold).order_by(  # noqa: E712
        Product.quantity.asc()).all()
    headers = ["Code", "Name", "Category", "Quantity", "Status"]
    rows = [[p.product_code, p.name, p.category.name if p.category else "-", p.quantity,
             "OUT OF STOCK" if p.quantity <= 0 else "LOW STOCK"] for p in items]
    if fmt == "pdf":
        return _pdf_response("Low Stock Report", headers, rows, "low_stock_report.pdf")
    return _csv_response(rows, headers, "low_stock_report.csv")


@main_bp.route("/reports/stock-summary/<fmt>")
@login_required
def report_stock_summary(fmt):
    items = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    headers = ["Code", "Name", "Quantity", "Purchase Price", "Selling Price", "Stock Value", "Potential Profit"]
    rows = [[p.product_code, p.name, p.quantity, p.purchase_price, p.selling_price,
             p.stock_value, round((p.selling_price - p.purchase_price) * p.quantity, 2)] for p in items]
    if fmt == "pdf":
        return _pdf_response("Stock Summary Report", headers, rows, "stock_summary_report.pdf")
    return _csv_response(rows, headers, "stock_summary_report.csv")


# --------------------------------------------------------------------------
# Error handlers
# --------------------------------------------------------------------------
@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@main_bp.app_errorhandler(413)
def too_large(e):
    flash("Uploaded file is too large. Maximum size is 5MB.", "danger")
    return redirect(request.referrer or url_for("main.dashboard"))
