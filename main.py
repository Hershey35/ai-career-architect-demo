from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

# SQLite DB path
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'ai_career.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '962d1b3c5fe0e373ab0c59c6'

db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

# Import routes and models AFTER db is defined
from routes import *
from models import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✔ Tables created.")
    app.run(debug=True)