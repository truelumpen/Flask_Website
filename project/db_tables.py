from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapper

from project import db, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_on': type
    }


class Seller(User):
    id = db.Column(db.Integer, ForeignKey('user.id'), primary_key=True)
    email = db.Column(db.String(25), unique=True, nullable=False)
    fname = db.Column(db.String(25), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fil_name = db.Column(db.String(25), unique=True, nullable=False)
    inn = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    trades = db.Column(db.Integer, default=0)

    autos = relationship("Auto", back_populates="seller")

    __mapper_args__ = {
        'polymorphic_identity': 'seller'
    }

    def __init__(self, fil_name, inn, image, address, trades, email, password, fname, lname):
        self.email = email
        self.password = password
        self.fname = fname
        self.lname = lname
        self.image = image
        self.fil_name = fil_name
        self.inn = inn
        self.address = address
        self.trades = trades


class Customer(User):
    id = db.Column(db.Integer, ForeignKey('user.id'), primary_key=True)
    email = db.Column(db.String(25), unique=True, nullable=False)
    fname = db.Column(db.String(25), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    sign = db.Column(db.Boolean, nullable=False)
    com_name = db.Column(db.String(25), nullable=True)

    contract = relationship("Contract", back_populates="customers")
    order = relationship("Order", back_populates="customers")

    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }

    def __init__(self, email, password, sign, com_name, fname, lname):
        self.email = email
        self.password = password
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = password
        self.sign = sign
        self.com_name = com_name
        self.fname = fname
        self.lname = lname



class Auto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    brand = db.Column(db.String(25), nullable=False)
    model = db.Column(db.String(25), nullable=False)
    distance = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    sold = db.Column(db.Boolean, nullable=False, default=False)
    fil_id = db.Column(db.Integer, ForeignKey('seller.id'))

    seller = relationship("Seller", back_populates="autos")
    contract = relationship("Contract", back_populates="cars")

    def __init__(self, price, brand, model, distance, image, sold, fil_id):
        self.price = price
        self.brand = brand
        self.model = model
        self.distance = distance
        self.fil_id = fil_id
        self.sold = sold
        self.image = image


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    document = db.Column(db.String, nullable=False)
    car_id = db.Column(db.Integer, ForeignKey('auto.id'))
    customer_id = db.Column(db.Integer, ForeignKey('customer.id'))

    cars = relationship("Auto", back_populates="contract")
    customers = relationship("Customer", back_populates="contract")

    def __init__(self, date, document, car_id, customer_id):
        self.date = date
        self.document = document
        self.car_id = car_id
        self.customer_id = customer_id



class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(25), nullable=False)
    gear = db.Column(db.String(25), nullable=False)
    helm = db.Column(db.String(25), nullable=False)
    power = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(25), nullable=False)
    time = db.Column(db.String(25), nullable=False)
    date = db.Column(db.Date, nullable=False)
    document = db.Column(db.String(25), nullable=False)
    price = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, ForeignKey('customer.id'))

    customers = relationship("Customer", back_populates="order")

    def __init__(self, model, gear, price, helm, power, color, time, date, document, customer_id):
        self.gear = gear
        self.helm = helm
        self.price = price
        self.model = model
        self.power = power
        self.color = color
        self.time = time
        self.date = date
        self.document = document
        self.customer_id = customer_id



@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


db.create_all()