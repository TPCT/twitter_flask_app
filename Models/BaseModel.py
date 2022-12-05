from sqlalchemy.sql import func
from config import db


class BaseModel:
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def serialize(self):
        return self.__dict__

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self, *args):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def deleteOne(*args, **kwargs):
        ...

    @staticmethod
    def getOne(*args, **kwargs):
        ...

    @staticmethod
    def getMany(*args, **kwargs):
        ...

    @staticmethod
    def deleteMany(*args, **kwargs):
        ...
