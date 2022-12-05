from Models.BaseModel import BaseModel
from Models.SessionModel import SessionModel
from FileManagement.FileManagement import FileManagement
from config import db


class ImageModel(db.Model, BaseModel):
    __tablename__ = "images"
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    filepath = db.Column(db.VARCHAR(8128), nullable=False)
    image_type = db.Column(db.INTEGER, nullable=False)

    @staticmethod
    def deleteOne(image_id):
        image = ImageModel.getOne(image_id)
        if image:
            FileManagement.removeFile(image.filepath)
            image.delete()

    @staticmethod
    def getOne(image_id):
        return ImageModel.query.filter_by(id=image_id).first()

    @staticmethod
    def getData(image_id):
        image = ImageModel.getOne(image_id)
        image_bytes = b''
        if image:
            image_bytes = FileManagement.loadImage(image.filepath)
        return image_bytes

    @staticmethod
    def getMany(session_id, image_types: list, union=True):
        current_session: SessionModel = db.session.query(SessionModel).filter_by(id=session_id).first()
        images = []

        if current_session:
            images = current_session.images
            final_image_type = 0 if union else 1
            for image_type in image_types:
                final_image_type = (final_image_type | image_type) if union else (final_image_type & image_type)
            images = images.filter(ImageModel.image_type.op('&')(final_image_type))
            images = images.all()

        return list(images)

    @staticmethod
    def deleteMany(session_id, image_types: list, union=True):
        images = ImageModel.getMany(session_id, image_types, union)
        for image in images:
            ImageModel.deleteOne(image.id)
