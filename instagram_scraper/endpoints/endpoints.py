from .instagram_query_id import InstagramQueryId

import urllib.parse
import json
from json import JSONEncoder


class Endpoints:

    BASE_URL = 'https://www.instagram.com'
    LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
    ACCOUNT_PAGE = 'https://www.instagram.com/{username}'
    MEDIA_LINK = 'https://www.instagram.com/p/{code}'
    ACCOUNT_MEDIAS = 'https://www.instagram.com/graphql/query/?query_hash=42323d64886122307be10013ad2dcc44&variables={variables}'
    ACCOUNT_JSON_INFO = 'https://www.instagram.com/{username}/?__a=1'
    MEDIA_JSON_INFO = 'https://www.instagram.com/p/{code}/?__a=1'
    MEDIA_JSON_BY_LOCATION_ID = 'https://www.instagram.com/explore/locations/{{facebookLocationId}}/?__a=1&max_id={{maxId}}'
    MEDIA_JSON_BY_TAG = 'https://www.instagram.com/explore/tags/{tag}/?__a=1&max_id={max_id}'
    GENERAL_SEARCH = 'https://www.instagram.com/web/search/topsearch/?query={query}'
    ACCOUNT_JSON_INFO_BY_ID = 'ig_user({userId}){id,username,external_url,full_name,profile_pic_url,biography,followed_by{count},follows{count},media{count},is_private,is_verified}'
    COMMENTS_BEFORE_COMMENT_ID_BY_CODE = 'https://www.instagram.com/graphql/query/?query_hash=33ba35852cb50da46f5b5e889df7d159&variables={variables}'
    LAST_LIKES_BY_CODE = 'ig_shortcode({{code}}){likes{nodes{id,user{id,profile_pic_url,username,follows{count},followed_by{count},biography,full_name,media{count},is_private,external_url,is_verified}},page_info}}'
    LIKES_BY_SHORTCODE = 'https://www.instagram.com/graphql/query/?query_id=17864450716183058&variables={"shortcode":"{{shortcode}}","first":{{count}},"after":"{{likeId}}"}'
    FOLLOWING_URL = 'https://www.instagram.com/graphql/query/?query_id=17874545323001329&id={{accountId}}&first={{count}}&after={{after}}'
    FOLLOWERS_URL = 'https://www.instagram.com/graphql/query/?query_id=17851374694183129&id={{accountId}}&first={{count}}&after={{after}}'
    FOLLOW_URL = 'https://www.instagram.com/web/friendships/{{accountId}}/follow/'
    UNFOLLOW_URL = 'https://www.instagram.com/web/friendships/{{accountId}}/unfollow/'
    USER_FEED = 'https://www.instagram.com/graphql/query/?query_id=17861995474116400&fetch_media_item_count=12&fetch_media_item_cursor=&fetch_comment_count=4&fetch_like=10'
    USER_FEED2 = 'https://www.instagram.com/?__a=1'
    INSTAGRAM_QUERY_URL = 'https://www.instagram.com/query/'
    INSTAGRAM_CDN_URL = 'https://scontent.cdninstagram.com/'
    ACCOUNT_JSON_PRIVATE_INFO_BY_ID = 'https://i.instagram.com/api/v1/users/{userId}/info/'
    LIKE_URL = 'https://www.instagram.com/web/likes/{mediaId}/like/'
    UNLIKE_URL = 'https://www.instagram.com/web/likes/{mediaId}/unlike/'
    ADD_COMMENT_URL = 'https://www.instagram.com/web/comments/{mediaId}/add/'
    DELETE_COMMENT_URL = 'https://www.instagram.com/web/comments/{mediaId}/delete/{commentId}/'

    ACCOUNT_MEDIAS2 = 'https://www.instagram.com/graphql/query/?query_id=17880160963012870&id={{accountId}}&first=10&after='

    # Look alike??
    URL_SIMILAR = 'https://www.instagram.com/graphql/query/?query_id=17845312237175864&id=4663052'

    GRAPH_QL_QUERY_URL = 'https://www.instagram.com/graphql/query/?query_id={{queryId}}'

    requestMediaCount = 30

    @staticmethod
    def getAccountPageLink(username):
        return Endpoints.ACCOUNT_PAGE.replace('{username}', urllib.parse.quote_plus(username))

    @staticmethod
    def getAccountJsonLink(username):
        return Endpoints.ACCOUNT_JSON_INFO.replace('{username}', urllib.parse.quote_plus(username))

    @staticmethod
    def getAccountJsonInfoLinkByAccountId(account_id):
        return Endpoints.ACCOUNT_JSON_INFO_BY_ID.replace('{userId}', urllib.parse.quote_plus(account_id))

    @staticmethod
    def getAccountJsonPrivateInfoLinkByAccountId(account_id):
        return Endpoints.ACCOUNT_JSON_PRIVATE_INFO_BY_ID.replace('{userId}', urllib.parse.quote_plus(str(account_id)))

    @staticmethod
    def getAccountMediasJsonLink(variables):
        return Endpoints.ACCOUNT_MEDIAS.replace('{variables}', urllib.parse.quote_plus(json.dumps(variables)))

    @staticmethod
    def getMediaPageLink(code):
        return Endpoints.MEDIA_LINK.replace('{code}', urllib.parse.quote_plus(code))

    @staticmethod
    def getMediaJsonLink(code):
        return Endpoints.MEDIA_JSON_INFO.replace('{code}', urllib.parse.quote_plus(code))

    @staticmethod
    def getMediasJsonByLocationIdLink(facebookLocationId, maxId=''):
        url = Endpoints.MEDIA_JSON_BY_LOCATION_ID.replace(
            '{{facebookLocationId}}', urllib.parse.quote_plus(str(facebookLocationId)))
        return url.replace('{{maxId}}', urllib.parse.quote_plus(maxId))

    @staticmethod
    def getMediasJsonByTagLink(tag, maxId=''):
        url = Endpoints.MEDIA_JSON_BY_TAG.replace(
            '{tag}', urllib.parse.quote_plus(tag))
        return url.replace('{max_id}', urllib.parse.quote_plus(maxId))

    @staticmethod
    def getGeneralSearchJsonLink(query):
        return Endpoints.GENERAL_SEARCH.replace('{query}', urllib.parse.quote_plus(query))

    @staticmethod
    def getCommentsBeforeCommentIdByCode(variables):
        return Endpoints.COMMENTS_BEFORE_COMMENT_ID_BY_CODE.replace('{variables}', urllib.parse.quote_plus(variables))

    @staticmethod
    def getLastLikesByCodeLink(code):
        return Endpoints.LAST_LIKES_BY_CODE.replace('{{code}}', urllib.parse.quote_plus(code))

    @staticmethod
    def getLastLikesByCode(code, count, lastLikeID):
        url = Endpoints.LIKES_BY_SHORTCODE.replace(
            '{{shortcode}}', urllib.parse.quote_plus(code))
        url = url.replace('{{count}}', urllib.parse.quote_plus(str(count)))
        url = url.replace('{{likeId}}', urllib.parse.quote_plus(str(lastLikeID)))

        return url

    @staticmethod
    def getFollowUrl(accountId):
        return Endpoints.FOLLOW_URL.replace('{{accountId}}', urllib.parse.quote_plus(accountId))

    @staticmethod
    def getFollowersJsonLink(accountId, count, after=''):
        url = Endpoints.FOLLOWERS_URL.replace(
            '{{accountId}}', urllib.parse.quote_plus(accountId))
        url = url.replace('{{count}}', urllib.parse.quote_plus(str(count)))

        if (after == ''):
            url = url.replace('&after={{after}}', '')
        else:
            url = url.replace('{{after}}', urllib.parse.quote_plus(str(after)))

        return url

    @staticmethod
    def getFollowingJsonLink(accountId, count, after=''):
        url = Endpoints.FOLLOWING_URL.replace(
            '{{accountId}}', urllib.parse.quote_plus(accountId))
        url = url.replace('{{count}}', urllib.parse.quote_plus(count))

        if (after == ''):
            url = url.replace('&after={{after}}', '')
        else:
            url = url.replace('{{after}}', urllib.parse.quote_plus(after))

        return url

    @staticmethod
    def getUserStoriesLink():
        return Endpoints.getGraphQlUrl(InstagramQueryId.USER_STORIES, {'variables': JSONEncoder().encode([])})

    @staticmethod
    def getGraphQlUrl(queryId, parameters):
        url = Endpoints.GRAPH_QL_QUERY_URL.replace(
            '{{queryId}}', urllib.parse.quote_plus(queryId))
        if (len(parameters) > 0):
            query_string = urllib.parse.urlencode(parameters)
            url += '&' + query_string

        return url

    @staticmethod
    def getStoriesLink(variables):
        return Endpoints.getGraphQlUrl(InstagramQueryId.STORIES, {'variables': JSONEncoder().encode(variables)})

    @staticmethod
    def getLikeUrl(mediaId):
        return Endpoints.LIKE_URL.replace('{mediaId}', urllib.parse.quote_plus(mediaId))

    @staticmethod
    def getUnlikeUrl(mediaId):
        return Endpoints.UNLIKE_URL.replace('{mediaId}', urllib.parse.quote_plus(mediaId))

    @staticmethod
    def getAddCommentUrl(mediaId):
        return Endpoints.ADD_COMMENT_URL.replace('{mediaId}', mediaId)

    @staticmethod
    def getDeleteCommentUrl(mediaId, commentId):
        url = Endpoints.DELETE_COMMENT_URL.replace('{mediaId}', mediaId)
        url = url.replace('{commentId}', commentId)
        return url
