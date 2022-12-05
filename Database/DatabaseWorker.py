from flask import current_app
from config import db
# from process_config import process_lock
# from multiprocessing import Process, Queue
from threading import Thread
from queue import Queue

operations_queue = Queue()


class DatabaseThread(Thread):
    def __init__(self, *args, **kwargs):
        super(DatabaseThread, self).__init__(daemon=True, *args, **kwargs)
        self.app = current_app._get_current_object()

    @staticmethod
    def insert(model, **kwargs):
        operations_queue.put(('insert', model, kwargs))

    @staticmethod
    def delete(model, **kwargs):
        operations_queue.put(('delete', model, kwargs))

    @staticmethod
    def update(model, **kwargs):
        operations_queue.put(('update', model, kwargs))

    @staticmethod
    def updateOrCreate(model, **kwargs):
        operations_queue.put(('updateOrCreate', model, kwargs))

    def run(self):
        with self.app.app_context():
            while True:
                try:
                    next_request = operations_queue.get()
                    # with process_lock:
                    action = next_request[0]
                    model = next_request[1]
                    kwargs = next_request[2]

                    if action == 'delete':
                        db.session.query(model).filter_by(**kwargs).delete(synchronize_session='fetch')

                    if action == 'update':
                        db.session.flush()
                        assign_model = model(**kwargs)
                        db.session.merge(assign_model)

                    if action == 'insert':
                        assign_model = model(**kwargs)
                        db.session.add(assign_model)

                    if action == 'updateOrCreate':
                        model_data = db.session.query(model).filter_by(**kwargs.get('selector')).first()
                        if model_data:
                            db.session.flush()
                            assign_model = model(id=model_data.id, **kwargs.get('data'))
                            db.session.merge(assign_model)
                        else:
                            assign_model = model(**kwargs.get('data'))
                            db.session.add(assign_model)

                    db.session.flush()
                    db.session.commit()
                    db.session.close()
                except Exception as e:
                    db.session.rollback()
