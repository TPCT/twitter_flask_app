from Models.AccountModel import AccountModel
from Models.SessionModel import SessionModel
from Models.ProxyModel import ProxyModel
from API.AccountSearch import AccountSearch
from Database.DatabaseWorker import DatabaseThread
from concurrent.futures import ThreadPoolExecutor
from Workers.BaseWorker import BaseWorker
from Constants.AccountTypes import AccountTypes
from Constants.ProxyTypes import ProxyTypes
import random
from config import db


class CheckerWorker(BaseWorker):
    def __init__(self, user_id, session_id, accounts_list, *args, **kwargs):
        super(CheckerWorker, self).__init__(user_id, session_id, *args, **kwargs)
        self.accounts_list = accounts_list
        self.checker = None

    def validatorThread(self, username,
                        password=None, email=None,
                        proxy_user=None, proxy_password=None,
                        proxy_ip=None, proxy_port=None,
                        *args):

        with self.app.app_context():
            try:
                checked = self.checker.checkAccount(username)
                if not checked:
                    self.checker = AccountSearch()
                    return self.validatorThread(username, password, email, proxy_user,
                                                proxy_password, proxy_ip, proxy_port)

                DatabaseThread.updateOrCreate(AccountModel,
                                              selector={
                                                  'session_id': self._session_id,
                                                  'username': username
                                              }, data=dict(session_id=self._session_id,
                                                           username=username,
                                                           password=password,
                                                           email=email,
                                                           proxy_user=proxy_user,
                                                           proxy_password=proxy_password,
                                                           proxy_ip=proxy_ip,
                                                           proxy_port=proxy_port,
                                                           account_type=AccountTypes.checker,
                                                           **checked)
                                              )
            except Exception as e:
                pass

    def operation(self):
        with self.app.app_context():
            session = db.session.query(SessionModel).filter_by(id=self._session_id).first()
            proxies = ProxyModel.getMany(session.id, [ProxyTypes.checker], {'active': True})

            with ThreadPoolExecutor(20) as executor:
                self.checker = AccountSearch()
                for account in self.accounts_list:
                    if self._terminate:
                        break

                    proxy = {}
                    if proxies:
                        proxy = random.choice(proxies).serialize

                    self._threads_pool.append(executor.submit(self.validatorThread, *(account[:3]),
                                                              proxy_user=proxy.get('proxy_user'),
                                                              proxy_password=proxy.get('proxy_password'),
                                                              proxy_ip=proxy.get('proxy_ip'),
                                                              proxy_port=proxy.get('proxy_port')))
