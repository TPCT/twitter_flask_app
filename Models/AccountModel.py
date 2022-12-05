from Models.SessionModel import SessionModel
from Models.BaseModel import BaseModel
from FileManagement.FileManagement import FileManagement
from Constants.AccountTypes import AccountTypes
from config import db


class AccountModel(db.Model, BaseModel):
    __tablename__ = "accounts"
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    username = db.Column(db.VARCHAR(255), nullable=False)
    password = db.Column(db.VARCHAR(255), nullable=True)
    email = db.Column(db.VARCHAR(255), nullable=True)
    account_id = db.Column(db.VARCHAR(255), default=0)
    proxy_user = db.Column(db.VARCHAR(255), nullable=True)
    proxy_password = db.Column(db.VARCHAR(255), nullable=True)
    proxy_ip = db.Column(db.VARCHAR(255), nullable=True)
    proxy_port = db.Column(db.VARCHAR(255), nullable=True)
    filepath = db.Column(db.VARCHAR(1024), nullable=True)
    active = db.Column(db.BOOLEAN, default=False)
    restricted = db.Column(db.BOOLEAN, default=False)
    suspended = db.Column(db.BOOLEAN, default=False)
    account_type = db.Column(db.Integer, default=0)
    follow_failed = db.Column(db.INTEGER, default=0)
    hidden = db.Column(db.BOOLEAN, default=False)

    def twitter_wrapper(self):
        return FileManagement.loadAccount(self.filepath)

    def saveHandler(self, twitter_wrapper):
        return FileManagement.saveAccount(self, twitter_wrapper)

    @staticmethod
    def deleteOne(account_id):
        account = AccountModel.getOne(account_id)
        if account:
            FileManagement.removeFile(account.filepath)
            account.delete()

    @staticmethod
    def getOne(account_id):
        return AccountModel.query.filter_by(id=account_id).first()

    @staticmethod
    def getMany(session_id, account_types: list, account_status: dict, union=True):
        current_session: SessionModel = db.session.query(SessionModel).filter_by(id=session_id).first()
        accounts = []

        if current_session:
            accounts = current_session.accounts.filter_by(**account_status) \
                if account_status else current_session.accounts
            final_account_type = 0 if union else 1
            for account_type in account_types:
                final_account_type = (final_account_type | account_type) \
                    if union else (final_account_type & account_type)
            accounts = accounts.filter(AccountModel.account_type.op('&')(final_account_type))
            accounts = accounts.all()

        return list(accounts)

    @staticmethod
    def getAll(session_id, account_status: dict):
        current_session: SessionModel = db.session.query(SessionModel).filter_by(id=session_id).first()
        accounts = []

        if current_session:
            accounts = current_session.accounts.filter_by(**account_status) \
                if account_status else current_session.accounts
            accounts = accounts.all()

        return list(accounts)

    def getAccountPermissions(self):
        account_permissions = []
        for name, permission in AccountTypes.PERMISSIONS.items():
            if permission & self.account_type:
                account_permissions.append(name)
        return ','.join(account_permissions)

    @staticmethod
    def deleteMany(session_id, account_types: list, account_status: dict, union=True):
        accounts = AccountModel.getMany(session_id, account_types, account_status, union)
        for account in accounts:
            AccountModel.deleteOne(account.id)

    @staticmethod
    def loadAccount(account_id):
        account = AccountModel.query.filter_by(id=account_id).first()
        return FileManagement.loadAccount(account.filepath)