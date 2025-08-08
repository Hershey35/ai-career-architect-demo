from main import db,login_manager
from main import bcrypt
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    fullname = db.Column(db.String(length=30), nullable=False)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    # budget = db.Column(db.Integer(), nullable=False, default=1000)
    # items = db.relationship('Item', backref='owned_user', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)


    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self,plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self,attempted_password):
        return bcrypt.check_password_hash(self.password_hash,attempted_password)

class UploadedResume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(200),nullable=False)
    parsed_text = db.Column(db.Text,nullable=False)
    skills = db.Column(db.Text,nullable=True)
    education = db.Column(db.Text,nullable=True)
    experience = db.Column(db.Text,nullable=True)
    achievements = db.Column(db.Text,nullable=True)
    upload_timestamp = db.Column(db.DateTime,default=datetime.utcnow)