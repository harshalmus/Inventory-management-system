"""
WTForms form definitions - provides server-side validation + CSRF protection
for all data-entry forms in the app.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, FloatField, IntegerField,
    TextAreaField, SelectField, DateField, BooleanField
)
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=255)])


class SupplierForm(FlaskForm):
    name = StringField("Contact Name", validators=[DataRequired(), Length(max=120)])
    company = StringField("Company Name", validators=[Optional(), Length(max=150)])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=30)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    address = TextAreaField("Address", validators=[Optional(), Length(max=255)])
    gst_number = StringField("GST Number", validators=[Optional(), Length(max=30)])


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(max=150)])
    category_id = SelectField("Category", coerce=int, validators=[Optional()])
    brand = StringField("Brand", validators=[Optional(), Length(max=100)])
    purchase_price = FloatField("Unit / Purchase Price", validators=[DataRequired(), NumberRange(min=0)])
    selling_price = FloatField("Selling Price", validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField("Description", validators=[Optional()])
    image = FileField("Product Image", validators=[
        Optional(), FileAllowed(["jpg", "jpeg", "png", "gif", "webp"], "Images only!")
    ])


class StockAdjustmentForm(FlaskForm):
    product_id = SelectField("Product", coerce=int, validators=[DataRequired()])
    change_type = SelectField("Type", choices=[("add", "Add Stock"), ("remove", "Remove Stock")])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    reason = StringField("Reason", validators=[Optional(), Length(max=255)])
