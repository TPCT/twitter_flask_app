from config import db
from Models.AccountModel import AccountModel
from Models.SessionModel import SessionModel
from Models.StatusModel import StatusModel
from Models.TextModel import TextModel
from Models.ImageModel import ImageModel
from Models.StorageModel import StorageModel
from Workers.BaseWorker import BaseWorker
from API.ImageRandomizer import ImageRandomize
from API.TwitterAccount import TwitterAccount
from concurrent.futures import ThreadPoolExecutor
from Constants.TextTypes import TextTypes
from Constants.ImageTypes import ImageTypes
from Constants.AccountTypes import AccountTypes
from Constants.FileTypes import FileTypes
from Database.DatabaseWorker import DatabaseThread
import random


class ProfileWorker(BaseWorker):
    def __init__(self, user_id, session_id, *args, **kwargs):
        super(ProfileWorker, self).__init__(user_id, session_id, *args, **kwargs)
        self.status_handler = None
        self.settings = None
        self._results = {
            'valid_profiles': 0,
            'invalid_profiles': 0,
            'valid_privates': 0,
            'invalid_privates': 0
        }

    def profileThread(self, account: AccountModel, trail=0, **kwargs):
        with self.app.app_context():
            twitter_wrapper: TwitterAccount = account.twitter_wrapper()

            profile_info_status = None
            if account.account_type & AccountTypes.profile:
                profile_info_status = twitter_wrapper.profileInfo(**kwargs)

            private_profile_status = None
            if account.account_type & AccountTypes.private:
                private_profile_status = twitter_wrapper.private()

            if not (private_profile_status or profile_info_status) and trail <= 5 and not self._terminate:
                return self.profileThread(account, trail=trail + 1, **kwargs)

            account.saveHandler(twitter_wrapper)
            self.updateDatabase(account.serialize, private_profile_status, profile_info_status, twitter_wrapper)

        return private_profile_status and profile_info_status

    def updateDatabase(self, account, private_profile_status, profile_info_status, twitter_wrapper):
        with self.app.app_context():
            DatabaseThread.update(AccountModel,
                                  session_id=self._session_id,
                                  id=account['id'],
                                  active=twitter_wrapper.logged,
                                  suspended=not twitter_wrapper.logged)

            if private_profile_status is not None:
                self._results['valid_privates'] += bool(private_profile_status)
                self._results['invalid_privates'] += not bool(private_profile_status)

            if profile_info_status is not None:
                self._results['valid_profiles'] += bool(profile_info_status)
                self._results['invalid_profiles'] += not bool(profile_info_status)

            DatabaseThread.update(StatusModel, session_id=self._session_id, id=self.status_handler['id'],
                                  **self._results)

    def operation(self):
        with self.app.app_context():
            db.session.flush()
            session = SessionModel.getOne(self._session_id)
            accounts = AccountModel.getMany(session.id, [AccountTypes.profile, AccountTypes.private],
                                            {'active': True, 'hidden': False})
            self.settings = session.settings.first()
            self.status_handler = session.status.first().serialize

            profile_images = ImageModel.getMany(session.id, [ImageTypes.profile_picture])
            profile_images = profile_images or StorageModel.getMany(self._user_id,
                                                                    FileTypes.images,
                                                                    [ImageTypes.profile_picture])

            profile_covers = ImageModel.getMany(session.id, [ImageTypes.profile_cover])
            profile_covers = profile_covers or StorageModel.getMany(self._user_id,
                                                                    FileTypes.images,
                                                                    [ImageTypes.profile_cover])

            profile_usernames = TextModel.getMany(session.id, [TextTypes.username])
            profile_usernames = profile_usernames or StorageModel.getMany(self._user_id,
                                                                          FileTypes.text,
                                                                          [TextTypes.username],
                                                                          self.settings.tweet_arabic)

            profile_countries = TextModel.getMany(session.id, [TextTypes.country])
            profile_countries = profile_countries or StorageModel.getMany(self._user_id,
                                                                          FileTypes.text,
                                                                          [TextTypes.country],
                                                                          self.settings.tweet_arabic)

            profile_bios = TextModel.getMany(session.id, [TextTypes.bio])
            profile_bios = profile_bios or StorageModel.getMany(self._user_id,
                                                                FileTypes.text,
                                                                [TextTypes.bio],
                                                                self.settings.tweet_arabic)

            db.session.close()

            with ThreadPoolExecutor(10) as executor:
                for account in accounts:
                    if self._terminate:
                        break

                    profile_image = b""
                    if profile_images:
                        profile_image: ImageModel | StorageModel = random.choice(profile_images)
                        profile_image = profile_image.getData(profile_image.id)
                        if self.settings.random_profile_images:
                            profile_image = ImageRandomize(profile_image).randomize()

                    profile_cover = b""
                    if profile_covers:
                        profile_cover: ImageModel | StorageModel = random.choice(profile_covers)
                        profile_cover = profile_cover.getData(profile_cover.id)
                        if self.settings.random_cover_images:
                            profile_cover = ImageRandomize(profile_cover).randomize()

                    profile_username = self.settings.fixed_username_string
                    if profile_usernames and self.settings.random_usernames:
                        temp_profile_username: TextModel | StorageModel = random.choice(profile_usernames)
                        temp_profile_username = temp_profile_username.getData(temp_profile_username.id)
                        profile_username += " " + temp_profile_username

                    profile_country = self.settings.fixed_country_string
                    if profile_countries and self.settings.random_countries:
                        temp_profile_country: TextModel | StorageModel = random.choice(profile_countries)
                        temp_profile_country = temp_profile_country.getData(temp_profile_country.id)
                        profile_country += " " + temp_profile_country

                    profile_bio = self.settings.fixed_bio_string
                    if profile_bios and self.settings.random_bios:
                        temp_profile_bio: TextModel | StorageModel = random.choice(profile_bios)
                        temp_profile_bio = temp_profile_bio.getData(temp_profile_bio.id)
                        profile_bio += " " + temp_profile_bio

                    self._threads_pool.append(executor.submit(self.profileThread, account, **{
                        'username': profile_username[:50],
                        'country': profile_country[:150],
                        'bio': profile_bio[:160],
                        'profile_picture': profile_image,
                        'cover_picture': profile_cover
                    }))
