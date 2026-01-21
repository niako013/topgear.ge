from flask import Flask, render_template, redirect, url_for, request, flash
from ext import db, login_manager
from models import Car, User, Booking
from forms import RegisterForm, LoginForm, CarForm
from flask_login import login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)

# 1. კონფიგურაცია
app.config["SECRET_KEY"] = "top_gear_secret_key_123"
# Render-ისთვის SQLite-ის გზის დაზუსტება
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "new_topgear.db")
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
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("ეს სახელი უკვე დაკავებულია", "danger")
            return render_template("register.html", form=form)

        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("რეგისტრაცია წარმატებით დასრულდა!", "success")
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
        else:
            flash("არასწორი სახელი ან პაროლი", "danger")
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


@app.route("/book/<int:car_id>/<string:type>")
@login_required
def book_car(car_id, type):
    car = Car.query.get_or_404(car_id)
    booking_type_ge = "საათობრივი" if type == "hourly" else "დღიური"

    new_booking = Booking(
        user_id=current_user.id,
        car_id=car.id,
        duration_type=booking_type_ge
    )

    db.session.add(new_booking)
    db.session.commit()

    flash(f"ავტომობილი {car.brand} {car.model} ({booking_type_ge}) დაჯავშნილია!", "success")
    return redirect(url_for("profile"))


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_page():
    if not current_user.is_admin:
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე", "danger")
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
        flash("მანქანა წარმატებით დაემატა!", "success")
        return redirect(url_for("cars"))

    bookings = Booking.query.all()
    return render_template("admin.html", form=form, bookings=bookings)


# ბაზის შექმნა და ადმინის ავტომატური დამატება
with app.app_context():
    db.create_all()
    # ვამოწმებთ არსებობს თუ არა ადმინი
    admin_user = User.query.filter_by(username="topgeargeorgia.admin").first()
    if not admin_user:
        new_admin = User(
            username="topgeargeorgia.admin",
            password="lewishamilton8timewdc",
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)