# import re
# import requests
# import urllib3
# from API.Logger import Logger
# from API.Payloads import Payloads
#
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#
#
# class TwitterWebAPI:
#     ENDPOINTS = {
#         'operations_script': 'https://abs.twimg.com/responsive-web/client-web-legacy/main.92d14499.js',
#         'main_tokens': 'https://twitter.com/i/flow/login',
#         'login_flow': 'https://mobile.twitter.com/i/api/1.1/onboarding/task.json?flow_name=login',
#         'flow_2': 'https://mobile.twitter.com/i/api/1.1/onboarding/task.json',
#         'access_token': "https://twitter.com/i/api/graphql/%s/Viewer?%s",
#         'create_tweet': "https://mobile.twitter.com/i/api/graphql/%s/CreateTweet",
#         'upload_media': "https://upload.twitter.com/i/media/upload.json?command={command}",
#         'favorite_tweet': "https://mobile.twitter.com/i/api/graphql/%s/FavoriteTweet",
#         'retweet': "https://mobile.twitter.com/i/api/graphql/%s/CreateRetweet",
#         'search': 'https://twitter.com/i/api/2/search/adaptive.json',
#         'user': 'https://mobile.twitter.com/i/api/graphql/%s/UserByScreenName?',
#         'media_alt_text': 'https://twitter.com/i/api/1.1/media/metadata/create.json',
#         'follow': 'https://twitter.com/i/api/1.1/friendships/create.json',
#         'update_profile_cover': 'https://twitter.com/i/api/1.1/account/update_profile_banner.json',
#         'update_profile_image': 'https://twitter.com/i/api/1.1/account/update_profile_image.json',
#         'update_profile': 'https://twitter.com/i/api/1.1/account/update_profile.json',
#         'settings': 'https://twitter.com/i/api/1.1/account/settings.json',
#         'notifications': 'https://twitter.com/i/api/1.1/friendships/update.json',
#         'personalization': 'https://twitter.com/i/api/1.1/account/personalization/p13n_data.json',
#         'verify_password': 'https://twitter.com/i/api/1.1/account/verify_password.json',
#         'username_availability': 'https://twitter.com/i/api/i/users/username_available.json'
#     }
#
#     USER_AGENTS = {
#         'web': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
#     }
#
#     ERROR_CODES = {
#         'LOCKED': [326, 37, 353, 64, 32],
#         'PROXY': [366]
#     }
#
#     def __init__(self, locker=None):
#         self._logger = Logger(threads_locker=locker)
#         self._session: requests.Session = None
#         self._guest_token = None
#         self._flow_token = None
#         self._email = None
#         self._password = None
#         self._user_id = None
#         self._username = None
#         self._is_logged = False
#
#         self.operations = {
#             'Retweeters': "E_sTx4dN9vCHFSQoHOfKhg",
#             'Viewer': "4jeP7HyKpQUitFUTWedrqA",
#             'CreateTweet': "kV0jgNRI3ofhHK_G5yhlZg",
#             'TweetDetail': "Nze3idtpjn4wcl09GpmDRg",
#             'FavoriteTweet': "lI07N6Otwv1PhnEgXILM7A",
#             'CreateRetweet': "ojPdsZsimiJrUGLR1sjUtA",
#             'UserByScreenName': 'vG3rchZtwqiwlKgUYCrTRA'
#         }
#
#         self.authorization = ""
#         self._errors = None
#
#     def getAccountInfo(self):
#         return {
#             'username': self._username,
#             'password': self._password,
#             'email': self._email,
#             'user_id': self._user_id
#         }
#
#     def __getTokens(self):
#         try:
#             self._logger.log("[*] Trying to get required tokens from twitter.")
#             r = self._session.get(self.ENDPOINTS['main_tokens'], verify=False)
#
#             self._guest_token = re.findall(r'gt=(\d{19})', r.text, re.IGNORECASE)[0].replace("\"gt=", "")
#             self.authorization = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
#             self._logger.log("\t[+] Guest token: %s" % self._guest_token)
#             self._session.headers.update({
#                 'X-Guest-Token': self._guest_token,
#                 'Authorization': self.authorization,
#             })
#
#             self._logger.log("[*] twitter api required tokens fetched successfully")
#             return self.authorization, self._guest_token, self.operations
#         except Exception as e:
#             self._logger.log(f"[-] failed to get the required tokens from twitter api.\n\terrors: {e}", error=True)
#
#     def __login(self, username, password, email):
#         try:
#             self._username = username
#             self._email = email
#             self._password = password
#             self._logger.log("[*] trying to login to twitter api")
#             self._logger.log("\t[+] trying to fetch login flow token.")
#             flow_1_response = self._session.post(self.ENDPOINTS['login_flow'], verify=False, json={})
#             self._flow_token = flow_1_response.json()['flow_token']
#             self._logger.log("\t[+] login flow fetched successfully.")
#
#             self._logger.log("\t[+] trying to get flow response token")
#             flow_2_response = self._session.post(self.ENDPOINTS['flow_2'], verify=False,
#                                                  json=Payloads.loginPayload('flow_token', flow_token=self._flow_token))
#             self._flow_token = flow_2_response.json()['flow_token']
#             self._logger.log("\t[+] flow response token has been fetched successfully.")
#
#             # Username Flow
#             self._logger.log("\t[+] trying to fetch username response.")
#             username_response = self._session.post(self.ENDPOINTS['flow_2'], verify=False,
#                                                    json=Payloads.loginPayload('username', username=self._username,
#                                                                               flow_token=self._flow_token))
#             username_response_json = username_response.json()
#             if username_response_json.get('errors'):
#                 self._logger.log('\t[-] invalid authentication.\n\t\terrors:' +
#                                  username_response_json[0]['message'],
#                                  True)
#                 self._errors = username_response_json['errors'][0]['code'] if not self._errors else self._errors
#                 return False
#
#             self._flow_token = username_response_json['flow_token']
#             self._logger.log("\t[+] username response token has been fetched successfully.")
#
#             # Password Flow
#             self._logger.log("\t[+] trying to fetch password response.")
#             password_response = self._session.post(self.ENDPOINTS['flow_2'], verify=False,
#                                                    json=Payloads.loginPayload('password',
#                                                                               flow_token=self._flow_token,
#                                                                               password=self._password))
#             password_response_json = password_response.json()
#             if password_response_json.get('errors'):
#                 self._logger.log('\t[-] invalid authentication.\n\t\terrors:' +
#                                  password_response_json['errors'][0]['message'], True)
#                 self._errors = password_response_json['errors'][0]['code'] if not self._errors else self._errors
#                 return False
#             self._flow_token = password_response_json['flow_token']
#             self._user_id = password_response_json['subtasks'][0]['check_logged_in_account']['user_id']
#
#             self._logger.log("\t[+] password response token has been fetched successfully.")
#             self._logger.log("[*] user_id: %s" % self._user_id)
#
#             # Account Duplication
#             self._logger.log("[*] logged in twitter api successfully")
#             authentication_token_response = self._session.post(self.ENDPOINTS['flow_2'], verify=False,
#                                                                json=Payloads.loginPayload('duplication',
#                                                                                           flow_token=self._flow_token))
#             authentication_token_response_json = authentication_token_response.json()
#             self._flow_token = authentication_token_response_json['flow_token']
#             if authentication_token_response_json.get('subtasks', [{}])[0].get('subtask_id') == "LoginAcid":
#                 self._logger.log("[*] email login is required")
#                 email_response = self._session.post(self.ENDPOINTS['flow_2'],
#                                                     json=Payloads.loginPayload('verify',
#                                                                                flow_token=self._flow_token,
#                                                                                email=self._email))
#                 email_response_json = email_response.json()
#                 if email_response_json.get('errors'):
#                     self._logger.log('\t[-] invalid authentication.\n\t\terrors:' +
#                                      email_response_json['errors'][0]['message'], True)
#                     self._errors = email_response_json['errors'][0]['code'] if not self._errors else self._errors
#                     return False
#                 self._logger.log("[*] email login has succeeded successfully.")
#             return True
#         except Exception as e:
#             self._logger.log(f"[-] couldn't login to twitter.\n\terrors: {e}", True)
#         return False
#
#     def __getCSRFToken(self):
#         self._logger.log("[*] trying to get access tokens from twitter api.")
#         try:
#             self._logger.log(f"\t[+] trying to get web access token")
#             self._session.headers['X-Csrf-Token'] = self._session.cookies['ct0']
#             access_token_response = self._session.get(self.ENDPOINTS['access_token'] %
#                                                       (self.operations['Viewer'],
#                                                        "variables=%7B%22withCommunitiesMemberships%22%3Atrue%2C"
#                                                        "%22withCommunitiesCreation%22%3Atrue%2C"
#                                                        "%22withSuperFollowsUserFields%22%3Atrue%7D&features=%7B"
#                                                        "%22responsive_web_graphql_timeline_navigation_enabled%22"
#                                                        "%3Afalse%7D")
#                                                       , verify=False)
#             if access_token_response.json().get('errors') is None:
#                 self._session.headers.update({
#                     'X-Csrf-Token': access_token_response.cookies['ct0'],
#                     'x-twitter-active-user': 'yes',
#                     'x-twitter-auth-type': 'OAuth2Session',
#                     'x-twitter-client-language': 'en'
#                 })
#
#                 self._logger.log("[*] csrf token has been fetched successfully.")
#                 return True
#             self._errors = access_token_response.json()['errors'][0]['code'] if not self._errors else self._errors
#             self._logger.log(
#                 f"[-] couldn't get csrf token.\n\terrors: {access_token_response.json()['errors'][0]['message']}", True)
#         except Exception as e:
#             self._logger.log(f"[-] couldn't get csrf token.\n\terrors: {e}", True)
#         return False
#
#     def Login(self, username, password, email, proxy_user=None, proxy_password=None, proxy_ip=None, proxy_port=None):
#         self._session = requests.Session()
#         self._session.headers.update({
#             'User-Agent': self.USER_AGENTS['web'],
#             'Referer': 'https://mobile.twitter.com/sw.js',
#             'x-requested-with': 'com.twitter.android.lite',
#         })
#         if all([proxy_user, proxy_password, proxy_ip, proxy_port]):
#             self._session.proxies.update({
#                 'http': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}',
#                 'https': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}'
#             })
#         tokens = self.__getTokens()
#         if not tokens:
#             self._logger.log("[-] unable to login to twitter api.\n\terrors: can't get the required tokens", True)
#             return False
#         self._is_logged = self.__login(username, password, email)
#         self._is_logged = self.__getCSRFToken()
#         return self._is_logged
#
#     def uploadMedia(self, binary_media, category="tweet_image"):
#         if self._is_logged:
#             try:
#                 self._logger.log(f"[*] Trying to upload media to twitter api.")
#
#                 command = "INIT"
#                 mime_type = 'image/png'
#                 content_length = len(binary_media) if binary_media is not None else 0
#
#                 url = self.ENDPOINTS[
#                           'upload_media'] + "&total_bytes={length}&media_type={media_type}&" + ("media_category={"
#                                                                                                 "media_category}"
#                                                                                                 if category else "")
#
#                 self._logger.log("\t[+] trying to initialize the request")
#                 initial_upload_response = self._session.post(url.format(command=command,
#                                                                         length=content_length,
#                                                                         media_type=mime_type,
#                                                                         media_category=category))
#                 initial_upload_response_json = initial_upload_response.json()
#                 if initial_upload_response_json.get('errors'):
#                     self._logger.log(
#                         f"[-] failed to upload media files.\n\terrors: "
#                         f"{initial_upload_response_json['errors'][0]['message']}",
#                         True)
#                     self._is_logged = initial_upload_response_json['errors'][0][
#                                           'code'] not in TwitterWebAPI.ERROR_CODES.get('LOCKED')
#                     self._errors = initial_upload_response_json['errors'][0]['code'] if not self._errors else self._errors
#                     return False
#
#                 # append upload
#                 command = 'APPEND'
#                 media_id = initial_upload_response_json['media_id']
#                 segment_index = 0
#                 url = self.ENDPOINTS['upload_media'] + f"&media_id={media_id}&segment_index={segment_index}"
#                 self._logger.log("\t[+] trying to append media to the request")
#                 append_upload_response = self._session.post(url.format(command=command), files={
#                     'media': (__file__, binary_media, mime_type)
#                 })
#
#                 if append_upload_response.status_code != 204:
#                     self._logger.log(
#                         f"[-] failed to upload media files.\n\terrors: file is too large", True)
#                     self._is_logged = False
#                     return False
#
#                 # finalize upload
#                 command = 'FINALIZE'
#                 url = self.ENDPOINTS['upload_media'] + f"&media_id={media_id}"
#                 self._logger.log("\t[+] trying to finalize media request")
#                 finalize_upload_response = self._session.post(url.format(command=command))
#                 finalize_upload_response_json = finalize_upload_response.json()
#
#                 if finalize_upload_response_json.get('errors'):
#                     self._logger.log(
#                         f"[-] failed to upload media files.\n\terrors: "
#                         f"{finalize_upload_response_json['errors'][0]['message']}", True)
#                     self._is_logged = finalize_upload_response_json['errors'][0][
#                                           'code'] not in TwitterWebAPI.ERROR_CODES.get('LOCKED')
#                     return False
#
#                 self._logger.log(f"[*] file has been uploaded successfully.")
#                 return finalize_upload_response_json
#
#             except Exception as e:
#                 self._logger.log(f"[-] Failed to upload media: .\n\terrors: {e}", True)
#         return False
#
#     def addAltText(self, alt_text, media_id):
#         if self._is_logged:
#             try:
#                 self._logger.log(f"[*] Trying to add alt text to tweet")
#                 with self._session.post(
#                     self.ENDPOINTS['media_alt_text'],
#                     json=Payloads.altTextPayload(alt_text, media_id)
#                 ) as alt_text_response:
#                     if alt_text_response.status_code == 200:
#                         self._logger.log(f"[*] {self._username} added alt text to {media_id} successfully.")
#                         return True
#                     self._logger.log(
#                         f"[-] {self._username} failed to add alt text to {media_id}.\n\terrors: {alt_text_response.text}",
#                         True)
#             except Exception as e:
#                 self._logger.log(f"[-] {self._username} failed to add alt text to {media_id}.\n\terrors: {e}", True)
#         return False
#
#     def tweet(self, tweet_text, **kwargs):
#         if self.logged:
#             media_ids = kwargs.get('media', [])
#             tweet_type = kwargs.get('tweet_type', None)
#             tweet_id = kwargs.get('tweet_id', None)
#             attachment = kwargs.get('quote_url', None)
#             try:
#                 payload = Payloads.tweetPayload(tweet_type,
#                                                 operation=self.operations['CreateTweet'],
#                                                 tweet_id=tweet_id,
#                                                 media_ids=media_ids,
#                                                 tweet_text=tweet_text,
#                                                 attachment=attachment)
#
#                 url = self.ENDPOINTS['retweet'] % (self.operations['CreateRetweet']) if tweet_type == 'retweet' \
#                     else self.ENDPOINTS['create_tweet'] % self.operations['CreateTweet']
#
#                 self._logger.log(
#                     f"[*] {self._username} trying to {tweet_type if tweet_type else 'tweet'}: {tweet_text}")
#                 with self._session.post(url, json=payload) as tweet_response:
#                     tweet_response_json = tweet_response.json()
#
#                     if not tweet_response_json.get('errors'):
#                         if tweet_type in [None, 'quote', 'reply']:
#                             response = tweet_response_json['data']['create_tweet']['tweet_results']['result']['legacy']
#                             self._logger.log(
#                                 f"[*] {self._username} tweet created successfully: "
#                                 f"{response['created_at']}")
#                             return response['id_str']
#                         else:
#                             self._logger.log(f"[*] {self._username} {tweet_type} created successfully")
#                         return True
#                     else:
#                         self._logger.log(
#                             f"[-] {self._username} unable to create tweet.\n\terrors: {tweet_response_json['errors'][0]['message']}")
#                         self._is_logged = tweet_response_json['errors'][0]['code'] not in TwitterWebAPI.ERROR_CODES.get(
#                             'LOCKED')
#             except Exception as e:
#                 self._logger.log(f"[-] {self._username} can't tweet: {tweet_text}.\n\terrors: {e}", True)
#         return False
#
#     def reactTweet(self, tweet_id):
#         if self._is_logged:
#             try:
#                 self._logger.log(f"[*] Trying to favorite tweet: {tweet_id} to twitter api.")
#                 with self._session.post(
#                     self.ENDPOINTS['favorite_tweet'] % (self.operations['FavoriteTweet']),
#                     json=Payloads.reactPayload(tweet_id=tweet_id, operation=self.operations['FavoriteTweet'])
#                 ) as favorite_tweet_response:
#                     favorite_tweet_response_json = favorite_tweet_response.json()
#                     if not favorite_tweet_response_json.get('errors'):
#                         self._logger.log(f"[*] {self._username} tweet {tweet_id} has been favorite successfully.")
#                         return True
#                     self._logger.log(
#                         f"[-] failed to favorite tweet.\n\terrors: {favorite_tweet_response_json['errors'][0]['message']}",
#                         True)
#                     self._is_logged = favorite_tweet_response_json['errors'][0][
#                                           'code'] not in TwitterWebAPI.ERROR_CODES.get('LOCKED')
#             except Exception as e:
#                 self._logger.log(f"[-] {self._username}  Failed to favorite tweet: {tweet_id}.\n\terrors: {e}", True)
#         return False
#
#     def follow(self, user_id):
#         if self._is_logged:
#             try:
#                 self._logger.log(f"[*] Trying to follow: {user_id} to twitter api.")
#                 with self._session.post(
#                     self.ENDPOINTS['follow'],
#                     data=Payloads.followPayload(user_id=user_id)
#                 ) as follow_response:
#                     follow_response_json = follow_response.json()
#
#                     if not follow_response_json.get('errors'):
#                         self._logger.log(
#                             f"[*] {self._username} -> {follow_response_json['screen_name']} has been followed successfully.")
#                         return follow_response_json
#                     self._logger.log(
#                         f"[-] failed to follow {user_id}.\n\terrors: {follow_response_json['errors'][0]['message']}",
#                         True)
#                     self._is_logged = follow_response_json['errors'][0][
#                                           'code'] not in TwitterWebAPI.ERROR_CODES.get('LOCKED')
#             except Exception as e:
#                 self._logger.log(f"[-] {self._username}  Failed to follow: {user_id}.\n\terrors: {e}", True)
#         return False
#
#     def profileInfo(self, username=None, bio=None, country=None, profile_picture=None, cover_picture=None):
#         if self._is_logged:
#             self.__getTokens()
#             try:
#                 self._logger.log(f"[*] Trying to update profile info: {self._username} to twitter api.")
#                 if cover_picture is not None:
#                     cover_image: dict | bool = self.uploadMedia(cover_picture, "banner_image")
#                     if not cover_image:
#                         self._logger.log(f"[-] Failed to update cover picture: {self._username} to twitter api.")
#                     else:
#                         self._logger.log(f"[+] Trying to save cover image: {self._username} to twitter api.")
#                         self._session.post(self.ENDPOINTS['update_profile_cover'], data=Payloads.profilePayload(
#                             step='cover_pic', media_id=cover_image.get('media_id_string')
#                         ))
#
#                 if profile_picture is not None:
#                     profile_image = self.uploadMedia(profile_picture, None)
#                     if not profile_image:
#                         self._logger.log(f"[-] Failed to update profile picture: {self._username} to twitter api.")
#                     else:
#                         self._logger.log(f"[+] Trying to save profile image: {self._username} to twitter api.")
#                         self._session.post(self.ENDPOINTS['update_profile_image'], data=Payloads.profilePayload(
#                             step='profile_pic', media_id=profile_image.get('media_id_string')
#                         ))
#
#                 self._logger.log(f'Trying to update profile info: {self._username} to twitter api.')
#                 with self._session.post(self.ENDPOINTS['update_profile'],
#                                         data=Payloads.profilePayload(step='profile_info',
#                                                                      username=username,
#                                                                      bio=bio,
#                                                                      country=country)) as update_profile_info_response:
#                     update_profile_info_response_json = update_profile_info_response.json()
#                     if not update_profile_info_response_json.get('errors'):
#                         self._logger.log(f"[*] {self._username} profile has been updated successfully.")
#                         return True
#                     self._logger.log(
#                         f"[-] {self._username} failed to update profile info.\n\terrors: "
#                         f"{update_profile_info_response_json['errors'][0]['message']}",
#                         True)
#                     self._is_logged = update_profile_info_response_json['errors'][0][
#                                           'code'] not in TwitterWebAPI.ERROR_CODES.get('LOCKED')
#             except Exception as e:
#                 self._logger.log(f"[-] {self._username}  Failed to update profile.\n\terrors: {e}", True)
#         return False
#
#     def notify(self, user_id):
#         if self._is_logged:
#             try:
#                 self._logger.log(f"[*] Trying to make notification: {user_id} to twitter api.")
#                 with self._session.post(
#                     self.ENDPOINTS['notifications'],
#                     data=Payloads.notificationPayload(user_id=user_id)
#                 ) as notification_response:
#                     notification_response_json = notification_response.json()
#
#                     if not notification_response_json.get('errors'):
#                         self._logger.log(
#                             f"[*] {self._username} "
#                             f"-> "
#                             f"{notification_response_json['relationship']['target']['screen_name']}"
#                             f" notification has been enabled successfully.")
#                         return notification_response_json
#                     self._logger.log(
#                         f"[-] failed to enable notification {user_id}."
#                         f"\n\terrors: {notification_response_json['errors'][0]['message']}",
#                         True)
#                     self._is_logged = notification_response_json['errors'][0][
#                                           'code'] not in TwitterWebAPI.ERROR_CODES.get('LOCKED')
#             except Exception as e:
#                 self._logger.log(f"[-] {self._username}  Failed to enable notification: {user_id}.\n\terrors: {e}", True)
#         return False
#
#     def private(self):
#         if self._is_logged:
#             try:
#                 self._logger.log(f"[*] Trying to make: {self._username} private to twitter api.")
#                 with self._session.post(
#                         self.ENDPOINTS['settings'],
#                         data=Payloads.settingsPayload(step='make_private')
#                 ) as private_response:
#                     private_response_json = private_response.json()
#                     if not private_response_json.get('errors'):
#                         self._logger.log(f"[*] {private_response_json['screen_name']} has been protected successfully.")
#                         return True
#                     self._logger.log(
#                         f"[-] failed to make {self._username} private.\n\terrors: "
#                         f"{private_response_json['errors'][0]['message']}",
#                         True)
#                     self._is_logged = private_response_json['errors'][0][
#                                           'code'] not in TwitterWebAPI.ERROR_CODES.get('LOCKED')
#             except Exception as e:
#                 self._logger.log(f"[-] failed to make {self._username} private.\n\terrors: {e}", True)
#
#     def verifyPassword(self, password):
#         if self._is_logged:
#             try:
#                 self._logger.log(f"[+] Trying to verify: {self._username} password")
#                 with self._session.post(self.ENDPOINTS['verify_password'],
#                                         data=Payloads.verifyPassword(password)) as verify_password_response:
#                     if verify_password_response.json().get('status') == 'ok':
#                         self._logger.log(f'[+] {self._username} password verified successfully')
#                         return True
#                     self._logger.log(f"[-] Failed to verify {self._username} password.")
#             except Exception as e:
#                 self._logger.log(f"[-] Failed to verify {self._username} password.\n\terrors: {e}", True)
#
#     def changeAccountUsername(self, username):
#         if self._is_logged:
#             try:
#                 password_status = True
#                 username_availability = False
#                 self._logger.log(f"[*] Trying to change: {self._username} username from twitter api.")
#                 with self._session.get(
#                     self.ENDPOINTS['personalization']
#                 ) as init_response:
#                     errors = init_response.json().get('errors')
#                     if errors and errors[0]['code'] == 401:
#                         password_status = self.verifyPassword(password=self._password)
#                 if password_status:
#                     self._logger.log('[+] Trying to check username availability')
#                     with self._session.get(self.ENDPOINTS['username_availability'], params={
#                         'username': username
#                     }) as username_availability_response:
#                         username_availability = username_availability_response.json().get('valid')
#                     self._logger.log(f"[+] Username availability: {username_availability}")
#                 if username_availability:
#                     with self._session.post(self.ENDPOINTS['settings'],
#                                             data=Payloads.usernameChange(username)) as settings_response:
#                         settings_response_json = settings_response.json()
#                         if settings_response_json.get('errors'):
#                             self._logger.log(
#                                 f"[-] failed to change username."
#                                 f"\n\terrors: {settings_response_json['errors'][0]['message']}",
#                                 True)
#                             self._is_logged = settings_response_json['errors'][0][
#                                                   'code'] not in TwitterWebAPI.ERROR_CODES.get('LOCKED')
#                         else:
#                             self._logger.log(f"{self._username} changed to {username} successfully")
#                             self._username = settings_response_json.get('screen_name')
#             except Exception as e:
#                 self._logger.log(f"[-] failed to change {self._username} username.\n\terrors: {e}")
#
#     def errors(self):
#         for key, item in self.ERROR_CODES.items():
#             if self._errors in item:
#                 return key
#
#     @property
#     def session(self):
#         return self._session
#
#     @property
#     def logged(self):
#         return self._is_logged
#
#
# if __name__ == "__main__":
#     "MarkusBest9:kS5lwkcivhf:vitaliyef4vcm@outlook.com:kS5lwkcivhf"
#     account_username = "islamTPCT12324"
#     account_password = "kS5lwkcivhf"
#     account_email = "vitaliyef4vcm@outlook.com"
#     account_api = TwitterWebAPI()
#     account_api.Login(account_username, account_password, account_email)
#     account_api.changeAccountUsername("MarkusBest9")