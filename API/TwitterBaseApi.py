import re
import requests
from API.Logger import Logger
from warnings import simplefilter

simplefilter('ignore')


class TwitterBaseApi:
    ENDPOINTS = {
        'operations_script': 'https://abs.twimg.com/responsive-web/client-web-legacy/main.92d14499.js',
        'guest_token': 'https://www.twitter.com',
        'task': 'https://mobile.twitter.com/i/api/1.1/onboarding/task.json',
        'csrf_token': 'https://onlyfans.com/api2/v2/init',
        'verification': 'https://twitter.com/i/api/1.1/onboarding/begin_verification.json',
        'access_token': "https://twitter.com/i/api/graphql/%s/Viewer?%s",
        'create_tweet': "https://mobile.twitter.com/i/api/graphql/%s/CreateTweet",
        'upload_media': "https://upload.twitter.com/i/media/upload.json?command={command}",
        'favorite_tweet': "https://mobile.twitter.com/i/api/graphql/%s/FavoriteTweet",
        'retweet': "https://mobile.twitter.com/i/api/graphql/%s/CreateRetweet",
        'search': 'https://twitter.com/i/api/2/search/adaptive.json',
        'user': 'https://mobile.twitter.com/i/api/graphql/%s/UserByScreenName?',
        'media_alt_text': 'https://twitter.com/i/api/1.1/media/metadata/create.json',
        'follow': 'https://twitter.com/i/api/1.1/friendships/create.json',
        'update_profile_cover': 'https://twitter.com/i/api/1.1/account/update_profile_banner.json',
        'update_profile_image': 'https://twitter.com/i/api/1.1/account/update_profile_image.json',
        'update_profile': 'https://twitter.com/i/api/1.1/account/update_profile.json',
        'settings': 'https://twitter.com/i/api/1.1/account/settings.json',
        'notifications': 'https://twitter.com/i/api/1.1/friendships/update.json',
        'user_tweets': 'https://twitter.com/i/api/graphql/%s/UserTweets',
        'user_tweets_and_replies': 'https://twitter.com/i/api/graphql/%s/UserTweetsAndReplies',
        'user_media': 'https://twitter.com/i/api/graphql/%s/UserMedia',
        'user_likes': 'https://twitter.com/i/api/graphql/%s/Likes',
        'personalization': 'https://twitter.com/i/api/1.1/account/personalization/p13n_data.json',
        'verify_password': 'https://twitter.com/i/api/1.1/account/verify_password.json',
        'username_availability': 'https://twitter.com/i/api/i/users/username_available.json'
    }

    USER_AGENTS = {
        'web': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
    }

    ERROR_CODES = {
        'LOCKED': [326, 37, 353, 64, 32],
        'PROXY': [366],
        'PHONE_NUMBER': [398]
    }

    AUTHORIZATION_TOKEN = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'

    def __init__(self, locker=None):
        self._logger = Logger(threads_locker=locker)
        self._session: requests.Session = None
        self._guest_token = None
        self._flow_token = None
        self._email = None
        self._password = None
        self._user_id = None
        self._username = None
        self._is_logged = False

        self.operations = {
            'Retweeters': "E_sTx4dN9vCHFSQoHOfKhg",
            'Viewer': "4jeP7HyKpQUitFUTWedrqA",
            'CreateTweet': "kV0jgNRI3ofhHK_G5yhlZg",
            'TweetDetail': "Nze3idtpjn4wcl09GpmDRg",
            'FavoriteTweet': "lI07N6Otwv1PhnEgXILM7A",
            'CreateRetweet': "ojPdsZsimiJrUGLR1sjUtA",
            'UserByScreenName': 'vG3rchZtwqiwlKgUYCrTRA',
            'UserTweets': 'q881FFtQa69KN7jS9h_EDA',
            'UserMedia': '_vFDgkWOKL_U64Y2VmnvJw',
            'UserLikes': '8ymqOI9bCoMKsTDx80xXqw',
            'UserTweetsAndReplies': '9pXWTtWPf0yOWJBKslHq5w',
        }

        self.authorization = ""
        self._errors = None

    def _getTokens(self):
        try:
            self._logger.log("[*] Trying to get required tokens from twitter.")
            r = self._session.post(self.ENDPOINTS['guest_token'], verify=False)
            self._guest_token = re.findall(r'gt=(\d{19})', r.text, re.IGNORECASE)[0].replace("\"gt=", "")
            self._session.headers.update({
                'X-Guest-Token': self._guest_token,
                'Authorization': self.AUTHORIZATION_TOKEN,
            })
            self._logger.log("[*] twitter api required tokens fetched successfully")
            return self.authorization, self._guest_token, self.operations
        except Exception as e:
            self._logger.log(f"[-] failed to get the required tokens from twitter api.\n\terrors: {e}", error=True)

    def _getCSRFToken(self):
        self._logger.log("[*] trying to get access tokens from twitter api.")
        try:
            self._logger.log(f"\t[+] trying to get web access token")
            self._session.headers['X-Csrf-Token'] = self._session.cookies['ct0']
            access_token_response = self._session.get(self.ENDPOINTS['access_token'] %
                                                      (self.operations['Viewer'],
                                                       "variables=%7B%22withCommunitiesMemberships%22%3Atrue%2C"
                                                       "%22withCommunitiesCreation%22%3Atrue%2C"
                                                       "%22withSuperFollowsUserFields%22%3Atrue%7D&features=%7B"
                                                       "%22responsive_web_graphql_timeline_navigation_enabled%22"
                                                       "%3Afalse%7D")
                                                      , verify=False)
            if access_token_response.json().get('errors') is None:
                self._session.headers.update({
                    'X-Csrf-Token': access_token_response.cookies['ct0'],
                    'x-twitter-active-user': 'yes',
                    'x-twitter-auth-type': 'OAuth2Session',
                    'x-twitter-client-language': 'en'
                })

                self._logger.log("[*] csrf token has been fetched successfully.")
                return True
            self._errors = access_token_response.json()['errors'][0]['code'] if not self._errors else self._errors
            self._logger.log(
                f"[-] couldn't get csrf token.\n\terrors: {access_token_response.json()['errors'][0]['message']}", True)
        except Exception as e:
            self._logger.log(f"[-] couldn't get csrf token.\n\terrors: {e}", True)
        return False

    def errors(self):
        for key, item in self.ERROR_CODES.items():
            if self._errors in item:
                return key

    @property
    def session(self):
        return self._session

    @property
    def logged(self):
        return self._is_logged