from API.TwitterBaseApi import TwitterBaseApi
from API.Payloads import Payloads
import requests


class RegisterApi(TwitterBaseApi):
    def _getCSRFToken(self):
        try:
            self._logger.log("[*] trying to get csrf tokens from twitter api.")
            response = self._session.get(self.ENDPOINTS['csrf_token'], headers={
                'accept': 'application/json',
                'app-token': '33d57ade8c02dbc5a333db99ff9ae26a',
                'origin': 'https://onlyfans.com/',
                'referer': 'https://onlyfans.com/',
                'sign': '2797:55311102c2ffacd7148ad23211b9abd889dc5b63:799:62321932',
                'time': '1647495197759',
                'x-bc': '61986e6187067400bd7893a6583fcda35f40d3cb'
            })
            self._session.headers['X-Csrf-Token'] = response.json()['csrf']
            return True
        except Exception as e:
            self._logger.log(f"[-] couldn't get csrf token.\n\terrors: {e}", True)
        return False

    def __registerFlowToken(self):
        try:
            self._logger.log("\t[+] trying to fetch register flow token.")
            flow_1_response = self._session.post(self.ENDPOINTS['task'], params={
                'flow_name': 'signup'
            }, verify=False, json=Payloads.signupFlowTokenPayload())
            if flow_1_response.json().get('errors'):
                self._logger.log(f"[-] couldn't get flow tokens from twitter.\n\terrors: "
                                 f"{flow_1_response.json()['errors'][-1]['message']}", True)
                return False
            self._flow_token = flow_1_response.json()['flow_token']
            # flow_2_response = self._session.post(self.ENDPOINTS['task'], verify=False,
            #                                      json=Payloads.signupFlowTokenPayload())
            # if flow_2_response.json().get('errors'):
            #     self._logger.log(f"[-] couldn't get flow tokens from twitter.\n\terrors: "
            #                      f"{flow_1_response.json()['errors'][-1]['message']}", True)
            #     return False
            # self._flow_token = flow_2_response.json()['flow_token']
            self._logger.log(f"[+] flow tokens has been fetched from twitter")
            return True
        except Exception as e:
            self._logger.log(f"[-] couldn't get flow tokens from twitter.\n\terrors: {e}", True)

    def __mobileVerificationFlowToken(self):
        try:
            self._logger.log("\t[+] trying to fetch mobile verification tokens.")
            mobile_verification_response = self._session.post(self.ENDPOINTS['verification'], verify=False,
                                                              json=Payloads.phoneVerificationPayload(self._flow_token,
                                                                                                     self._email))
            if not mobile_verification_response.json().get('errors'):
                self._logger.log("\t[+] mobile verification flow fetched successfully.")
                return True
            self._logger.log(f"[-] couldn't get mobile verification tokens from twitter.\n\terrors: "
                             f"{mobile_verification_response.json()['errors'][-1]['message']}", True)
        except Exception as e:
            self._logger.log(f"[-] couldn't get mobile verification tokens from twitter.\n\terrors: {e}", True)

    def __register(self, username, password, email=None, phone_number=None):
        try:
            self._username = username
            self._email = email if email else phone_number
            self._password = password
            self._logger.log("[*] trying to register to twitter api")
            if not self._getCSRFToken():
                return False

            if not self.__registerFlowToken():
                return False

            if phone_number and not self.__mobileVerificationFlowToken():
                return False

            self._logger.log("[*] registered to twitter api successfully")
            return True
        except Exception as e:
            self._logger.log(f"[-] couldn't register to twitter.\n\terrors: {e}", True)
        return False

    def register(self, username, password, email=None, phone_number=None,
                 proxy_user=None, proxy_password=None, proxy_ip=None, proxy_port=None):
        self._session = requests.Session()
        self._session.headers.update({
            'Origin': 'https://twitter.com',
            'Referer': 'https://twitter.com/',
            'x-twitter-client-language': 'en'
        })
        if all([proxy_user, proxy_password, proxy_ip, proxy_port]):
            self._session.proxies.update({
                'http': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}',
                'https': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}'
            })
        tokens = self._getTokens()
        if not tokens:
            self._logger.log("[-] unable to login to twitter api.\n\terrors: can't get the required tokens", True)
            return False
        self._is_logged = self.__register(username, password, email, phone_number)
        return self._is_logged

    # def __loginUsernameFlow(self):
    #     try:
    #         self._logger.log("\t[+] trying to fetch username response.")
    #         username_response = self._session.post(self.ENDPOINTS['flow_2'], verify=False,
    #                                                json=Payloads.loginPayload('username', username=self._username,
    #                                                                           flow_token=self._flow_token))
    #         username_response_json = username_response.json()
    #         if not username_response_json.get('errors'):
    #             self._flow_token = username_response_json['flow_token']
    #             self._logger.log("\t[+] username response token has been fetched successfully.")
    #         self._logger.log('\t[-] invalid authentication.\n\t\terrors:' +
    #                          username_response_json[0]['message'],
    #                          True)
    #         self._errors = username_response_json['errors'][0]['code'] if not self._errors else self._errors
    #     except Exception as e:
    #         self._logger.log(f"[-] couldn't get username flow from twitter.\n\terrors: {e}", True)
    #     return False
    #
    # def __loginPasswordFlow(self):
    #     try:
    #         self._logger.log("\t[+] trying to fetch password response.")
    #         password_response = self._session.post(self.ENDPOINTS['flow_2'], verify=False,
    #                                                json=Payloads.loginPayload('password',
    #                                                                           flow_token=self._flow_token,
    #                                                                           password=self._password))
    #         password_response_json = password_response.json()
    #         if not password_response_json.get('errors'):
    #             self._flow_token = password_response_json['flow_token']
    #             self._user_id = password_response_json['subtasks'][0]['check_logged_in_account']['user_id']
    #
    #             self._logger.log("\t[+] password response token has been fetched successfully.")
    #             self._logger.log("[*] user_id: %s" % self._user_id)
    #             return True
    #         self._logger.log('\t[-] invalid authentication.\n\t\terrors:' +
    #                          password_response_json['errors'][0]['message'], True)
    #         self._errors = password_response_json['errors'][0]['code'] if not self._errors else self._errors
    #     except Exception as e:
    #         self._logger.log(f"[-] couldn't get password flow from twitter.\n\terrors: {e}", True)
    #     return False
    #
    # def __accountDuplicationFlow(self):
    #     try:
    #         self._logger.log("[*] Trying to check account duplication")
    #         authentication_token_response = self._session.post(self.ENDPOINTS['flow_2'], verify=False,
    #                                                            json=Payloads.loginPayload('duplication',
    #                                                                                       flow_token=self._flow_token))
    #         authentication_token_response_json = authentication_token_response.json()
    #         self._flow_token = authentication_token_response_json['flow_token']
    #         if authentication_token_response_json.get('subtasks', [{}])[0].get('subtask_id') == "LoginAcid":
    #             self._logger.log("[*] email login is required")
    #             email_response = self._session.post(self.ENDPOINTS['flow_2'],
    #                                                 json=Payloads.loginPayload('verify',
    #                                                                            flow_token=self._flow_token,
    #                                                                            email=self._email))
    #             email_response_json = email_response.json()
    #             if not email_response_json.get('errors'):
    #                 self._logger.log("[*] email login has succeeded successfully.")
    #                 return True
    #             self._logger.log('\t[-] invalid authentication.\n\t\terrors:' +
    #                              email_response_json['errors'][0]['message'], True)
    #             self._errors = email_response_json['errors'][0]['code'] if not self._errors else self._errors
    #     except Exception as e:
    #         self._logger.log(f"[-] couldn't get account duplication from twitter.\n\terrors: {e}", True)
    #     return False
    #
    # def __login(self, username, password, email):
    #     try:
    #         self._username = username
    #         self._email = email
    #         self._password = password
    #         self._logger.log("[*] trying to login to twitter api")
    #         self.__loginFlowTokens()
    #         if not self.__loginUsernameFlow():
    #             return False
    #
    #         if not self.__loginPasswordFlow():
    #             return False
    #
    #         if not self.__accountDuplicationFlow():
    #             return False
    #         self._logger.log("[*] logged in twitter api successfully")
    #         return True
    #     except Exception as e:
    #         self._logger.log(f"[-] couldn't login to twitter.\n\terrors: {e}", True)
    #     return False


if __name__ == "__main__":
    register_api = RegisterApi()
    account_username = "adjasdhasjkdh"
    account_password = "adasjdhaskjd"
    account_email = "asdhasjdhasd"
    account_phone_number = "201062905126"
    register_api.register(account_username, account_password, account_email, account_phone_number)

