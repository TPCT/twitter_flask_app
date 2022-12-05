from API.TwitterBaseApi import TwitterBaseApi
from API.AccountSearch import AccountSearch
from API.Payloads import Payloads
import requests


class TwitterAccount(TwitterBaseApi):
    def __loginFlowTokens(self):
        try:
            self._logger.log("\t[+] trying to fetch login flow token.")
            flow_1_response = self._session.post(self.ENDPOINTS['task'], params={
                "flow_name": 'login'
            }, verify=False, json=Payloads.loginPayload('flow_token'))
            self._flow_token = flow_1_response.json()['flow_token']
            self._logger.log("\t[+] login flow fetched successfully.")

            self._logger.log("\t[+] trying to get flow response token")
            flow_2_response = self._session.post(self.ENDPOINTS['task'], verify=False,
                                                 json=Payloads.loginPayload('flow_token', flow_token=self._flow_token))
            self._flow_token = flow_2_response.json()['flow_token']
            self._logger.log("\t[+] flow response token has been fetched successfully.")
            return True
        except Exception as e:
            self._logger.log(f"[-] couldn't get flow tokens from twitter.\n\terrors: {e}", True)

    def __loginUsernameFlow(self):
        try:
            self._logger.log("\t[+] trying to fetch username response.")
            username_response = self._session.post(self.ENDPOINTS['task'], verify=False,
                                                   json=Payloads.loginPayload('username', username=self._username,
                                                                              flow_token=self._flow_token))
            username_response_json = username_response.json()
            if not username_response_json.get('errors'):
                self._flow_token = username_response_json['flow_token']
                self._logger.log("\t[+] username response token has been fetched successfully.")
                return True
            self._logger.log('\t[-] invalid authentication.\n\t\terrors:' +
                             username_response_json['errors'][0]['message'], True)
            self._errors = username_response_json['errors'][0]['code'] if not self._errors else self._errors
        except Exception as e:
            self._logger.log(f"[-] couldn't get username flow from twitter.\n\terrors: {e}", True)
        return False

    def __loginIdentifierFlow(self):
        try:
            self._logger.log("\t[+] trying to fetch identifier response.")
            username_response = self._session.post(self.ENDPOINTS['task'], verify=False,
                                                   json=Payloads.loginPayload('identifier', email=self._email,
                                                                              flow_token=self._flow_token))
            username_response_json = username_response.json()
            if not username_response_json.get('errors'):
                self._flow_token = username_response_json['flow_token']
                self._logger.log("\t[+] username response token has been fetched successfully.")
                return True
            self._logger.log('\t[-] invalid authentication.\n\t\terrors:' +
                             username_response_json['errors'][0]['message'], True)
            self._errors = username_response_json['errors'][0]['code'] if not self._errors else self._errors
        except Exception as e:
            self._logger.log(f"[-] couldn't get identifier flow from twitter.\n\terrors: {e}", True)
        return False

    def __loginPasswordFlow(self):
        try:
            self._logger.log("\t[+] trying to fetch password response.")
            password_response = self._session.post(self.ENDPOINTS['task'], verify=False,
                                                   json=Payloads.loginPayload('password',
                                                                              flow_token=self._flow_token,
                                                                              password=self._password))
            password_response_json = password_response.json()
            if not password_response_json.get('errors'):
                self._flow_token = password_response_json['flow_token']
                self._user_id = password_response_json['subtasks'][0]['check_logged_in_account']['user_id']

                self._logger.log("\t[+] password response token has been fetched successfully.")
                self._logger.log("[*] user_id: %s" % self._user_id)
                return True
            self._logger.log('\t[-] invalid authentication.\n\t\terrors:' +
                             password_response_json['errors'][0]['message'], True)
            self._errors = password_response_json['errors'][0]['code'] if not self._errors else self._errors
        except Exception as e:
            self._logger.log(f"[-] couldn't get password flow from twitter.\n\terrors: {e}", True)
        return False

    def __accountDuplicationFlow(self):
        try:
            self._logger.log("[*] Trying to check account duplication")
            authentication_token_response = self._session.post(self.ENDPOINTS['task'], verify=False,
                                                               json=Payloads.loginPayload('duplication',
                                                                                          flow_token=self._flow_token))
            authentication_token_response_json = authentication_token_response.json()
            self._flow_token = authentication_token_response_json['flow_token']

            if authentication_token_response_json.get('subtasks', [{}])[0].get('subtask_id') == "LoginAcid":
                self._logger.log("[*] email login is required")
                email_response = self._session.post(self.ENDPOINTS['task'],
                                                    json=Payloads.loginPayload('verify',
                                                                               flow_token=self._flow_token,
                                                                               email=self._email))
                email_response_json = email_response.json()
                if not email_response_json.get('errors'):
                    self._logger.log("[*] email login has succeeded successfully.")
                    return True
                self._logger.log('\t[-] invalid authentication.\n\t\terrors:' +
                                 email_response_json['errors'][0]['message'], True)
                self._errors = email_response_json['errors'][0]['code'] if not self._errors else self._errors
                return False
            self._logger.log("[*] email login has succeeded successfully.")
            return True
        except Exception as e:
            self._logger.log(f"[-] couldn't get account duplication from twitter.\n\terrors: {e}", True)
        return False

    def __login(self, username, password, email):
        try:
            self._username = username
            self._email = email
            self._password = password
            self._logger.log("[*] trying to login to twitter api")
            self.__loginFlowTokens()

            if not self.__loginUsernameFlow():
                return False

            # if not self.__loginIdentifierFlow():
            #     return False

            if not self.__loginPasswordFlow():
                return False

            if not self.__accountDuplicationFlow():
                return False

            self._logger.log("[*] logged in twitter api successfully")
            return True
        except Exception as e:
            self._logger.log(f"[-] couldn't login to twitter.\n\terrors: {e}", True)
        return False
    
    def getAccountInfo(self):
        return {
            'username': self._username,
            'password': self._password,
            'email': self._email,
            'user_id': self._user_id
        }

    def Login(self, username, password, email, proxy_user=None, proxy_password=None, proxy_ip=None, proxy_port=None):
        self._session = requests.Session()
        self._session.headers.update({
            'Origin': 'https://twitter.com',
            'Referer': 'https://twitter.com/',
            'x-twitter-client-language': 'en',
            'x-twitter-active-user': 'yes',
            'Authorization': self.AUTHORIZATION_TOKEN
        })
        if all([proxy_user, proxy_password, proxy_ip, proxy_port]):
            self._session.proxies.update({
                'http': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}',
                'https': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}'
            })
        self._is_logged = self._getTokens()
        if not self._is_logged:
            self._logger.log("[-] unable to login to twitter api.\n\terrors: can't get the required tokens", True)
            return False
        self._is_logged = self.__login(username, password, email) if self._is_logged else False
        self._is_logged = self._getCSRFToken() if self._is_logged else False
        # check_account = None
        # while check_account is None:
        #     check_account = AccountSearch().checkAccount(self._username,
        #                                                  proxy_user=proxy_user,
        #                                                  proxy_password=proxy_password,
        #                                                  proxy_ip=proxy_ip,
        #                                                  proxy_port=proxy_port)['active'] if self._is_logged else False
        # self._is_logged = check_account
        return self._is_logged

    def uploadMedia(self, binary_media, category="tweet_image"):
        if self._is_logged:
            try:
                self._logger.log(f"[*] Trying to upload media to twitter api.")
                command = "INIT"
                mime_type = 'image/png'
                content_length = len(binary_media) if binary_media is not None and len(binary_media) else 0

                url = self.ENDPOINTS[
                          'upload_media'] + "&total_bytes={length}&media_type={media_type}&" + ("media_category={"
                                                                                                "media_category}"
                                                                                                if category else "")

                self._logger.log("\t[+] trying to initialize the request")
                initial_upload_response = self._session.post(url.format(command=command,
                                                                        length=content_length,
                                                                        media_type=mime_type,
                                                                        media_category=category))
                initial_upload_response_json = initial_upload_response.json()
                if initial_upload_response_json.get('errors'):
                    self._logger.log(
                        f"[-] failed to upload media files.\n\terrors: "
                        f"{initial_upload_response_json['errors'][0]['message']}",
                        True)
                    self._is_logged = initial_upload_response_json['errors'][0][
                                          'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
                    self._errors = initial_upload_response_json['errors'][0][
                        'code'] if not self._errors else self._errors
                    return False

                # append upload
                command = 'APPEND'
                media_id = initial_upload_response_json['media_id']
                segment_index = 0
                url = self.ENDPOINTS['upload_media'] + f"&media_id={media_id}&segment_index={segment_index}"
                self._logger.log("\t[+] trying to append media to the request")
                append_upload_response = self._session.post(url.format(command=command), files={
                    'media': (__file__, binary_media, mime_type)
                })

                if append_upload_response.status_code != 204:
                    self._logger.log(
                        f"[-] failed to upload media files.\n\terrors: file is too large", True)
                    self._is_logged = False
                    return False

                # finalize upload
                command = 'FINALIZE'
                url = self.ENDPOINTS['upload_media'] + f"&media_id={media_id}"
                self._logger.log("\t[+] trying to finalize media request")
                finalize_upload_response = self._session.post(url.format(command=command))
                finalize_upload_response_json = finalize_upload_response.json()

                if finalize_upload_response_json.get('errors'):
                    self._logger.log(
                        f"[-] failed to upload media files.\n\terrors: "
                        f"{finalize_upload_response_json['errors'][0]['message']}", True)
                    self._is_logged = finalize_upload_response_json['errors'][0][
                                          'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
                    return False

                self._logger.log(f"[*] file has been uploaded successfully.")
                return finalize_upload_response_json

            except Exception as e:
                self._logger.log(f"[-] Failed to upload media: .\n\terrors: {e}", True)
        return False

    def addAltText(self, alt_text, media_id):
        if self._is_logged:
            try:
                self._logger.log(f"[*] Trying to add alt text to tweet")
                with self._session.post(
                        self.ENDPOINTS['media_alt_text'],
                        json=Payloads.altTextPayload(alt_text, media_id)
                ) as alt_text_response:
                    if alt_text_response.status_code == 200:
                        self._logger.log(f"[*] {self._username} added alt text to {media_id} successfully.")
                        return True
                    self._logger.log(
                        f"[-] {self._username} failed to add alt text to {media_id}.\n\terrors: {alt_text_response.text}",
                        True)
            except Exception as e:
                self._logger.log(f"[-] {self._username} failed to add alt text to {media_id}.\n\terrors: {e}", )
        return False

    def tweet(self, tweet_text, **kwargs):
        if self.logged:
            media_ids = kwargs.get('media', [])
            tweet_type = kwargs.get('tweet_type', None)
            tweet_id = kwargs.get('tweet_id', None)
            attachment = kwargs.get('quote_url', None)
            try:
                payload = Payloads.tweetPayload(tweet_type,
                                                operation=self.operations['CreateTweet'],
                                                tweet_id=tweet_id,
                                                media_ids=media_ids,
                                                tweet_text=tweet_text,
                                                attachment=attachment)

                url = self.ENDPOINTS['retweet'] % (self.operations['CreateRetweet']) if tweet_type == 'retweet' \
                    else self.ENDPOINTS['create_tweet'] % self.operations['CreateTweet']

                self._logger.log(
                    f"[*] {self._username} trying to {tweet_type if tweet_type else 'tweet'}: {tweet_text}")
                with self._session.post(url, json=payload) as tweet_response:
                    tweet_response_json = tweet_response.json()

                    if not tweet_response_json.get('errors'):
                        if tweet_type in [None, 'quote', 'reply']:
                            response = tweet_response_json['data']['create_tweet']['tweet_results']['result']['legacy']
                            self._logger.log(
                                f"[*] {self._username} tweet created successfully: "
                                f"{response['created_at']}")
                            return response['id_str']
                        else:
                            self._logger.log(f"[*] {self._username} {tweet_type} created successfully")
                        return True
                    else:
                        self._logger.log(
                            f"[-] {self._username} unable to create tweet.\n\terrors: {tweet_response_json['errors'][0]['message']}")
                        self._is_logged = tweet_response_json['errors'][0]['code'] not in TwitterBaseApi.ERROR_CODES.get(
                            'LOCKED')
            except Exception as e:
                self._logger.log(f"[-] {self._username} can't tweet: {tweet_text}.\n\terrors: {e}", True)
        return False

    def reactTweet(self, tweet_id):
        if self._is_logged:
            try:
                self._logger.log(f"[*] Trying to favorite tweet: {tweet_id} to twitter api.")
                with self._session.post(
                        self.ENDPOINTS['favorite_tweet'] % (self.operations['FavoriteTweet']),
                        json=Payloads.reactPayload(tweet_id=tweet_id, operation=self.operations['FavoriteTweet'])
                ) as favorite_tweet_response:
                    favorite_tweet_response_json = favorite_tweet_response.json()
                    if not favorite_tweet_response_json.get('errors'):
                        self._logger.log(f"[*] {self._username} tweet {tweet_id} has been favorite successfully.")
                        return True
                    self._logger.log(
                        f"[-] failed to favorite tweet.\n\terrors: {favorite_tweet_response_json['errors'][0]['message']}",
                        True)
                    self._is_logged = favorite_tweet_response_json['errors'][0][
                                          'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
            except Exception as e:
                self._logger.log(f"[-] {self._username}  Failed to favorite tweet: {tweet_id}.\n\terrors: {e}")
        return False

    def follow(self, user_id):
        if self._is_logged:
            try:
                self._logger.log(f"[*] Trying to follow: {user_id} to twitter api.")
                with self._session.post(
                        self.ENDPOINTS['follow'],
                        data=Payloads.followPayload(user_id=user_id)
                ) as follow_response:
                    follow_response_json = follow_response.json()

                    if not follow_response_json.get('errors'):
                        self._logger.log(
                            f"[*] {self._username} -> {follow_response_json['screen_name']} has been followed successfully.")
                        return follow_response_json
                    self._logger.log(
                        f"[-] failed to follow {user_id}.\n\terrors: {follow_response_json['errors'][0]['message']}",
                        True)
                    self._logger.log(follow_response_json['errors'][0][
                                          'code'])
                    self._is_logged = follow_response_json['errors'][0][
                                          'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
            except Exception as e:
                self._logger.log(f"[-] {self._username}  Failed to follow: {user_id}.\n\terrors: {e}")
        return False

    def notify(self, user_id):
        if self._is_logged:
            try:
                self._logger.log(f"[*] Trying to make notification: {user_id} to twitter api.")
                with self._session.post(
                        self.ENDPOINTS['notifications'],
                        data=Payloads.notificationPayload(user_id=user_id)
                ) as notification_response:
                    notification_response_json = notification_response.json()

                    if not notification_response_json.get('errors'):
                        self._logger.log(
                            f"[*] {self._username} "
                            f"-> "
                            f"{notification_response_json['relationship']['target']['screen_name']}"
                            f" notification has been enabled successfully.")
                        return notification_response_json
                    self._logger.log(
                        f"[-] failed to enable notification {user_id}."
                        f"\n\terrors: {notification_response_json['errors'][0]['message']}",
                        True)
                    self._is_logged = notification_response_json['errors'][0][
                                          'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
            except Exception as e:
                self._logger.log(f"[-] {self._username}  Failed to enable notification: {user_id}.\n\terrors: {e}")
        return False

    def getTweets(self):
        try:
            self._logger.log(f"[*] Trying to get: {self._username} tweets.")
            with self._session.get(
                    self.ENDPOINTS['user_tweets'] % (self.operations['UserTweets']) +
                    f"?variables={Payloads.TweetsVariablesPayload(self._user_id)}"
                    f"&features={Payloads.TweetsFeaturesPayload()}",
            ) as tweets_response:
                tweets_response_json = tweets_response.json()
                if not tweets_response_json.get('errors'):
                    return len(tweets_response_json['data']
                               ['user']['result']['timeline_v2']
                               ['timeline']['instructions'][-1].get('entries', {}))
                self._logger.log(
                    f"[-] failed to get {self._username} tweets.\n\terrors: {tweets_response_json['errors'][0]['message']}",
                    True)
                self._is_logged = tweets_response_json['errors'][0][
                                      'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
        except Exception as e:
            self._logger.log(f"[-] failed to get {self._username} tweets.\n\terrors: {e}")

    def getTweetsAndReplies(self):
        try:
            self._logger.log(f"[*] Trying to get: {self._username} Tweets And Replies.")
            with self._session.get(
                    self.ENDPOINTS['user_tweets_and_replies'] % (self.operations['UserTweetsAndReplies']) +
                    f"?variables={Payloads.TweetsAndRepliesVariablesPayload(self._user_id)}"
                    f"&features={Payloads.TweetsAndRepliesFeaturesPayload()}",
            ) as tweets_response:
                tweets_response_json = tweets_response.json()
                if not tweets_response_json.get('errors'):
                    return len(tweets_response_json['data']
                               ['user']['result']['timeline_v2']
                               ['timeline']['instructions'][-1].get('entries', {}))
                self._logger.log(
                    f"[-] failed to get {self._username} Tweets And Replies.\n\terrors: {tweets_response_json['errors'][0]['message']}",
                    True)
                self._is_logged = tweets_response_json['errors'][0][
                                      'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
        except Exception as e:
            self._logger.log(f"[-] failed to get {self._username} Tweets And Replies.\n\terrors: {e}")

    def getUserLikes(self):
        try:
            self._logger.log(f"[*] Trying to get: {self._username} Likes.")
            with self._session.get(
                    self.ENDPOINTS['user_likes'] % (self.operations['UserLikes']) +
                    f"?variables={Payloads.LikesVariablesPayload(self._user_id)}"
                    f"&features={Payloads.LikesFeaturesPayload()}",
            ) as tweets_response:
                tweets_response_json = tweets_response.json()
                if not tweets_response_json.get('errors'):
                    return len(tweets_response_json['data']
                               ['user']['result']['timeline_v2']
                               ['timeline']['instructions'][-1].get('entries', {}))
                self._logger.log(
                    f"[-] failed to get {self._username} Likes.\n\terrors: {tweets_response_json['errors'][0]['message']}",
                    True)
                self._is_logged = tweets_response_json['errors'][0][
                                      'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
        except Exception as e:
            self._logger.log(f"[-] failed to get {self._username} Likes.\n\terrors: {e}")

    def getUserMedia(self):
        try:
            self._logger.log(f"[*] Trying to get: {self._username} Media.")
            with self._session.get(
                    self.ENDPOINTS['user_media'] % (self.operations['UserMedia']) +
                    f"?variables={Payloads.MediaVariablesPayload(self._user_id)}"
                    f"&features={Payloads.MediaFeaturesPayload()}",
            ) as tweets_response:
                tweets_response_json = tweets_response.json()
                if not tweets_response_json.get('errors'):
                    return len(tweets_response_json['data']
                               ['user']['result']['timeline_v2']
                               ['timeline']['instructions'][-1].get('entries', {}))
                self._logger.log(
                    f"[-] failed to get {self._username} Likes.\n\terrors: {tweets_response_json['errors'][0]['message']}",
                    True)
                self._is_logged = tweets_response_json['errors'][0][
                                      'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
        except Exception as e:
            self._logger.log(f"[-] failed to get {self._username} Likes.\n\terrors: {e}")

    def profileInfo(self, username=None, bio=None, country=None, profile_picture=None, cover_picture=None):
        if self._is_logged:
            self._getTokens()
            try:
                self._logger.log(f"[*] Trying to update profile info: {self._username} to twitter api.")
                if cover_picture is not None:
                    cover_image: dict | bool = self.uploadMedia(cover_picture, "banner_image")
                    if not cover_image:
                        self._logger.log(f"[-] Failed to update cover picture: {self._username} to twitter api.")
                    else:
                        self._logger.log(f"[+] Trying to save cover image: {self._username} to twitter api.")
                        self._session.post(self.ENDPOINTS['update_profile_cover'], data=Payloads.profilePayload(
                            step='cover_pic', media_id=cover_image.get('media_id_string')
                        ))

                if profile_picture is not None:
                    profile_image = self.uploadMedia(profile_picture, None)
                    if not profile_image:
                        self._logger.log(f"[-] Failed to update profile picture: {self._username} to twitter api.")
                    else:
                        self._logger.log(f"[+] Trying to save profile image: {self._username} to twitter api.")
                        self._session.post(self.ENDPOINTS['update_profile_image'], data=Payloads.profilePayload(
                            step='profile_pic', media_id=profile_image.get('media_id_string')
                        ))

                self._logger.log(f'Trying to update profile info: {self._username} to twitter api.')
                with self._session.post(self.ENDPOINTS['update_profile'],
                                        data=Payloads.profilePayload(step='profile_info',
                                                                     username=username,
                                                                     bio=bio,
                                                                     country=country)) as update_profile_info_response:
                    update_profile_info_response_json = update_profile_info_response.json()
                    if not update_profile_info_response_json.get('errors'):
                        self._logger.log(f"[*] {self._username} profile has been updated successfully.")
                        return True
                    self._logger.log(
                        f"[-] {self._username} failed to update profile info.\n\terrors: "
                        f"{update_profile_info_response_json['errors'][0]['message']}",
                        True)
                    self._is_logged = update_profile_info_response_json['errors'][0][
                                          'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
            except Exception as e:
                self._logger.log(f"[-] {self._username}  Failed to update profile.\n\terrors: {e}")
        return False

    def private(self):
        if self._is_logged:
            try:
                self._logger.log(f"[*] Trying to make: {self._username} private to twitter api.")
                with self._session.post(
                        self.ENDPOINTS['settings'],
                        data=Payloads.settingsPayload(step='make_private')
                ) as private_response:
                    private_response_json = private_response.json()
                    if not private_response_json.get('errors'):
                        self._logger.log(f"[*] {private_response_json['screen_name']} has been protected successfully.")
                        return True
                    self._logger.log(
                        f"[-] failed to make {self._username} private.\n\terrors: {private_response_json['errors'][0]['message']}",
                        True)
                    self._is_logged = private_response_json['errors'][0][
                                          'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
            except Exception as e:
                self._logger.log(f"[-] failed to make {self._username} private.\n\terrors: {e}")

    def verifyPassword(self, password):
        if self._is_logged:
            try:
                self._logger.log(f"[+] Trying to verify: {self._username} password")
                with self._session.post(self.ENDPOINTS['verify_password'],
                                        data=Payloads.verifyPassword(password)) as verify_password_response:
                    if verify_password_response.json().get('status') == 'ok':
                        self._logger.log(f'[+] {self._username} password verified successfully')
                        return True
                    self._logger.log(f"[-] Failed to verify {self._username} password.")
            except Exception as e:
                self._logger.log(f"[-] Failed to verify {self._username} password.\n\terrors: {e}", True)

    def changeAccountUsername(self, username):
        if self._is_logged:
            try:
                password_status = True
                username_availability = False
                self._logger.log(f"[*] Trying to change: {self._username} username from twitter api.")
                with self._session.get(
                    self.ENDPOINTS['personalization']
                ) as init_response:
                    errors = init_response.json().get('errors')
                    if errors and errors[0]['code'] == 401:
                        password_status = self.verifyPassword(password=self._password)
                if password_status:
                    self._logger.log('[+] Trying to check username availability')
                    with self._session.get(self.ENDPOINTS['username_availability'], params={
                        'username': username
                    }) as username_availability_response:
                        username_availability = username_availability_response.json().get('valid')
                    self._logger.log(f"[+] Username availability: {username_availability}")
                if username_availability:
                    with self._session.post(self.ENDPOINTS['settings'],
                                            data=Payloads.usernameChange(username)) as settings_response:
                        settings_response_json = settings_response.json()
                        if settings_response_json.get('errors'):
                            self._logger.log(
                                f"[-] failed to change username."
                                f"\n\terrors: {settings_response_json['errors'][0]['message']}",
                                True)
                            self._is_logged = settings_response_json['errors'][0][
                                                  'code'] not in TwitterBaseApi.ERROR_CODES.get('LOCKED')
                        else:
                            self._logger.log(f"{self._username} changed to {username} successfully")
                            self._username = settings_response_json.get('screen_name')
            except Exception as e:
                self._logger.log(f"[-] failed to change {self._username} username.\n\terrors: {e}")


if __name__ == "__main__":
    account_username = "Veronic56307074"
    account_password = "ybWY1i1k0mlJ9Di"
    account_mobile = "platorhotrei1984@outlook.com"
    twitter_account_api = TwitterAccount()
    twitter_account_api.Login(account_username, account_password, account_mobile)
