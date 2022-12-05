import hashlib
import pickle
from os import path, makedirs, unlink
from io import BytesIO
from FileManagement.SessionPaths import SessionPaths
from FileManagement.UserPaths import UserPaths
from Database.DatabaseWorker import DatabaseThread
from flask import current_app


class FileManagement:
    @staticmethod
    def saveImages(consumer_id, images, images_folder, image_types, **kwargs):
        images_folder = SessionPaths if images_folder == 'session' else UserPaths
        images_folders = []
        for image_type in image_types:
            images_folders.append(images_folder(current_app.root_path, consumer_id)['images'].get(image_type))
        if images_folders:
            FileManagement.saveFiles(images, images_folders, **kwargs)

    @staticmethod
    def loadImage(filepath):
        with open(filepath, 'rb') as image_reader:
            return image_reader.read()

    @staticmethod
    def saveTexts(consumer_id, texts, texts_folder, text_types, **kwargs):
        text_folder = SessionPaths if texts_folder == 'session' else UserPaths
        texts_folder = []
        for text_type in text_types:
            texts_folder.append(text_folder(current_app.root_path, consumer_id)['texts'].get(text_type))
        if texts_folder:
            FileManagement.saveFiles(texts, texts_folder, extension='.txt', **kwargs)

    @staticmethod
    def loadText(filepath):
        # with open(filepath, 'rb') as text_reader:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as text_reader:
            return text_reader.read()

    @staticmethod
    def saveAccount(account, obj):
        accounts_folder = SessionPaths(current_app.root_path, account.session_id)['binary']['accounts']
        makedirs(accounts_folder, exist_ok=True)
        filebytes = pickle.dumps(obj)
        filepath = account.filepath if account.filepath else FileManagement.generatePath(accounts_folder,
                                                                                         filebytes, '.bin')
        FileManagement.saveFile(filepath, filebytes)
        return filepath

    @staticmethod
    def loadAccount(filepath):
        try:
            with open(filepath, 'rb') as account_wrapper_reader:
                return pickle.load(account_wrapper_reader)
        except:
            return None

    @staticmethod
    def generatePath(filepath, filebytes, extension=''):
        return path.join(filepath, f"{hashlib.sha1(filebytes).hexdigest()}{extension}")

    @staticmethod
    def saveFiles(files, paths, **kwargs):
        for file in files:
            for folder_path in paths:
                makedirs(folder_path, exist_ok=True)

                file.seek(0)
                file_bytes = file.read()
                if file_bytes:
                    file_path = FileManagement.generatePath(folder_path, file_bytes, kwargs.get('extension', ''))

                    FileManagement.saveFile(file_path, file_bytes)
                    FileManagement.updateFilePath(file_path, kwargs.get('model'),
                                                  kwargs.get('data', {}), kwargs.get('selector', {}))

    @staticmethod
    def updateFilePath(filepath, model, data, selector=None):
        if all([model, data]):
            data.update({'filepath': filepath})
            DatabaseThread.insert(model, **data) if not selector \
                else DatabaseThread.updateOrCreate(model, selector=selector, data=data)

    @staticmethod
    def saveFile(filepath, filebytes):
        makedirs(path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb+') as file_writer:
            file_writer.write(filebytes)

    @staticmethod
    def splitAndSave(consumer_id, stream, folder, file_for, **kwargs):
        files = []
        for i in range(0, len(stream)):
            text = stream[i].strip()
            if not text:
                continue
            files.append(BytesIO(text.encode('utf-8')))
        FileManagement.saveTexts(consumer_id, files, folder, file_for, **kwargs)

    @staticmethod
    def removeFiles(model_items):
        for item in model_items:
            FileManagement.removeFile(item.filepath)

    @staticmethod
    def removeFile(filepath):
        unlink(filepath) if filepath and path.exists(filepath) else None
