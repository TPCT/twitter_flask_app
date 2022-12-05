from Models.BaseModel import BaseModel
from Models.SettingsModel import SettingsModel
from Models.StatusModel import StatusModel
from config import db
from FileManagement.FileManagement import FileManagement


class SessionModel(db.Model, BaseModel):
    __tablename__ = "sessions"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.TEXT(256), nullable=False)
    active = db.Column(db.BOOLEAN, default=False)
    completed = db.Column(db.BOOLEAN, default=False)
    selected = db.Column(db.BOOLEAN, default=False)

    accounts = db.relationship('AccountModel', lazy='dynamic', backref=db.backref(__tablename__), passive_deletes=True)
    status = db.relationship('StatusModel', lazy='dynamic', backref=db.backref(__tablename__), passive_deletes=True)
    settings = db.relationship('SettingsModel', lazy='dynamic', backref=db.backref(__tablename__), passive_deletes=True)
    proxies = db.relationship('ProxyModel', lazy='dynamic', backref=db.backref(__tablename__), passive_deletes=True)

    texts = db.relationship('TextModel', lazy='dynamic', backref=db.backref(__tablename__),
                            passive_deletes=True)
    images = db.relationship('ImageModel', lazy='dynamic', backref=db.backref(__tablename__),
                             passive_deletes=True)

    def delete(self):
        FileManagement.removeFiles(self.accounts.all())
        FileManagement.removeFiles(self.texts.all())
        FileManagement.removeFiles(self.images.all())

        self.accounts.delete(synchronize_session='fetch')
        self.texts.delete(synchronize_session='fetch')
        self.images.delete(synchronize_session='fetch')
        self.proxies.delete(synchronize_session='fetch')
        self.settings.delete(synchronize_session='fetch')
        self.status.delete(synchronize_session='fetch')

        db.session.delete(self)
        db.session.commit()
        db.session.close()

    @staticmethod
    def getOne(session_id):
        return SessionModel.query.filter_by(id=session_id).first()

    @staticmethod
    def activate(session_id):
        current_session = SessionModel.getOne(session_id)
        current_session.selected = True
        db.session.commit()
        return current_session

    @staticmethod
    def deactivate(session):
        if session:
            session.selected = False
        db.session.flush()
        db.session.commit()

    def save(self):
        super(SessionModel, self).save()
        SettingsModel(session_id=self.id).save()
        StatusModel(session_id=self.id).save()
