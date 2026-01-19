from flask import Flask, render_template, redirect, url_for, request, flash
from ext import db, login_manager
from models import Car, User, Booking
from forms import RegisterForm, LoginForm, CarForm
from flask_login import login_user, logout_user, login_required, current_user
import os

app = Flask (__name__)

# 1. კონფიგურაცია
app.config["SECRET_KEY"] = "top_gear_secret_key_123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new_topgear.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 2. ინსტრუმენტების დაკავშირება
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- როუტები ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cars")
def cars():
    all_cars = Car.query.all()
    return render_template("cars.html", cars=all_cars)


@app.route("/car/<int:car_id>")
def car_detail(car_id):
    car = Car.query.get_or_404(car_id)
    return render_template("car_detail.html", car=car)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for("index"))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/profile")
@login_required
def profile():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("profile.html", bookings=user_bookings)


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ადმინ პანელი
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_page():
    if not current_user.is_admin:
        return redirect(url_for("index"))

    form = CarForm()
    if form.validate_on_submit():
        new_car = Car(
            name=form.name.data,
            brand=form.brand.data,
            model=form.model.data,
            year=form.year.data,
            price_daily=form.price_daily.data,
            price_hourly=form.price_hourly.data,
            description=form.description.data,
            image=form.image.data
        )
        db.session.add(new_car)
        db.session.commit()
        return redirect(url_for("cars"))

    bookings = Booking.query.all()
    return render_template("admin.html", form=form, bookings=bookings)


# ბაზის შექმნა
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)