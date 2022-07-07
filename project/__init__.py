import lxml

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from cloudipsp import Api, Checkout


app = Flask(__name__)
app.secret_key = 'very secret key please dont hack me t i g r a n e s h a c k'
SQLALCHEMY_TRACK_MODIFICATIONS = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ['PNG', 'JPG', 'JPEG']
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
db.init_app(app)
api = Api(merchant_id=1396424,
          secret_key='test')
checkout = Checkout(api=api)
data = {
    "currency": "RUB",
    "amount": 0
}


from project.routes import *
from project.db_tables import *
