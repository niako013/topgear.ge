from flask import Flask, render_template, redirect, url_for, flash, request
from ext import db, login_manager
from models import Car, User, Booking
from forms import RegisterForm, LoginForm, CarForm
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# კონფიგურაცია
app.config["SECRET_KEY"] = "top_gear_secret_123"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "instance", "ultimate_db.db")

# ბაზის და ლოგინის ინიციალიზაცია
db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- მთავარი გვერდი ---
@app.route("/")
def index():
    return render_template("index.html")


# --- კატალოგი ---
@app.route("/cars")
def cars():
    all_cars = Car.query.all()
    return render_template("cars.html", cars=all_cars)


# --- მანქანის დეტალები ---
@app.route("/car/<int:car_id>")
def car_detail(car_id):
    car = Car.query.get_or_404(car_id)
    return render_template("car_detail.html", car=car)


# --- ავტორიზაცია ---
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for("index"))
        flash("მომხმარებლის სახელი ან პაროლი არასწორია!", "danger")
    return render_template("login.html", form=form)


# --- რეგისტრაცია ---
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("ეს სახელი უკვე დაკავებულია!", "danger")
            return render_template("register.html", form=form)

        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("რეგისტრაცია წარმატებით დასრულდა!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


# --- ადმინ პანელი (მანქანის დამატება ფოტოთი) ---
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_page():
    if not current_user.is_admin:
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე!", "danger")
        return redirect(url_for("index"))

    form = CarForm()
    if form.validate_on_submit():
        # ფოტოს შენახვა
        file = form.image.data
        filename = secure_filename(file.filename)
        # ვინახავთ static/images საქაღალდეში
        file.save(os.path.join(app.root_path, 'static', 'images', filename))

        new_car = Car(
            brand=form.brand.data,
            model=form.model.data,
            year=form.year.data,
            image=filename,
            description=form.description.data,
            price_daily=request.form.get('price_daily'),
            price_hourly=request.form.get('price_hourly')
        )
        db.session.add(new_car)
        db.session.commit()
        flash("მანქანა წარმატებით დაემატა!", "success")
        return redirect(url_for("cars"))

    bookings = Booking.query.all()
    return render_template("admin.html", form=form, bookings=bookings)


# --- მანქანის წაშლა ---
@app.route("/delete_car/<int:car_id>")
@login_required
def delete_car(car_id):
    if not current_user.is_admin:
        return redirect(url_for("index"))
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    flash("მანქანა წარმატებით წაიშალა!", "info")
    return redirect(url_for("cars"))


# --- დაჯავშნა ---
@app.route("/book/<int:car_id>/<string:type>")
@login_required
def book_car(car_id, type):
    car = Car.query.get_or_404(car_id)
    new_booking = Booking(user_id=current_user.id, car_id=car.id, duration_type=type)
    db.session.add(new_booking)
    db.session.commit()
    flash(f"ავტომობილი {car.brand} {car.model} დაჯავშნილია!", "success")
    return redirect(url_for("profile"))


# --- პროფილი ---
@app.route("/profile")
@login_required
def profile():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("profile.html", bookings=user_bookings)


# --- ჯავშნის გაუქმება ---
@app.route("/cancel_booking/<int:booking_id>")
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id == current_user.id or current_user.is_admin:
        db.session.delete(booking)
        db.session.commit()
        flash("ჯავშანი გაუქმებულია.", "info")
    return redirect(url_for("profile"))


# --- გასვლა ---
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


# --- კონტაქტი ---
@app.route("/contact")
def contact():
    return render_template("contact.html")


# --- ბაზის ინიციალიზაცია და ადმინის შექმნა ---
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username="topgeargeorgia.admin").first()
    if not admin:
        admin = User(username="topgeargeorgia.admin", password="lewishamilton8timewdc", is_admin=True)
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
