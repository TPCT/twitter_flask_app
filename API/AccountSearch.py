import re
import requests
import urllib3
from API.Logger import Logger
from API.Payloads import Payloads

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AccountSearch:
    ENDPOINTS = {
        'operations_script': 'https://abs.twimg.com/responsive-web/client-web-legacy/main.92d14499.js',
        'main_tokens': 'https://twitter.com/i/flow/login',
        'access_token': "https://twitter.com/i/api/graphql/%s/Viewer?%s",
        'search': 'https://twitter.com/i/api/2/search/adaptive.json',
        'user': 'https://mobile.twitter.com/i/api/graphql/%s/UserByScreenName?'
    }

    USER_AGENTS = {
        'web': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'android': 'TwitterAndroid/9.58.0-release.0 (29580000-r-0) Samsung+Galaxy+S10/10 (Genymobile;Samsung+Galaxy+S10;Android;vbox86p;0;;1;2010)',
        'iphone': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/36.0  Mobile/15E148 Safari/605.1.15'
    }

    ERROR_CODES = {
        'LOCKED': [326, 37, 353]
    }

    def __init__(self, locker=None):
        self._logger = Logger(threads_locker=locker)
        self._session = requests.Session()
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
            'UserByScreenName': 'vG3rchZtwqiwlKgUYCrTRA'
        }

        self.authorization = ""
        self._errors = None

    def __getTokens(self):
        try:
            self._logger.log("[*] Trying to get required tokens from twitter.")
            r = self._session.get(self.ENDPOINTS['main_tokens'], verify=False)
            self._guest_token = re.findall(r'gt=(\d{19})', r.text, re.IGNORECASE)[0].replace("\"gt=", "")
            self.authorization = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
            self._logger.log("\t[+] Guest token: %s" % self._guest_token)
            self._session.headers.update({
                'X-Guest-Token': self._guest_token,
                'Authorization': self.authorization,
            })

            self._logger.log("[*] twitter api required tokens fetched successfully")
            return self.authorization, self._guest_token, self.operations
        except Exception as e:
            self._logger.log(f"[-] failed to get the required tokens from twitter api.\n\terrors: {e}", error=True)

    def search(self, username, proxy_user=None, proxy_password=None, proxy_ip=None, proxy_port=None,
               search_type='tweets'):
        username = username.replace('@', '')
        self.__getTokens()
        self._logger.log(f"[+] trying to search for account: {username}")
        try:
            if all([proxy_user, proxy_password, proxy_ip, proxy_port]):
                self._session.proxies({
                    'http': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}',
                    'https': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}'
                })
            search_response = self._session.get(Payloads.accountCheckPayload('search', self.ENDPOINTS['search'],
                                                                             username=username, search_type=search_type))
            search_response_json = search_response.json()
            if search_response_json.get('errors'):
                self._logger.log(f'[-] an error occurred while trying to search {username}\n\t'
                                 f'errors: {search_response_json["errors"][0]["message"]}', True)
                return False
            self._logger.log(f'[+] {username} has been fetched successfully')
            return search_response_json.get('globalObjects')
        except Exception as e:
            self._logger.log(f'[-] an error occurred while trying to search {username}\n\terrors: {e}', True)
        return False

    def checkAccount(self, username, proxy_user=None, proxy_password=None, proxy_ip=None, proxy_port=None):
        try:
            self.__getTokens()
            self._logger.log(f"[*] Trying to check: {username} to twitter api.")
            username = username.replace('@', '')
            if all([proxy_user, proxy_password, proxy_ip, proxy_port]):
                self._session.proxies({
                    'http': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}',
                    'https': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}'
                })
            check_account_response = self._session.get(Payloads.accountCheckPayload('check',
                                                                                    self.ENDPOINTS['user'] %
                                                                                    (self.operations[
                                                                                        'UserByScreenName']),
                                                                                    username=username))
            check_account_response_json = check_account_response.json()
            if not check_account_response_json.get('errors'):
                self._logger.log(f"[*] checked the account {username}")
                result = check_account_response_json.get('data', {}).get('user', {}).get('result', {})
                return {
                    'followers_count': result.get('legacy', {}).get('followers_count'),
                    'suspended': result.get('__typename') == 'UserUnavailable',
                    'restricted': result.get('legacy', {}).get('profile_interstitial_type') == 'fake_account',
                    'active': result.get('legacy', {}).get('profile_interstitial_type') == '',
                    'account_id': result.get('rest_id', 0)
                }
            self._logger.log(
                f"[-] failed to check account.\n\terrors: {check_account_response_json['errors'][0]['message']}",
                True)
        except Exception as e:
            self._logger.log(f"[-] Failed to check account: {username}.\n\terrors: {e}", True)


if __name__ == "__main__":
    account_search = AccountSearch()
    # 1568189262729986048
    print(account_search.checkAccount('islamTPCT12'))
