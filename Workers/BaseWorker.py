from flask import current_app
from config import threads_pool
from Database.DatabaseWorker import DatabaseThread
from Models.SessionModel import SessionModel
from multiprocessing import Process
from threading import Thread


class BaseWorker(Thread):
    # manager = Manager()
    # app = current_app.test_request_context()

    def __init__(self, user_id, session_id, *args, **kwargs):
        super(BaseWorker, self).__init__(daemon=True, *args, **kwargs)
        self.app = current_app._get_current_object()
        self._terminate = False
        self._completed = False
        self._user_id = user_id
        self._session_id = session_id
        self._threads_pool = []

        if not threads_pool.get(user_id):
            threads_pool[user_id] = {}
        if not threads_pool.get(user_id, {}).get(session_id):
            threads_pool[user_id][session_id] = {}
        threads_pool[user_id][session_id][self.__class__.__name__] = self
        self._process = None

    @property
    def completed(self):
        return self._completed

    def complete(self):
        if not self._completed:
            self._completed = True
            del threads_pool[self._user_id][self._session_id][self.__class__.__name__]
        DatabaseThread.update(SessionModel, id=self._session_id, user_id=self._user_id, completed=True, active=False)

    def terminate(self):
        if not self._terminate:
            self._terminate = True
            del threads_pool[self._user_id][self._session_id][self.__class__.__name__]
            DatabaseThread.update(SessionModel, id=self._session_id, user_id=self._user_id, completed=False,
                                  active=False)

            for thread in self._threads_pool:
                thread.cancel()
                continue

    def operation(self):
       ...

    def __operation(self):
        if self._terminate:
            return None

        with self.app.app_context():
            self.operation()

        if not self._terminate:
            self.complete()

    def run(self):
        process = Process(target=self.__operation(), name=self.__class__.__name__, daemon=True)
        self._threads_pool.append(process)
        process.start
