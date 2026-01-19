from ext import db
from flask_login  import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price_daily = db.Column(db.Integer, default=100)
    price_hourly = db.Column(db.Integer, default=20)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    date = db.Column(db.DateTime, default=db.func.now())
    duration_type = db.Column(db.String(20), default="დღიური")
    user = db.relationship('User', backref='bookings')
    car = db.relationship('Car', backref='bookings')

    # useris damanqanis kavshiri es
    user = db.relationship('User', backref='bookings')
    car = db.relationship('Car', backref='bookings')