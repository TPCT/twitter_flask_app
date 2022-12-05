import random
import json
from urllib.parse import quote


class Payloads:
    @staticmethod
    def loginPayload(step, **kwargs):
        response = {}
        if step == 'flow_token':
            response = {
                'subtask_inputs': []}
        elif step == 'username':
            response = {"subtask_inputs": [
                {
                    "subtask_id": "LoginEnterUserIdentifierSSO",
                    "settings_list": {
                        "setting_responses": [
                            {
                                "key": "user_identifier",
                                "response_data": {
                                    "text_data": {
                                        "result": kwargs.get('username')
                                    }
                                }
                            }
                        ],
                        "link": "next_link"
                    }
                }
            ]}
        elif step == 'identifier':
            response = {
                "subtask_inputs": [
                    {
                        "subtask_id": "LoginEnterAlternateIdentifierSubtask",
                        "enter_text": {
                            "text": kwargs.get('email'),
                            "link": "next_link"
                        }
                    }
                ]
            }
        elif step == 'password':
            response = {"subtask_inputs": [
                {
                    "subtask_id": "LoginEnterPassword",
                    "enter_password": {
                        "password": kwargs.get('password'),
                        "link": "next_link"
                    }
                }
            ]}
        elif step == 'verify':
            response = {
                "subtask_inputs": [
                    {
                        "subtask_id": "LoginAcid",
                        "enter_text": {
                            "text": kwargs.get('email'),
                            "link": "next_link"
                        }
                    }
                ]
            }
        elif step == 'duplication':
            response = {"subtask_inputs": [
                {"subtask_id": "AccountDuplicationCheck",
                 "check_logged_in_account": {
                     "link": "AccountDuplicationCheck_False"}}]}
        response.update({'flow_token': kwargs.get('flow_token')})
        return response

    @staticmethod
    def tweetPayload(step, **kwargs):
        response = {
            "variables": {
                "tweet_text": f"{kwargs.get('tweet_text')}",
                "media": {
                    "media_entities": [
                        {"media_id": media_id, "tagged_users": []} for media_id
                        in kwargs.get('media_ids')],
                    "possibly_sensitive": False
                },
                "semantic_annotation_ids": [],
                "withDownvotePerspective": False,
                "withReactionsMetadata": False,
                "withReactionsPerspective": False,
                "withSuperFollowsTweetFields": True,
                "withSuperFollowsUserFields": True,
                "dark_request": False
            },
            "features": {
                "dont_mention_me_view_api_enabled": True,
                "responsive_web_uc_gql_enabled": True,
                "vibe_api_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": False,
                "interactive_text_enabled": True,
                "responsive_web_text_conversations_enabled": False,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": False,
                "responsive_web_enhance_cards_enabled": True,
                "unified_cards_ad_metadata_container_dynamic_card_content_query_enabled": False,
                "tweetypie_unmention_optimization_enabled": True
            }}
        if step == 'retweet':
            response = {
                "variables": {
                    "tweet_id": f"{kwargs.get('tweet_id')}",
                    "dark_request": False
                },
            }
        elif step == 'quote':
            response['variables'].update({
                "attachment_url": f"{kwargs.get('attachment')}",
            })
        elif step == 'reply':
            response['variables'].update({
                "reply": {
                    "in_reply_to_tweet_id": f"{kwargs.get('tweet_id')}",
                    "exclude_reply_user_ids": []
                }
            })

        response.update({
            "queryId": kwargs.get('operation')
        })
        return response

    @staticmethod
    def reactPayload(**kwargs):
        return {"variables": {
            "tweet_id": f"{kwargs.get('tweet_id')}"
        },
            "queryId": kwargs.get('operation')
        }

    @staticmethod
    def accountCheckPayload(check_type, url, **kwargs):
        if check_type == 'search':
            return url + ("?include_profile_interstitial_type=1"
                          "&include_blocking=0"
                          "&include_blocked_by=0"
                          "&include_followed_by=0"
                          "&include_want_retweets=0"
                          "&include_mute_edge=0"
                          "&include_can_dm=0"
                          "&include_can_media_tag=0"
                          "&include_ext_has_nft_avatar=0"
                          "&skip_status=0"
                          "&cards_platform=Web-12"
                          "&include_cards=0"
                          "&include_ext_alt_text=false"
                          "&include_ext_limited_action_results=false"
                          "&include_quote_count=false"
                          "&include_reply_count=0"
                          "&tweet_mode=extended"
                          "&include_ext_collab_control=false"
                          "&include_entities=true"
                          "&include_user_entities=true"
                          "&include_ext_media_color=true"
                          "&include_ext_media_availability=true"
                          "&include_ext_sensitive_media_warning=true"
                          "&include_ext_trusted_friends_metadata=true"
                          "&send_error_codes=true"
                          "&simple_quoted_tweet=true"
                          f"&q={kwargs.get('username')}"
                          f"&result_filter={kwargs.get('search_type', 'tweets')}"
                          "&count=20"
                          "&query_source=typeahead_click"
                          "&pc=1"
                          "&spelling_corrections=1"
                          "&include_ext_edit_control=true"
                          "&ext=mediaStats,highlightedLabel,"
                          "hasNftAvatar,voiceInfo,enrichments,"
                          "superFollowMetadata,unmentionInfo,e"
                          "ditControl,vibe")
        if check_type == 'check':
            return url + ('variables={"screen_name":"' +
                          kwargs.get('username') + '",'
                                                   '"withSafetyModeUserFields":true,'
                                                   '"withSuperFollowsUserFields":true'
                                                   '}&features={'
                                                   '"responsive_web_graphql_timeline_navigation_enabled":false}')

    @staticmethod
    def altTextPayload(alt_text, media_id):
        return {
            "media_id": media_id,
            "alt_text": {
                "text": alt_text
            }
        }

    @staticmethod
    def followPayload(user_id):
        return {
            'include_profile_interstitial_type': 1,
            'include_blocking': 1,
            'include_blocked_by': 1,
            'include_followed_by': 1,
            'include_want_retweets': 1,
            'include_mute_edge': 1,
            'include_can_dm': 1,
            'include_can_media_tag': 1,
            'include_ext_has_nft_avatar': 1,
            'skip_status': 1,
            'user_id': user_id
        }

    @staticmethod
    def profilePayload(step, **kwargs):
        if step == 'cover_pic' or step == 'profile_pic':
            return {
                'include_profile_interstitial_type': 1,
                'include_blocking': 1,
                'include_blocked_by': 1,
                'include_followed_by': 1,
                'include_want_retweets': 1,
                'include_mute_edge': 1,
                'include_can_dm': 1,
                'include_can_media_tag': 1,
                'include_ext_has_nft_avatar': 1,
                'skip_status': 1,
                'return_user': 'true',
                'media_id': kwargs.get('media_id')
            }
        elif step == 'profile_info':
            return {
                'birthdate_day': random.randint(1, 28),
                'birthdate_month': random.randint(1, 12),
                'birthdate_year': random.randint(1950, 1990),
                'birthdate_visibility': 'mutualfollow',
                'birthdate_year_visibility': 'self',
                'displayNameMaxLength': 50,
                'name': kwargs.get('username'),
                'description': kwargs.get('bio'),
                'location': kwargs.get('country')
            }

    @staticmethod
    def settingsPayload(step):
        if step == "make_private":
            return {
                'include_mention_filter': 'true',
                'include_nsfw_user_flag': 'true',
                'include_nsfw_admin_flag': 'true',
                'include_ranked_timeline': 'true',
                'include_alt_text_compose': 'true',
                'protected': 'true'
            }

    @staticmethod
    def notificationPayload(user_id):
        return {
            'include_profile_interstitial_type': 1,
            'include_blocking': 1,
            'include_blocked_by': 1,
            'include_followed_by': 1,
            'include_want_retweets': 1,
            'include_mute_edge': 1,
            'include_can_dm': 1,
            'include_can_media_tag': 1,
            'include_ext_has_nft_avatar': 1,
            'skip_status': 1,
            'cursor': -1,
            'id': user_id,
            'device': True
        }

    @staticmethod
    def verifyPassword(password):
        return {
            'password': password
        }

    @staticmethod
    def usernameChange(username):
        return {
            "include_mention_filter": True,
            'include_nsfw_user_flag': True,
            'include_nsfw_admin_flag': True,
            'include_ranked_timeline': True,
            'include_alt_text_compose': True,
            'screen_name': username
        }

    @staticmethod
    def AccountIdVariablesPayload(username):
        variables = {"screen_name": f"{username}", "withSafetyModeUserFields": True, "withSuperFollowsUserFields": True}
        variables = json.dumps(variables).replace(' ', '')
        return quote(variables)

    @staticmethod
    def AccountIdFeaturesPayload():
        features = {"verified_phone_label_enabled": False, "responsive_web_graphql_timeline_navigation_enabled": True}
        features = json.dumps(features).replace(' ', '')
        return quote(features)

    @staticmethod
    def TweetsVariablesPayload(user_id):
        variables = {"userId": f"{user_id}", "count": 40,
                     "includePromotedContent": True, "withQuickPromoteEligibilityTweetFields": True,
                     "withSuperFollowsUserFields": True, "withDownvotePerspective": False,
                     "withReactionsMetadata": False, "withReactionsPerspective": False,
                     "withSuperFollowsTweetFields": True, "withVoice": True, "withV2Timeline": True}
        variables = json.dumps(variables).replace(' ', '')
        return quote(variables)

    @staticmethod
    def TweetsFeaturesPayload():
        features = {"verified_phone_label_enabled": False, "responsive_web_graphql_timeline_navigation_enabled": True,
                    "unified_cards_ad_metadata_container_dynamic_card_content_query_enabled": True,
                    "tweetypie_unmention_optimization_enabled": True, "responsive_web_uc_gql_enabled": True,
                    "vibe_api_enabled": True, "responsive_web_edit_tweet_api_enabled": True,
                    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                    "standardized_nudges_misinfo": True,
                    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
                    "interactive_text_enabled": True, "responsive_web_text_conversations_enabled": False,
                    "responsive_web_enhance_cards_enabled": True, "dont_mention_me_view_api_enabled": False}
        features = json.dumps(features).replace(' ', '')
        return quote(features)

    @staticmethod
    def TweetsAndRepliesVariablesPayload(user_id):
        variables = {"userId": f"{user_id}", "count": 40,
                     "includePromotedContent": True, "withQuickPromoteEligibilityTweetFields": True,
                     "withSuperFollowsUserFields": True, "withDownvotePerspective": False,
                     "withReactionsMetadata": False, "withReactionsPerspective": False,
                     "withSuperFollowsTweetFields": True, "withVoice": True, "withV2Timeline": True}
        variables = json.dumps(variables).replace(' ', '')
        return quote(variables)

    @staticmethod
    def TweetsAndRepliesFeaturesPayload():
        features = {"verified_phone_label_enabled": False, "responsive_web_graphql_timeline_navigation_enabled": True,
                    "unified_cards_ad_metadata_container_dynamic_card_content_query_enabled": True,
                    "tweetypie_unmention_optimization_enabled": True, "responsive_web_uc_gql_enabled": True,
                    "vibe_api_enabled": True, "responsive_web_edit_tweet_api_enabled": True,
                    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                    "standardized_nudges_misinfo": True,
                    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
                    "interactive_text_enabled": True, "responsive_web_text_conversations_enabled": False,
                    "responsive_web_enhance_cards_enabled": True, "dont_mention_me_view_api_enabled": False}
        features = json.dumps(features).replace(' ', '')
        return quote(features)

    @staticmethod
    def LikesVariablesPayload(user_id):
        variables = {"userId": f"{user_id}", "count": 40,
                     "includePromotedContent": True, "withQuickPromoteEligibilityTweetFields": True,
                     "withSuperFollowsUserFields": True, "withDownvotePerspective": False,
                     "withReactionsMetadata": False, "withReactionsPerspective": False,
                     "withSuperFollowsTweetFields": True, "withVoice": True, "withV2Timeline": True}
        variables = json.dumps(variables).replace(' ', '')
        return quote(variables)

    @staticmethod
    def LikesFeaturesPayload():
        features = {"verified_phone_label_enabled": False, "responsive_web_graphql_timeline_navigation_enabled": True,
                    "unified_cards_ad_metadata_container_dynamic_card_content_query_enabled": True,
                    "tweetypie_unmention_optimization_enabled": True, "responsive_web_uc_gql_enabled": True,
                    "vibe_api_enabled": True, "responsive_web_edit_tweet_api_enabled": True,
                    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                    "standardized_nudges_misinfo": True,
                    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
                    "interactive_text_enabled": True, "responsive_web_text_conversations_enabled": False,
                    "responsive_web_enhance_cards_enabled": True, "dont_mention_me_view_api_enabled": False}
        features = json.dumps(features).replace(' ', '')
        return quote(features)

    @staticmethod
    def MediaVariablesPayload(user_id):
        variables = {"userId": f"{user_id}", "count": 40,
                     "includePromotedContent": True, "withQuickPromoteEligibilityTweetFields": True,
                     "withSuperFollowsUserFields": True, "withDownvotePerspective": False,
                     "withReactionsMetadata": False, "withReactionsPerspective": False,
                     "withSuperFollowsTweetFields": True, "withVoice": True, "withV2Timeline": True}
        variables = json.dumps(variables).replace(' ', '')
        return quote(variables)

    @staticmethod
    def MediaFeaturesPayload():
        features = {"verified_phone_label_enabled": False, "responsive_web_graphql_timeline_navigation_enabled": True,
                    "unified_cards_ad_metadata_container_dynamic_card_content_query_enabled": True,
                    "tweetypie_unmention_optimization_enabled": True, "responsive_web_uc_gql_enabled": True,
                    "vibe_api_enabled": True, "responsive_web_edit_tweet_api_enabled": True,
                    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                    "standardized_nudges_misinfo": True,
                    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
                    "interactive_text_enabled": True, "responsive_web_text_conversations_enabled": False,
                    "responsive_web_enhance_cards_enabled": True, "dont_mention_me_view_api_enabled": False}
        features = json.dumps(features).replace(' ', '')
        return quote(features)
