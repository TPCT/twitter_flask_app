import random
import time
from Models.AccountModel import AccountModel
from Models.SessionModel import SessionModel
from Models.TextModel import TextModel
from Models.StorageModel import StorageModel
from Database.DatabaseWorker import DatabaseThread
from flask import current_app
from threading import Thread
from config import db
from concurrent.futures import ThreadPoolExecutor
from Constants.AccountTypes import AccountTypes
from Constants.TextTypes import TextTypes
from Constants.FileTypes import FileTypes


class ReactionsWorker(Thread):
    def __init__(self, user_id, session_id, username, tweet_id, *args, **kwargs):
        super(ReactionsWorker, self).__init__(daemon=True, *args, **kwargs)
        self._user_id = user_id
        self._session_id = session_id
        self.app = current_app._get_current_object()
        self.accounts = None
        self.tweet_id = tweet_id
        self.account_username = username

        self.retweets_count = 0
        self.likes_count = 0
        self.quotes_count = 0
        self.replies_count = 0

        self.user = None
        self.status = None
        self.quotes_text = None or [None]
        self.replies_text = None or [None]
        self.settings = None

        self._results = {
            'valid_reacts': 0,
            'valid_retweets': 0,
            'valid_quotes': 0,
            'valid_replies': 0,
            'invalid_reacts': 0,
            'invalid_retweets': 0,
            'invalid_quotes': 0,
            'invalid_replies': 0
        }

        self._counters = {
            'react': 0,
            'retweet': 0,
            'quote': 0,
            'reply': 0
        }

        self._threads_pool = []
        self.run()

    def reactingThread(self, tweet_id, account: AccountModel, *args):
        with self.app.app_context():
            twitter_wrapper = account.twitter_wrapper()
            success = twitter_wrapper.reactTweet(tweet_id)
            return success, twitter_wrapper

    def retweetThread(self, tweet_id, account: AccountModel, *args):
        with self.app.app_context():
            twitter_wrapper = account.twitter_wrapper()
            success = twitter_wrapper.tweet(tweet_id=tweet_id, tweet_type='retweet', tweet_text="")
            return success, twitter_wrapper

    def quoteThread(self, tweet_id, account: AccountModel, account_username, quote_text=None, *args):
        with self.app.app_context():
            twitter_wrapper = account.twitter_wrapper()
            quote_text = f"{time.time()}" if not quote_text else quote_text
            success = twitter_wrapper.tweet(tweet_type="quote", tweet_text=quote_text,
                                            quote_url=f"https://twitter.com/{account_username.replace('@', '')}"
                                                      f"/status/{tweet_id}")
            return success, twitter_wrapper

    def repliesThread(self, tweet_id, account: AccountModel, reply_text=None, *args):
        with self.app.app_context():
            twitter_wrapper = account.twitter_wrapper()
            reply_text = f"{time.time()}" if not reply_text else reply_text
            success = twitter_wrapper.tweet(tweet_type='reply', tweet_text=reply_text,
                                            tweet_id=tweet_id)
            return success, twitter_wrapper

    def updateDatabase(self, account_id, operations_status, twitter_wrapper):
        with self.app.app_context():
            for operation_status in operations_status:
                self._results[f'valid_{operation_status["name"]}'] += bool(operation_status['success'])
                self._results[f'invalid_{operation_status["name"]}'] += not bool(operation_status['success'])

            DatabaseThread.update(AccountModel,
                                  id=account_id,
                                  session_id=self._session_id,
                                  active=twitter_wrapper.logged,
                                  suspended=not twitter_wrapper.logged)

    def main_routine(self, reacting_account: AccountModel, tweet_id, action, trial=0):

        to_be_updated = []
        final_twitter_wrapper = None

        def quote(account):
            nonlocal final_twitter_wrapper
            success = True
            with self.app.app_context():
                if account.account_type & AccountTypes.quote and self._counters['quote'] < self.quotes_count:
                    quote_text = ""
                    if self.settings.random_quotes and self.quotes_text:
                        quote_text: StorageModel | TextModel = random.choice(self.quotes_text)
                        quote_text = quote_text.getData(quote_text.id)

                    quote_text += f"\n{self.settings.fixed_quote_string}" \
                        if quote_text else self.settings.fixed_quote_string

                    success, final_twitter_wrapper = self.quoteThread(tweet_id, account,
                                                                      account.username,
                                                                      quote_text)
                    to_be_updated.append({
                        'name': 'quotes',
                        'success': success
                    })
            return success, 'quote'

        def reply(account, *args):
            nonlocal final_twitter_wrapper
            success = True
            with self.app.app_context():
                if account.account_type & AccountTypes.reply and self._counters['reply'] < self.replies_count:
                    reply_text = ""
                    if self.settings.random_replies and self.replies_text:
                        reply_text: StorageModel | TextModel = random.choice(self.replies_text)
                        reply_text = reply_text.getData(reply_text.id)

                    reply_text += f"\n{self.settings.fixed_reply_string}" \
                        if reply_text else self.settings.fixed_reply_string

                    success, final_twitter_wrapper = self.repliesThread(tweet_id, account, reply_text)

                    to_be_updated.append({
                        'name': 'replies',
                        'success': success
                    })
            return success, 'reply'

        def retweet(account, *args):
            nonlocal final_twitter_wrapper
            success = True
            if account.account_type & AccountTypes.retweet and self._counters['retweet'] < self.retweets_count:
                success, final_twitter_wrapper = self.retweetThread(tweet_id, account)
                to_be_updated.append({
                    'name': 'retweets',
                    'success': success
                })
            return success, 'retweet'

        def react(account, *args):
            nonlocal final_twitter_wrapper
            success = True
            if account.account_type & AccountTypes.react and self._counters['react'] < self.likes_count:
                success, final_twitter_wrapper = self.reactingThread(tweet_id, account)
                to_be_updated.append({
                    'name': 'reacts',
                    'success': success
                })
            return success, 'react'

        actions = {
            'react': react,
            'retweet': retweet,
            'quote': quote,
            'reply': reply
        }

        success, name = actions[action](reacting_account)
        self._counters[name] += bool(success)

        if not success and trial <= 5:
            return self.main_routine(random.choice(self.accounts), self.tweet_id, name, trial + 1)

        if all([to_be_updated, final_twitter_wrapper]):
            with self.app.app_context():
                reacting_account.saveHandler(final_twitter_wrapper)
            self.updateDatabase(reacting_account.id, to_be_updated, final_twitter_wrapper)

    def run(self):
        with self.app.app_context():
            db.session.flush()

            current_session = db.session.query(SessionModel).filter_by(id=self._session_id,
                                                                       user_id=self._user_id).first()
            self.settings = current_session.settings.first()
            self.status = current_session.status.first()

            self.quotes_text = TextModel.getMany(self._session_id, [TextTypes.quote]) or \
                               StorageModel.getMany(self._user_id, FileTypes.text, [TextTypes.quote],
                                                    self.settings.tweet_arabic)

            self.replies_text = TextModel.getMany(self._session_id, [TextTypes.reply]) or \
                                StorageModel.getMany(self._user_id, FileTypes.text, [TextTypes.reply],
                                                     self.settings.tweet_arabic)

            self.retweets_count = random.randint(self.settings.min_retweets_count, self.settings.max_retweets_count)
            self.likes_count = random.randint(self.settings.min_likes_count, self.settings.max_likes_count)
            self.quotes_count = random.randint(self.settings.min_quotes_count, self.settings.max_quotes_count)
            self.replies_count = random.randint(self.settings.min_replies_count, self.settings.max_replies_count)

            self.accounts = AccountModel.getMany(current_session.id, [AccountTypes.reply, AccountTypes.quote,
                                                                      AccountTypes.react, AccountTypes.retweet],
                                                 {'active': True})

            self._results = self.status.serialize

            if not self.accounts or not any(
                    [self.likes_count, self.quotes_count, self.replies_count, self.retweets_count]):
                return

            with ThreadPoolExecutor(max_workers=max([self.likes_count,
                                                     self.quotes_count,
                                                     self.replies_count,
                                                     self.retweets_count])) as executor:

                random.shuffle(self.accounts)
                for account in self.accounts[:self.retweets_count]:
                    self._threads_pool.append(executor.submit(self.main_routine, account, self.tweet_id, 'retweet'))

                random.shuffle(self.accounts)
                for account in self.accounts[:self.replies_count]:
                    self._threads_pool.append(executor.submit(self.main_routine, account, self.tweet_id, 'reply'))

                random.shuffle(self.accounts)
                for account in self.accounts[:self.quotes_count]:
                    self._threads_pool.append(executor.submit(self.main_routine, account, self.tweet_id, 'quote'))

                random.shuffle(self.accounts)
                for account in self.accounts[:self.likes_count]:
                    self._threads_pool.append(executor.submit(self.main_routine, account, self.tweet_id, 'react'))
