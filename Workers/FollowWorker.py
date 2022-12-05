import random
from config import db
from Models.AccountModel import AccountModel
from Models.SessionModel import SessionModel
from Models.StatusModel import StatusModel
from Database.DatabaseWorker import DatabaseThread
from Workers.BaseWorker import BaseWorker
from Constants.AccountTypes import AccountTypes
from concurrent.futures import ThreadPoolExecutor


class FollowWorker(BaseWorker):
    def __init__(self, user_id, session_id, *args, **kwargs):
        super(FollowWorker, self).__init__(user_id, session_id, *args, **kwargs)
        self.status_handler = None
        self.settings = None
        self._results = {
            'valid_follows': 0,
            'invalid_follows': 0
        }
        self.followers_accounts = []
        self.follows_count = 0
        self.account_followers_count = 0

    def following_thread(self, account: AccountModel, account_id, trial=0, *args):
        with self.app.app_context():
            twitter_wrapper = account.twitter_wrapper()
            operation_status = twitter_wrapper.follow(account_id)
            self.updateDatabase(account.serialize, twitter_wrapper)

            if not operation_status and trial <= 10:
                return self.following_thread(random.choice(self.followers_accounts), account_id, trial + 1)

            if operation_status and self.settings.notify:
                twitter_wrapper.notify(account_id)

            account_followers_count = operation_status.get('followers_count') \
                if operation_status else self.account_followers_count

            self.account_followers_count = account_followers_count \
                if account_followers_count >= self.account_followers_count else self.account_followers_count

            self.updateDatabase(account.serialize, twitter_wrapper)
            account.saveHandler(twitter_wrapper)
            return operation_status

    def updateDatabase(self, account, twitter_wrapper):
        with self.app.app_context():
            DatabaseThread.update(AccountModel,
                                  session_id=self._session_id,
                                  id=account['id'],
                                  active=twitter_wrapper.logged,
                                  suspended=not twitter_wrapper.logged)

    def operation(self):
        with self.app.app_context():
            db.session.flush()
            session = db.session.query(SessionModel).filter_by(id=self._session_id, user_id=self._user_id).first()
            to_be_followed_accounts = AccountModel.getMany(session.id, [AccountTypes.followed], {'active': True})

            self.followers_accounts = AccountModel.getMany(session.id, [AccountTypes.follower], {'active': True})

            self.settings = session.settings.first()
            self.status_handler = session.status.first().serialize
            db.session.close()

            if not (to_be_followed_accounts or self.followers_accounts):
                self.complete()
                return

            for account in to_be_followed_accounts:
                if self._terminate:
                    break

                self.follows_count = random.randint(self.settings.min_follow_count,
                                                    self.settings.max_follow_count)

                account_followers = self.following_thread(random.choice(self.followers_accounts), account.account_id)
                while account_followers is False:
                    account_followers = self.following_thread(random.choice(self.followers_accounts),
                                                              account.account_id)

                self.account_followers_count = account_followers.get('followers_count', 0)
                self.follows_count = self.account_followers_count + self.follows_count

                min_follows = self.account_followers_count + self.settings.min_follow_count
                max_follows = self.account_followers_count + self.settings.max_follow_count

                random.shuffle(self.followers_accounts)

                for i in range(10):
                    with ThreadPoolExecutor(50) as executor:
                        if self.account_followers_count >= self.follows_count:
                            break

                        for follower_account in self.followers_accounts[
                                                :self.follows_count - self.account_followers_count]:
                            if not self._terminate:
                                self._threads_pool.append(executor.submit(self.following_thread,
                                                                          follower_account,
                                                                          account.account_id))

                success = min_follows <= self.account_followers_count <= max_follows or \
                          self.account_followers_count >= max_follows \
                          or self.account_followers_count >= self.follows_count

                self._results['valid_follows'] += success
                self._results['invalid_follows'] += not success

                DatabaseThread.update(AccountModel, id=account.id,
                                      follow_failed=1 if not success else -1)

                DatabaseThread.update(StatusModel, session_id=self._session_id,
                                      id=self.status_handler['id'],
                                      **self._results)
