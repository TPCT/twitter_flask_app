import random
from Workers.BaseWorker import BaseWorker
from Database.DatabaseWorker import DatabaseThread
from Models.AccountModel import AccountModel
from Models.SessionModel import SessionModel
from Models.ProxyModel import ProxyModel
from API.TwitterAccount import TwitterAccount
from concurrent.futures import ThreadPoolExecutor, CancelledError
from config import db
# from process_config import process_lock
from Constants.ProxyTypes import ProxyTypes


class AccountValidationWorker(BaseWorker):
    def __init__(self, user_id, session_id, accounts_list, *args, **kwargs):
        super(AccountValidationWorker, self).__init__(user_id, session_id, *args, **kwargs)
        self.account_list = accounts_list
        self.proxies = []

    def validatorThread(self, account_model):
        try:
            with self.app.app_context():
                account: AccountModel = AccountModel.query.filter_by(username=account_model.username).first()
                twitter_wrapper = None
                if account:
                    twitter_wrapper = account.twitter_wrapper()
                    logged = twitter_wrapper.logged if twitter_wrapper else None
                    account_model.filepath = account.filepath

                if not twitter_wrapper or not account or not account.filepath:
                    twitter_wrapper = TwitterAccount()
                    logged = twitter_wrapper.Login(account_model.username, account_model.password, account_model.email,
                                                   account_model.proxy_user, account_model.proxy_password,
                                                   account_model.proxy_ip, account_model.proxy_port)

                if twitter_wrapper and twitter_wrapper.errors() != 'PROXY':
                    filepath = account_model.saveHandler(twitter_wrapper)
                    DatabaseThread.updateOrCreate(AccountModel,
                                                  selector={
                                                      'username': account_model.username,
                                                      'session_id': self._session_id
                                                  },
                                                  data=dict(
                                                      session_id=self._session_id,
                                                      username=account_model.username,
                                                      password=account_model.password,
                                                      email=account_model.email,
                                                      account_type=account_model.account_type,
                                                      proxy_user=account_model.proxy_user,
                                                      proxy_password=account_model.proxy_password,
                                                      proxy_ip=account_model.proxy_ip,
                                                      proxy_port=account_model.proxy_port,
                                                      active=logged,
                                                      suspended=not logged,
                                                      account_id=twitter_wrapper.getAccountInfo().get('user_id', 0),
                                                      filepath=filepath
                                                  ))

                return twitter_wrapper.errors(), account_model
        except Exception as e:
            return "Proxy", account_model

    def operation(self):
        with self.app.app_context():
            for i in range(5):
                if not self.account_list:
                    break

                session = db.session.query(SessionModel).filter_by(id=self._session_id).first()
                self.proxies = session.proxies.filter_by(proxy_for=ProxyTypes.account, active=True).all()

                with ThreadPoolExecutor(50) as executor:
                    for account in self.account_list:
                        if not account:
                            continue

                        if self._terminate:
                            break

                        account_type, *account_credentials, = account[:4]
                        account_model = AccountModel(session_id=self._session_id,
                                                     username=account_credentials[0],
                                                     password=account_credentials[1],
                                                     email=account_credentials[2],
                                                     account_type=account_type)
                        proxy = None

                        if len(account) == 8:
                            account_model.proxy_ip = account[-4]
                            account_model.proxy_port = account[-3]
                            account_model.proxy_user = account[-2]
                            account_model.proxy_password = account[-1]

                        if not all([account_model.proxy_user, account_model.proxy_password,
                                   account_model.proxy_port, account_model.proxy_ip]) and self.proxies:
                            proxy: ProxyModel = random.choice(self.proxies)
                            account_model.proxy_ip = proxy.proxy_ip
                            account_model.proxy_port = proxy.proxy_port
                            account_model.proxy_user = proxy.proxy_user
                            account_model.proxy_password = proxy.proxy_password
                        # self.validatorThread(account_model)

                        self._threads_pool.append(executor.submit(self.validatorThread, account_model))

                self.account_list = []

                for thread in self._threads_pool:
                    try:
                        erorrs, account = thread.result()
                        if erorrs and erorrs == "PROXY":
                            DatabaseThread.update(ProxyModel, id=proxy.id, active=False) if proxy else None
                            self.account_list.append((account.account_type,
                                                      account.username,
                                                      account.password,
                                                      account.email))
                    except CancelledError:
                        break