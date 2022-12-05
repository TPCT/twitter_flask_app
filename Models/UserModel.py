from Models.BaseModel import BaseModel
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from config import db, login


class UserModel(UserMixin, db.Model, BaseModel):
    __tablename__ = "users"
    username = db.Column(db.VARCHAR(255), unique=True)
    _password = db.Column(db.VARCHAR(255))
    is_admin = db.Column(db.BOOLEAN, default=False)

    sessions = db.relationship('SessionModel', lazy='dynamic', backref=db.backref(__tablename__), passive_deletes=True)
    storage = db.relationship('StorageModel', lazy='dynamic', backref=db.backref(__tablename__), passive_deletes=True)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plain_text):
        self._password = generate_password_hash(plain_text)

    def verifyPassword(self, plain_text):
        return check_password_hash(self.password, plain_text)


@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))
