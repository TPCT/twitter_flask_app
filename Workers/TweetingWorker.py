import time
import random
from config import db
from Models.AccountModel import AccountModel
from Models.SessionModel import SessionModel
from Models.StatusModel import StatusModel
from Models.ImageModel import ImageModel
from Models.TextModel import TextModel
from Models.StorageModel import StorageModel
from Models.ProxyModel import ProxyModel
from Database.DatabaseWorker import DatabaseThread
from Workers.ReactionsWorker import ReactionsWorker
from Workers.BaseWorker import BaseWorker
from API.AccountSearch import AccountSearch
from API.ImageRandomizer import ImageRandomize
from Constants.AccountTypes import AccountTypes
from Constants.ImageTypes import ImageTypes
from Constants.TextTypes import TextTypes
from Constants.FileTypes import FileTypes
from Constants.ProxyTypes import ProxyTypes


class TweetingWorker(BaseWorker):
    def __init__(self, user_id, session_id, *args, **kwargs):
        super(TweetingWorker, self).__init__(user_id, session_id, *args, **kwargs)
        self.status_handler = None
        self.settings = None
        self._results = {'valid_tweets': 0, 'invalid_tweets': 0}
        self.iteration_count = {}
        self.texts = []
        self.images = []
        self.accounts_index = 0
        self.proxies = []

    def tweetingThread(self, account: AccountModel, tweet_text, tweet_image, trial=0, tweet_id=None,
                       twitter_wrapper=None):
        if trial > 5:
            return self.updateDatabase(account.serialize, tweet_id, twitter_wrapper)

        with self.app.app_context():
            twitter_wrapper = account.twitter_wrapper()
            if tweet_image not in [None, False] and len(tweet_image):
                tweet_image = twitter_wrapper.uploadMedia(tweet_image)

            if tweet_image and self.settings.tweet_alt_text:
                twitter_wrapper.addAltText(self.settings.tweet_alt_text, tweet_image['media_id'])

            tweet_id = twitter_wrapper.tweet(tweet_text[:280],
                                             media=[tweet_image['media_id_string']]
                                             if tweet_image and tweet_image.get('media_id_string') else [])

            if tweet_id is False and not self._terminate:
                return self.tweetingThread(account, tweet_text, tweet_image, trial + 1, tweet_id, twitter_wrapper)

            ReactionsWorker(self._user_id, self._session_id, account.username, tweet_id)
            account.saveHandler(twitter_wrapper)
            self.updateDatabase(account.serialize, tweet_id, twitter_wrapper)
        return tweet_id

    def updateDatabase(self, account, account_status, twitter_wrapper):
        self._results['valid_tweets'] += bool(account_status)
        self._results['invalid_tweets'] += not bool(account_status)

        with self.app.app_context():
            DatabaseThread.update(AccountModel,
                                  session_id=self._session_id,
                                  id=account['id'],
                                  active=twitter_wrapper.logged,
                                  suspended=not twitter_wrapper.logged)

            DatabaseThread.update(StatusModel, session_id=self._session_id,
                                  id=self.status_handler['id'],
                                  **self._results)

    def checkAccount(self, account):
        if self.iteration_count.get(account.id) is not None:
            search_result = AccountSearch().search(account.username)
            while not search_result:
                search_result = AccountSearch().search(account.username)

            hidden = True
            for tweet_id, twitter_tweet in search_result.get('tweets', {}).items():
                if twitter_tweet.get('user_id_str') == account.account_id:
                    hidden = False
                    break

            if hidden:
                account.hidden = True
                db.session.merge(account)
                db.session.flush()
                db.session.commit()
                return False

        return True

    def prepareTweet(self):
        tweet_text = ""
        tweet_image = b""

        if self.settings.random_tweets:
            if self.texts:
                text: TextModel | StorageModel = random.choice(self.texts)
                tweet_text = text.getData(text.id)

            if self.images:
                image: ImageModel | StorageModel = random.choice(self.images)
                image = image.getData(image.id)
                tweet_image = ImageRandomize(image).randomize() \
                    if self.settings.random_images else image

        tweet_text += f"\n{self.settings.fixed_tweet_string}" \
            if tweet_text else self.settings.fixed_tweet_string

        return tweet_text, tweet_image

    def operation(self):
        while not self._terminate:
            accounts_index = 0
            with self.app.app_context():
                db.session.flush()
                session = db.session.query(SessionModel).filter_by(id=self._session_id, user_id=self._user_id).first()
                accounts = AccountModel.getMany(session.id, [AccountTypes.tweet], {'active': True, 'hidden': False})
                self.settings = session.settings.first()
                self.proxies = session.proxies.filter_by(proxy_for=ProxyTypes.account, active=True).all()
                self.texts = TextModel.getMany(session.id, [TextTypes.tweet])
                self.images = ImageModel.getMany(session.id, [ImageTypes.tweet])

                self.images = self.images or StorageModel.getMany(self._user_id, FileTypes.images, [ImageTypes.tweet],
                                                                  self.settings.tweet_arabic)

                self.texts = self.texts or StorageModel.getMany(self._user_id, FileTypes.text, [TextTypes.tweet],
                                                                self.settings.tweet_arabic)

                self.status_handler = session.status.first().serialize
                db.session.close()

                if not (accounts and (self.texts or self.images)):
                    self.terminate()
                    return

                accounts_length = len(accounts)

                for i in range(accounts_length):
                    if self._terminate:
                        break

                    account = accounts[accounts_index]

                    for j in range(self.settings.account_tweets_limit + 1):
                        if not self.checkAccount(account):
                            break

                        self.iteration_count[account.id] = self.iteration_count[account.id] + 1 \
                            if self.iteration_count.get(account.id) else 0

                        if self._terminate:
                            break

                        tweet_text, tweet_image = self.prepareTweet()

                        if not self.tweetingThread(account, tweet_text, tweet_image):
                            break

                        time.sleep(self.settings.tweets_time_sleep)
                    accounts_index = (accounts_index + 1) if len(accounts) - 1 > accounts_index else 0

                if not accounts_length:
                    break
