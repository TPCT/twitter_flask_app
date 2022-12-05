from Models.BaseModel import BaseModel
from Models.SessionModel import SessionModel
from config import db
from FileManagement.FileManagement import FileManagement


class TextModel(db.Model, BaseModel):
    __tablename__ = "texts"
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    filepath = db.Column(db.VARCHAR(8128), nullable=False)
    text_type = db.Column(db.INTEGER, nullable=False)

    @staticmethod
    def deleteOne(text_id):
        text = TextModel.getOne(text_id)
        if text:
            FileManagement.removeFile(text.filepath)
            text.delete()

    @staticmethod
    def getOne(text_id):
        return TextModel.query.filter_by(id=text_id).first()

    @staticmethod
    def getData(text_id):
        text = TextModel.getOne(text_id)
        text_bytes = b''
        if text:
            text_bytes = FileManagement.loadText(text.filepath)
        return text_bytes

    @staticmethod
    def getMany(session_id, text_types: list, union=True):
        current_session: SessionModel = db.session.query(SessionModel).filter_by(id=session_id).first()
        texts = []

        if current_session:
            texts = current_session.texts
            final_text_type = 0 if union else 1
            for text_type in text_types:
                final_text_type = (final_text_type | text_type) if union else (final_text_type & text_type)
            texts = texts.filter(TextModel.text_type.op('&')(final_text_type))
            texts = texts.all()

        return list(texts)

    @staticmethod
    def deleteMany(session_id, text_types: list, union=True):
        texts = TextModel.getMany(session_id, text_types, union)
        for text in texts:
            TextModel.deleteOne(text.id)
