from Models.BaseModel import BaseModel
from Models.UserModel import UserModel
from config import db
from FileManagement.FileManagement import FileManagement
from Constants.FileTypes import FileTypes


class StorageModel(db.Model, BaseModel):
    __tablename__ = "storages"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    filepath = db.Column(db.VARCHAR(8128), nullable=True)
    text_arabic = db.Column(db.BOOLEAN, default=False)
    file_type = db.Column(db.INTEGER, nullable=False)
    file_for = db.Column(db.INTEGER, nullable=False)

    @staticmethod
    def deleteOne(storage_id):
        storage = StorageModel.getOne(storage_id)
        if storage:
            FileManagement.removeFile(storage.filepath)
            storage.delete()

    @staticmethod
    def getOne(storage_id):
        return db.session.query(StorageModel).filter_by(id=storage_id).first()

    @staticmethod
    def getData(storage_id):
        storage = StorageModel.getOne(storage_id)
        storage_bytes = b''
        if storage:
            storage_bytes = FileManagement.loadText(storage.filepath) \
                if int(storage.file_type) == int(FileTypes.text) else FileManagement.loadImage(storage.filepath)
        return storage_bytes

    @staticmethod
    def getMany(user_id, storage_type, storage_for: list, text_arabic=None, union=True):
        storages = db.session.query(StorageModel).filter_by(user_id=user_id, file_type=storage_type)
        if storages:
            if text_arabic is not None:
                storages = storages.filter_by(text_arabic=text_arabic)

            final_permissions = 0 if union else 0

            for permission in storage_for:
                final_permissions = (final_permissions | permission) if union else (final_permissions & permission)

            storages = storages.filter(StorageModel.file_for.op('&')(final_permissions))
            storages = storages.all()

        return list(storages) if storages else []

    @staticmethod
    def deleteMany(user_id, storage_type, storage_for: list, text_arabic, union=True):
        storages = StorageModel.getMany(user_id, storage_type, storage_for, text_arabic, union)
        for storage in storages:
            StorageModel.deleteOne(storage.id)
