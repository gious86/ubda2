from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_sock import Sock

hostname = 'http://192.168.1.101:5000'

DB_NAME = "database.db"

db = SQLAlchemy()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'huP_*jsh!2jQ#hdj4$$#ahskAKDjfks798KljPo457/%2DGkj^&shk@#jdhjs'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

sock = Sock(app)


db.init_app(app)


from .views import views
from .auth import auth
from .access import access

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(access, url_prefix='/')

#from .device_server import deviceServer
#app.register_blueprint(deviceServer)###

from .models import User

with app.app_context():
    db.create_all()
    print('Created Database!')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

