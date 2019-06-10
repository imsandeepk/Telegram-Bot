from bs4 import BeautifulSoup
import requests
import re
import json
import hashlib
import os
from slugify import slugify

from .session_manager import CookieSessionManager

from .exception.instagram_auth_exception import InstagramAuthException
from .exception.instagram_exception import InstagramException
from .exception.instagram_not_found_exception import InstagramNotFoundException

from .model.account import Account
from .model.comment import Comment
# import model.Like
from .model.location import Location
from .model.media import Media
from .model.story import Story
from .model.user_stories import UserStories
from .model.tag import Tag

from .endpoints.endpoints import Endpoints

from .two_step_verification.console_verification import ConsoleVerification

#TODO funcs for setting and disabling Proxy
class Instagram:
    HTTP_NOT_FOUND = 404
    HTTP_OK = 200
    HTTP_FORBIDDEN = 403
    HTTP_BAD_REQUEST = 400

    MAX_COMMENTS_PER_REQUEST = 300
    MAX_LIKES_PER_REQUEST = 50
    # 30 mins time limit on operations that require multiple requests
    PAGING_TIME_LIMIT_SEC = 1800
    PAGING_DELAY_MINIMUM_MICROSEC = 1000000  # 1 sec min delay to simulate browser
    PAGING_DELAY_MAXIMUM_MICROSEC = 3000000  # 3 sec max delay to simulate browser

    '''
    @var ExtendedCacheItemPoolInterface $instanceCache
    '''
    instanceCache = None

    def __init__(self):
        self.pagingTimeLimitSec = Instagram.PAGING_TIME_LIMIT_SEC
        self.pagingDelayMinimumMicrosec = Instagram.PAGING_DELAY_MINIMUM_MICROSEC
        self.pagingDelayMaximumMicrosec = Instagram.PAGING_DELAY_MAXIMUM_MICROSEC

        self.sessionUsername = None
        self.sessionPassword = None
        self.userSession = None
        self.rhxGis = None
        self.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'


    @staticmethod
    def withCredentials(username, password, sessionFolder = None):
        '''
        param string username
        param string password
        param null sessionFolder
    
        return Instagram
        '''

        Instagram.instanceCache = None
        
        if sessionFolder == None:
            cwd = os.getcwd()
            sessionFolder = cwd + os.path.sep + 'sessions' + os.path.sep
        
        if isinstance(sessionFolder, str):
            
            Instagram.instanceCache = CookieSessionManager(sessionFolder, slugify(username) + '.txt')

        else:
            Instagram.instanceCache = sessionFolder
        
        Instagram.instanceCache.empty_saved_cookies()

        instance = Instagram()
        instance.sessionUsername = username
        instance.sessionPassword = password
    
        return instance

    @staticmethod
    def setAccountMediasRequestCount(count):
        '''
        Set how many media objects should be retrieved in a single request
        param int count
        '''
        Endpoints.requestMediaCount = count

    def getAccountById(self, id):
        '''
        param string $id

        return Account
        throws InstagramException
        throws InvalidArgumentException
        throws InstagramNotFoundException
        '''
        username = self.getUsernameById(id)
        return self.getAccount(username)

    def getUsernameById(self, id):
        '''
        param string $id
        return string
        throws InstagramException
        throws InstagramNotFoundException
        '''
        response = requests.get(Endpoints.getAccountJsonPrivateInfoLinkByAccountId(
            id), headers=self.generateHeaders(self.userSession))

        if Instagram.HTTP_NOT_FOUND == response.status_code:
            raise InstagramNotFoundException(
                'Failed to fetch account with given id')

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        json_response = response.json()
        if json_response == None:
            raise InstagramException('Response does not JSON')

        if json_response['status'] != 'ok':
            message = json_response['message'] if (
                'message' in json_response.keys()) else 'Unknown Error'
            raise InstagramException(message)

        return json_response['user']['username']

    def generateHeaders(self, session, gisToken=None):
        '''
        @param $session
        @param $gisToken
        @return array
        '''
        headers = {}
        if (session != None):
            cookies = ''

            for key in session.keys():
                cookies += f"{key}={session[key]}; "

            csrf = session['x-csrftoken'] if session['csrftoken'] == None else session['csrftoken']

            headers = {
                'cookie': cookies,
                'referer': Endpoints.BASE_URL + '/',
                'x-csrftoken': csrf
            }

        if self.userAgent != None:
            headers['user-agent'] = self.userAgent

            if (gisToken != None):
                headers['x-instagram-gis'] = gisToken

        return headers
    

    def __generateGisToken(self, variables):
        '''
        param $variables
        return string
        throws InstagramException
        '''
        rhxGis = self.__getRhxGis() if self.__getRhxGis() != None else 'NULL'
        string_to_hash = ':'.join([rhxGis, json.dumps(variables)])
        return hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()

    def __getRhxGis(self):
        if self.rhxGis == None:
            try:
                sharedData = self.__getSharedDataFromPage()
            except:
                raise InstagramException('Could not extract gis from page')

            if 'rhx_gis' in sharedData.keys():
                self.rhxGis = sharedData['rhx_gis']
            else:
                self.rhxGis = None
                

        return self.rhxGis
        
    def __get_mid(self):
        'manually fetches the machine id from graphQL'
        response =requests.get('https://www.instagram.com/web/__mid/')

        if response.status_code != Instagram.HTTP_OK:
            raise InstagramException.default(response.text, response.status_code)

        return response.text
        
    def __getSharedDataFromPage(self, url = Endpoints.BASE_URL):
        '''
        param string $url
        return mixed|null
        throws InstagramException
        throws InstagramNotFoundException
         '''
        url.strip
        url = url.rstrip('/') + '/'
        response = requests.get(url, headers=self.generateHeaders(self.userSession))

        if (Instagram.HTTP_NOT_FOUND == response.status_code):
            raise InstagramNotFoundException(f"Page {url} not found")

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        return Instagram.extractSharedDataFromBody(response.text)


    @staticmethod
    def extractSharedDataFromBody(body):
        array = re.findall(r'_sharedData = .*?;</script>', body)
        if len(array) > 0:
            raw_json = array[0][len("_sharedData ="):-len(";</script>")]

            return json.loads(raw_json)

        return None


    @staticmethod
    def searchTagsByTagName(tag):
        '''
        param string tag
     
        return array
        throws InstagramException
        throws InstagramNotFoundException
        '''
        # TODO: Add tests and auth
        response = requests.get(Endpoints.getGeneralSearchJsonLink(tag))

        if Instagram.HTTP_NOT_FOUND == response.status_code:
            raise InstagramNotFoundException('Account with given username does not exist.')

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        jsonResponse = response.json()

        try:
            status = jsonResponse['status']
            if status != 'ok':
                raise InstagramException('Response code is not equal 200. Something went wrong. Please report issue.')
        except KeyError:
            raise InstagramException('Response code is not equal 200. Something went wrong. Please report issue.')

        try:
            hashtags_raw = jsonResponse['hashtags']
            if len(hashtags_raw) == 0:
                return []
        except KeyError:
            return []

        hashtags = []
        for jsonHashtag in hashtags_raw:
            hashtags.append(Tag(jsonHashtag['hashtag']))

        return hashtags

    def getMedias(self, username, count=20, maxId=''):
        '''
        param string username
        param int count
        param string maxId

        return Media[]
        throws InstagramException
        throws InstagramNotFoundException
        '''

        account = self.getAccount(username)
        return self.getMediasByUserId(account.identifier, count, maxId)

        
    def getMediaByCode(self, mediaCode):
        '''
        param string mediaCode (for example BHaRdodBouH)
   
        return Media
        throws InstagramException
        throws InstagramNotFoundException
        '''
        url = Endpoints.getMediaPageLink(mediaCode)
        return self.getMediaByUrl(url)

    def getMediasByUserId(self, id, count = 12, maxId = ''):
        '''
        param int id
        param int count
        param string maxId
     
        return Media[]
        throws InstagramException
        '''
        
        index = 0
        medias = []
        isMoreAvailable = True

        while index < count and isMoreAvailable:

            variables = {
                'id': str(id),
                'first': str(count),
                'after': str(maxId)
            }

            headers = self.generateHeaders(self.userSession, self.__generateGisToken(variables))

            response = requests.get(Endpoints.getAccountMediasJsonLink(variables), headers=headers)

            if (Instagram.HTTP_OK != response.status_code):
                raise InstagramException.default(response.text, response.status_code)

            arr = json.loads(response.text)

            try:
                nodes = arr['data']['user']['edge_owner_to_timeline_media']['edges']
            except KeyError:
                return {}

            for mediaArray in nodes:
                if index == count:
                    return medias
                    
                media = Media(mediaArray['node'])
                medias.append(media)
                index += 1

            if nodes == None or nodes == '':
                return medias
            
            maxId = arr['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            isMoreAvailable = arr['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']

        return medias


    def getMediaById(self, mediaId):
        '''
        param mediaId
     
        return Media
        throws InstagramException
        throws InstagramNotFoundException
        '''
        mediaLink = Media.getLinkFromId(mediaId)
        return self.getMediaByUrl(mediaLink)

        
    def getMediaByUrl(self, mediaUrl):
        '''
        param string $mediaUrl
    
        return Media
        throws InstagramException
        throws InstagramNotFoundException
        '''
        url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

        if len(re.findall(url_regex, mediaUrl)) <= 0:
            raise ValueError('Malformed media url')

        url = mediaUrl.rstrip('/') + '/?__a=1'
        response = requests.get(url, headers=self.generateHeaders(self.userSession))
        
        if Instagram.HTTP_NOT_FOUND == response.status_code:
            raise InstagramNotFoundException('Media with given code does not exist or account is private.')

        if Instagram.HTTP_OK != response.status_code:
            raise InstagramException.default(response.text, response.status_code)

        mediaArray = response.json()
        try:
            mediaInJson = mediaArray['graphql']['shortcode_media']
        except KeyError:
            raise InstagramException('Media with this code does not exist')

        return Media(mediaInJson)


    def getMediasFromFeed(self, username, count = 20):
        '''
        param string username
        param int count
        return Media[]
        throws InstagramException
        throws InstagramNotFoundException
        '''
        medias = []
        index = 0
        response = requests.get(Endpoints.getAccountJsonLink(username), headers=self.generateHeaders(self.userSession))

        if (Instagram.HTTP_NOT_FOUND == response.status_code):
            raise InstagramNotFoundException('Account with given username does not exist.')

        if Instagram.HTTP_OK != response.status_code:
            raise InstagramException.default(response.text, response.status_code)

        userArray = response.json()

        try:
            user = userArray['graphql']['user']
        except KeyError:
            raise InstagramNotFoundException('Account with this username does not exist')
            
        try:
            nodes = user['edge_owner_to_timeline_media']['edges']
            if len(nodes) == 0:
                return []
        except:
            return []

        for mediaArray in nodes:
            if index == count:
                return medias
            medias.append(Media(mediaArray['node']))
            index += 1

        return medias
    

    def getMediasByTag(self, tag, count = 12, maxId = '', minTimestamp = None):
        '''
        param string $tag
        param int $count
        param string $maxId
        param string $minTimestamp
    
        return Media[]
        throws InstagramException
        '''
        index = 0
        medias = []
        mediaIds = []
        hasNextPage = True
        while index < count and hasNextPage:

            response = requests.get(Endpoints.getMediasJsonByTagLink(tag, maxId),
                headers=self.generateHeaders(self.userSession))

            if response.status_code != Instagram.HTTP_OK:
                raise InstagramException.default(response.text, response.status_code)

            arr = response.json()
           
            try:
                arr['graphql']['hashtag']['edge_hashtag_to_media']['count']
            except KeyError:
                return []
           
            nodes = arr['graphql']['hashtag']['edge_hashtag_to_media']['edges']
            for mediaArray in nodes:
                if index == count:
                    return medias
                media = Media(mediaArray['node'])
                if media.identifier in mediaIds:
                    return medias
                
                if minTimestamp != None and media.createdTime < minTimestamp:
                    return medias

                mediaIds.append(media.identifier)
                medias.append(media)
                index+=1

            if len(nodes) == 0:
                return medias
            
            maxId = arr['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            hasNextPage = arr['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
            print('maxId:', maxId)
            print('hasNextPage:', hasNextPage)

        return medias

        
    def getMediasByLocationId(self, facebookLocationId, quantity = 24, offset = ''):
        '''
        param string facebookLocationId
        param int quantity
        param string offset
     
        return Media[]
        throws InstagramException
        '''

        index = 0
        medias = []
        hasNext = True

        while index < quantity and hasNext:

            response = requests.get(Endpoints.getMediasJsonByLocationIdLink(facebookLocationId, offset),
                headers=self.generateHeaders(self.userSession))

            if response.status_code != Instagram.HTTP_OK:
                raise InstagramException.default(response.text,response.status_code)

            arr = response.json()

            nodes = arr['graphql']['location']['edge_location_to_media']['edges']
            for mediaArray in nodes:
                if index == quantity:
                    return medias

                medias.append(Media(mediaArray['node']))
                index += 1

            if len(nodes) == 0:
                return medias

            hasNextPage = arr['graphql']['location']['edge_location_to_media']['page_info']['has_next_page']
            endCursor = arr['graphql']['location']['edge_location_to_media']['page_info']['end_cursor']
            print(hasNextPage, endCursor)

        return medias

    def getCurrentTopMediasByTagName(self, tagName):
        '''
        param $tagName
     
        return Media[]
        throws InstagramException
        throws InstagramNotFoundException
        '''

        response = requests.get(Endpoints.getMediasJsonByTagLink(tagName, ''),
            headers=self.generateHeaders(self.userSession))

        if response.status_code == Instagram.HTTP_NOT_FOUND:
            raise InstagramNotFoundException('Account with given username does not exist.')

        if (response.status_code != Instagram.HTTP_OK):
            raise InstagramException.default(response.text, response.status_code)


        jsonResponse = response.json()
        medias = []

        nodes = jsonResponse['graphql']['hashtag']['edge_hashtag_to_top_posts']['edges']
        
        for mediaArray in nodes:
            medias.append(Media(mediaArray['node']))

        return medias

    def getCurrentTopMediasByLocationId(self, facebookLocationId):
        '''
        param facebookLocationId
     
        return Media[]
        throws InstagramException
        throws InstagramNotFoundException
        '''
        response = requests.get(Endpoints.getMediasJsonByLocationIdLink(facebookLocationId),
            headers=self.generateHeaders(self.userSession))
        if response.status_code == Instagram.HTTP_NOT_FOUND:
            raise InstagramNotFoundException("Location with this id doesn't exist")

        if response.status_code != Instagram.HTTP_OK:
            raise InstagramException.default(response.text, response.status_code)

        jsonResponse = response.json()
        #print(response.json())
        nodes = jsonResponse['graphql']['location']['edge_location_to_top_posts']['edges']
        medias = []

        for mediaArray in nodes:
            medias.append(Media(mediaArray['node']))

        return medias

    def getPaginateMedias(self, username, maxId = ''):
        '''
        param string username
        param string maxId
    
        return array
        throws InstagramException
        throws InstagramNotFoundException
        '''

        account = self.getAccount(username)
        hasNextPage = True
        medias = []

        toReturn = {
            'medias' : medias,
            'maxId' : maxId,
            'hasNextPage' : hasNextPage,
        }

        variables = json.dumps({
            'id' : str(account.identifier),
            'first' : str(Endpoints.requestMediaCount),
            'after' : str(maxId)
        })

        response = requests.get(
            Endpoints.getAccountMediasJsonLink(variables),
            headers=self.generateHeaders(self.userSession, self.__generateGisToken(variables))
        )

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        arr = response.json()

        try: 
            nodes = arr['data']['user']['edge_owner_to_timeline_media']['edges']
        except KeyError:
            return toReturn

        #if (count($arr['items']) === 0) {
        # I generally use empty. Im not sure why people would use count really - If the array is large then count takes longer/has more overhead.
        # If you simply need to know whether or not the array is empty then use empty.
        for mediaArray in nodes:
            medias.append(Media(mediaArray['node']))


        end_cursor = arr['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        hasNextPage = arr['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']

        toReturn = {
            'medias' : medias,
            'maxId' : maxId,
            'hasNextPage' : hasNextPage,
        }

        return toReturn

    def getPaginateMediasByTag(self, tag, maxId = ''):
        '''
        param string tag
        param string maxId
     
        return array
        throws InstagramException
        '''
        hasNextPage = True
        medias = []

        toReturn = {
            'medias' : medias,
            'maxId' : maxId,
            'hasNextPage' : hasNextPage,
        }

        response = requests.get(Endpoints.getMediasJsonByTagLink(tag, maxId),
            headers=self.generateHeaders(self.userSession))

        if response.status_code != Instagram.HTTP_OK :
            raise InstagramException.default(response.text, response.code)

        arr = response.json

        try:
            mediaCount = arr['graphql']['hashtag']['edge_hashtag_to_media']['count']
        except KeyError:
            return toReturn

        try:
            nodes = arr['graphql']['hashtag']['edge_hashtag_to_media']['edges']
        except KeyError:
            return toReturn
        
        for mediaArray in nodes:
            medias.append(Media(mediaArray['node']))


        maxId = arr['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        hasNextPage = arr['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
        count = arr['graphql']['hashtag']['edge_hashtag_to_media']['count']

        toReturn = {
            'medias' : medias,
            'count' : count,
            'maxId' : maxId,
            'hasNextPage' : hasNextPage,
        }

        return toReturn


    def getLocationById(self, facebookLocationId):
        '''
        param string $facebookLocationId
     
        return Location
        throws InstagramException
        throws InstagramNotFoundException
        '''
        response = requests.get(Endpoints.getMediasJsonByLocationIdLink(facebookLocationId),
            headers=self.generateHeaders(self.userSession))

        if response.status_code == Instagram.HTTP_NOT_FOUND:
            raise InstagramNotFoundException('Location with this id doesn\'t exist')

        if response.status_code != Instagram.HTTP_OK:
            raise InstagramException.default(response.text, response.status_code)
            
        jsonResponse = response.json()

        return Location(jsonResponse['graphql']['location'])

    def getMediaLikesByCode(self, code, count = 10, maxId = None):
        '''
        param      code
        param int count
        param null maxId
     
        return array
        throws InstagramException
        '''
        pass
        #TODO implement
        # remain = count
        # likes = []
        # index = 0
        # hasPrevious = True
        # #TODO: $index < $count (bug index getting to high since max_likes_per_request gets sometimes changed by instagram)
        # while (hasPrevious and index < count):
        #     if (remain > self.MAX_LIKES_PER_REQUEST):
        #         numberOfLikesToRetreive = self.MAX_LIKES_PER_REQUEST
        #         remain -= self.MAX_LIKES_PER_REQUEST
        #         index += self.MAX_LIKES_PER_REQUEST
        #     else:
        #         numberOfLikesToRetreive = remain
        #         index += remain
        #         remain = 0
            
        #     if (maxId != None):
        #         maxId = ''

        #     commentsUrl = Endpoints.getLastLikesByCode(code, numberOfLikesToRetreive, maxId)
        #     response = requests.get(commentsUrl, headers=self.generateHeaders(self.userSession))

        #     if (response.status_code != Instagram.HTTP_OK):
        #         raise InstagramException(f'Response code is {response.status_code}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)

        #     jsonResponse = response.json()
        #     print(jsonResponse)
        #     exit()

        #     $nodes = $jsonResponse['data']['shortcode_media']['edge_liked_by']['edges'];

        #     foreach ($nodes as $likesArray) {
        #         $likes[] = Like::create($likesArray['node']);
        #     }

        #     $hasPrevious = $jsonResponse['data']['shortcode_media']['edge_liked_by']['page_info']['has_next_page'];
        #     $numberOfLikes = $jsonResponse['data']['shortcode_media']['edge_liked_by']['count'];
        #     if ($count > $numberOfLikes) {
        #         $count = $numberOfLikes;
        #     }
        #     if (sizeof($nodes) == 0) {
        #         return $likes;
        #     }
        #     $maxId = $jsonResponse['data']['shortcode_media']['edge_liked_by']['page_info']['end_cursor'];

        # data['next_page'] = maxId
        # data['likes'] = likes

        # return data

    def getFollowers(self, accountId, count = 20, pageSize = 20, endCursor = '', delayed = True):
        #TODO implement
        #previous method of extracting this data not working any longer
        '''
        param string accountId Account id of the profile to query
        param int count Total followers to retrieve
        param int pageSize Internal page size for pagination
        param bool delayed Use random delay between requests to mimic browser behaviour
     
        return array
        throws InstagramException
        '''
        #TODO set time limit
        # if ($delayed) {
        #     set_time_limit($this->pagingTimeLimitSec);
        # }

        index = 0
        accounts = []

        next_page = None

        if count < pageSize:
            raise InstagramException('Count must be greater than or equal to page size.')

        while (True):
            next_page = None
            print(self.isLoggedIn(self.userSession))
            response = requests.get(Endpoints.getFollowersJsonLink(accountId, pageSize, endCursor),
                headers=self.generateHeaders(self.userSession))

            if (response.status_code != Instagram.HTTP_OK):
                raise InstagramException.default(response.text, response.status_code)

            
            jsonResponse = response.json()
            #TODO request gives empty response, fix
            print(jsonResponse)

            if (jsonResponse['data']['user']['edge_followed_by']['count'] == 0):
                return accounts

            edgesArray = jsonResponse['data']['user']['edge_followed_by']['edges']
            if len(edgesArray) == 0:
                InstagramException(f'Failed to get followers of account id {accountId}. The account is private.', Instagram.HTTP_FORBIDDEN)

            exit()
            pageInfo = jsonResponse['data']['user']['edge_followed_by']['page_info']
            if pageInfo['has_next_page']:
                next_page = pageInfo['end_cursor']
            for edge in edgesArray:
                accounts.append(edge['node'])
                index += 1
                if index >= count:
                    pass
                    #TODO does not work in python
                    #break 2

            # $pageInfo = $jsonResponse['data']['user']['edge_followed_by']['page_info'];
            # if ($pageInfo['has_next_page']) {
            #     $endCursor = $pageInfo['end_cursor'];
            # } else {
            #     break;
            # }

            # if ($delayed) {
            #     # Random wait between 1 and 3 sec to mimic browser
            #     $microsec = rand($this-> Microsec, $this->pagingDelayMaximumMicrosec);
            #     usleep($microsec);
            # }

        # $data['next_page'] = $next_page;
        # $data['accounts'] = $accounts;

        # return $data;


    def getFollowing(self, accountId, count = 20, pageSize = 20, endCursor = '', delayed = True):
        '''
        param string $accountId Account id of the profile to query
        param int $count Total followed accounts to retrieve
        param int $pageSize Internal page size for pagination
        param bool $delayed Use random delay between requests to mimic browser behaviour
     
        return array
        throws InstagramException
        '''
        pass
        #TODO implement
        #previous method of extracting this data not working any longer

    # {
    #     if ($delayed) {
    #         set_time_limit($this->pagingTimeLimitSec);
    #     }

    #     $index = 0;
    #     $accounts = [];

    #     $next_page = null;

    #     if ($count < $pageSize) {
    #         throw new InstagramException('Count must be greater than or equal to page size.');
    #     }

    #     while (true) {
    #         $next_page = null;

    #         $response = Request::get(Endpoints::getFollowingJsonLink($accountId, $pageSize, $endCursor),
    #             $this->generateHeaders($this->userSession));

    #         if ($response->code !== static::HTTP_OK) {
    #             throw new InstagramException('Response code is ' . $response->code . '. Body: ' . static::getErrorBody($response->body) . ' Something went wrong. Please report issue.', $response->code);
    #         }

    #         $jsonResponse = $this->decodeRawBodyToJson($response->raw_body);

    #         if ($jsonResponse['data']['user']['edge_follow']['count'] === 0) {
    #             return $accounts;
    #         }

    #         $edgesArray = $jsonResponse['data']['user']['edge_follow']['edges'];
    #         if (count($edgesArray) === 0) {
    #             throw new InstagramException('Failed to get followers of account id ' . $accountId . '. The account is private.', static::HTTP_FORBIDDEN);
    #         }

    #         $pageInfo = $jsonResponse['data']['user']['edge_follow']['page_info'];
    #         if ($pageInfo['has_next_page']) {
    #             $next_page = $pageInfo['end_cursor'];
    #         }

    #         foreach ($edgesArray as $edge) {
    #             $accounts[] = $edge['node'];
    #             $index++;
    #             if ($index >= $count) {
    #                 break 2;
    #             }
    #         }

    #         $pageInfo = $jsonResponse['data']['user']['edge_follow']['page_info'];
    #         if ($pageInfo['has_next_page']) {
    #             $endCursor = $pageInfo['end_cursor'];
    #         } else {
    #             break;
    #         }

    #         if ($delayed) {
    #             # Random wait between 1 and 3 sec to mimic browser
    #             $microsec = rand($this->pagingDelayMinimumMicrosec, $this->pagingDelayMaximumMicrosec);
    #             usleep($microsec);
    #         }
    #     }

    #     $data['next_page'] = $next_page;
    #     $data['accounts'] = $accounts;

    #     return $data;
    # }

    def getMediaCommentsById(self, mediaId, count = 10, maxId = None):
        '''
        param mediaId
        param int count
        param null maxId
     
        return Comment[]
        throws InstagramException
        '''
        code = Media.getCodeFromId(mediaId)
        return self.getMediaCommentsByCode(code, count, maxId)


    def getMediaCommentsByCode(self, code, count = 10, maxId = ''):
        #TODO implement not working!
        '''
        param      $code
        param int $count
        param null $maxId
     
        return Comment[]
        throws InstagramException
        '''
        comments = []
        index = 0
        hasPrevious = True

        while hasPrevious and index < count:

            if count - index > Instagram.MAX_COMMENTS_PER_REQUEST:
                numberOfCommentsToRetreive = Instagram.MAX_COMMENTS_PER_REQUEST
            else:
                numberOfCommentsToRetreive = count - index


            variables = json.dumps({
                'shortcode' : str(code),
                'first' : str(numberOfCommentsToRetreive),
                'after' : str(maxId)
            })

            commentsUrl = Endpoints.getCommentsBeforeCommentIdByCode(variables)
            print(commentsUrl)
            response = requests.get(commentsUrl, headers=self.generateHeaders(self.userSession, self.__generateGisToken(variables)))
            # use a raw constant in the code is not a good idea!!
            #if ($response->code !== 200) {
            if (response.status_code != Instagram.HTTP_OK):
                raise InstagramException.default(response.text, response.status_code)

            jsonResponse = response.json()
            print(jsonResponse)
            exit()
            # nodes = $jsonResponse['data']['shortcode_media']['edge_media_to_comment']['edges'];
 
            # foreach ($nodes as $commentArray) {
            #     $comments[] = Comment::create($commentArray['node']);
            #     $index++;
            # }
            # $hasPrevious = $jsonResponse['data']['shortcode_media']['edge_media_to_comment']['page_info']['has_next_page'];

            # $numberOfComments = $jsonResponse['data']['shortcode_media']['edge_media_to_comment']['count'];
            # if ($count > $numberOfComments) {
            #     $count = $numberOfComments;
            # }
            # if (sizeof($nodes) == 0) {
            #     return $comments;
            # }
            # $maxId = $jsonResponse['data']['shortcode_media']['edge_media_to_comment']['page_info']['end_cursor'];

        # $data['next_page'] = $maxId;
        # $data['comments'] = $comments;
        # return $data;

    def getAccount(self, username):
        '''
        param string $username

        return Account
        throws InstagramException
        throws InstagramNotFoundException
        '''
        response = requests.get(Endpoints.getAccountPageLink(
            username), headers=self.generateHeaders(self.userSession))

        if (Instagram.HTTP_NOT_FOUND == response.status_code):
            raise InstagramNotFoundException(
                'Account with given username does not exist.')

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        userArray = Instagram.extractSharedDataFromBody(response.text)

        if userArray['entry_data']['ProfilePage'][0]['graphql']['user'] == None:
            raise InstagramNotFoundException('Account with this username does not exist')

        return Account(userArray['entry_data']['ProfilePage'][0]['graphql']['user'])


    def getStories(self, reel_ids = None):
        '''
        param array reel_ids - array of instagram user ids
        return array
        throws InstagramException
        '''

        variables = {'precomposed_overlay' : False, 'reel_ids' : []}

        if reel_ids == None or len(reel_ids) == 0:
            response = requests.get(Endpoints.getUserStoriesLink(),
                headers=self.generateHeaders(self.userSession))

            if (Instagram.HTTP_OK != response.status_code):
                raise InstagramException.default(response.text, response.status_code)

            jsonResponse = response.json()

            try:
                edges = jsonResponse['data']['user']['feed_reels_tray']['edge_reels_tray_to_reel']['edges']
            except KeyError:
                return []

            for edge in edges:
                variables['reel_ids'].append(edge['node']['id'])
        
        else:
            variables['reel_ids'] = reel_ids

        response = requests.get(Endpoints.getStoriesLink(variables),
            headers=self.generateHeaders(self.userSession))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        jsonResponse = response.json()

        try: 
            reels_media = jsonResponse['data']['reels_media']
            if len(reels_media) == 0:
                return []
        except KeyError:
            return []

        stories = []
        for user in reels_media:
            userStories = UserStories()

            userStories.owner = Account(user['user'])
            for item in user['items']:
                story = Story(item)
                userStories.stories.append(story)

            stories.append(userStories)
        return stories

    def searchAccountsByUsername(self, username):
        '''
        param string username
     
        return Account[]
        throws InstagramException
        throws InstagramNotFoundException
        '''
    
        response = requests.get(Endpoints.getGeneralSearchJsonLink(username), headers=self.generateHeaders(self.userSession))

        if (Instagram.HTTP_NOT_FOUND == response.status_code):
            raise InstagramNotFoundException('Account with given username does not exist.')

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        jsonResponse = response.json()

        try:
            status = jsonResponse['status']
            if status != 'ok':
                raise InstagramException('Response code is not equal 200. Something went wrong. Please report issue.')
        except KeyError:
            raise InstagramException('Response code is not equal 200. Something went wrong. Please report issue.')

        try: 
            users = jsonResponse['users']
            if len(users)==0:
                return []
        except KeyError:
            return []

        accounts = []
        for jsonAccount in jsonResponse['users']:
            accounts.append(Account(jsonAccount['user']))

        return accounts


     #TODO not optimal seperate http call after getMedia
    def getMediaTaggedUsersByCode(self, code):
        '''
        param $code
     
        return array
        throws InstagramException
        '''
        url = Endpoints.getMediaJsonLink(code)

        response = requests.get(url, headers=self.generateHeaders(self.userSession))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        jsonResponse = response.json()

        try: 
            tag_data = jsonResponse['graphql']['shortcode_media']['edge_media_to_tagged_user']['edges']
        except KeyError:
            return []
        
        tagged_users = []

        for tag in tag_data:
            xPos = tag['node']['x']
            yPos = tag['node']['y']
            user = tag['node']['user']
            #TODO: add Model and add Data to it instead of Dict
            tagged_user = {}
            tagged_user['xPos'] = xPos
            tagged_user['yPos'] = yPos
            tagged_user['user'] = user

            tagged_users.append(tagged_user)
            
        
        return tagged_users

    def isLoggedIn(self, session):
        '''
        param $session
   
        return bool
        '''
        if session == None or not 'sessionid' in session.keys():
            return False

        sessionId = session['sessionid']
        csrfToken = session['csrftoken']

        headers = {
            'cookie' : f"ig_cb=1; csrftoken={csrfToken}; sessionid={sessionId};",
            'referer' : Endpoints.BASE_URL + '/',
            'x-csrftoken' : csrfToken,
            'X-CSRFToken' : csrfToken,
            'user-agent' : self.userAgent,
        }

        response = requests.get(Endpoints.BASE_URL, headers=headers)

        if (response.status_code != Instagram.HTTP_OK):
            return False
    
        cookies = response.cookies.get_dict()

        if cookies == None or not 'ds_user_id' in cookies.keys():
            return False

        return True


    def login(self, force = False, twoStepVerificator = None):
        '''
        param bool $force
        param bool|TwoStepVerificationInterface $twoStepVerificator

        support_two_step_verification true works only in cli mode - just run login in cli mode - save cookie to file and use in any mode
    
        throws InstagramAuthException
        throws InstagramException
    
        return array
        '''
        
        if self.sessionUsername == None or self.sessionPassword == None:
            raise InstagramAuthException("User credentials not provided")

        if twoStepVerificator == True:
            twoStepVerificator = ConsoleVerification()

        session = json.loads(Instagram.instanceCache.get_saved_cookies()) if Instagram.instanceCache.get_saved_cookies() != None else None

        if force or not self.isLoggedIn(session):
            response = requests.get(Endpoints.BASE_URL)
            if (response.status_code != Instagram.HTTP_OK):
                raise InstagramException.default(response.text, response.status_code)
            
            match = re.findall(r'"csrf_token":"(.*?)"', response.text)
            
            if len(match) > 0:
                csrfToken = match[0]

            cookies = response.cookies.get_dict()

            # cookies['mid'] doesnt work at the moment so fetch it with function
            mid = self.__get_mid()

            headers = {
                'cookie' : f"ig_cb=1; csrftoken={csrfToken}; mid={mid};",
                'referer' : Endpoints.BASE_URL + '/',
                'x-csrftoken' : csrfToken,
                'X-CSRFToken' : csrfToken,
                'user-agent' : self.userAgent,
            }
            payload = {'username' : self.sessionUsername, 'password': self.sessionPassword}
            response = requests.post(Endpoints.LOGIN_URL, data=payload,headers=headers)
            
            if (response.status_code != Instagram.HTTP_OK):
                if (
                    response.status_code == Instagram.HTTP_BAD_REQUEST
                    and response.text != None
                    and response.json()['message'] == 'checkpoint_required'
                    and twoStepVerificator != None):
                    response = self.__verifyTwoStep(response, cookies, twoStepVerificator)
                    print('checkpoint required')
                
                elif response.status_code != None and response.text != None:
                    raise InstagramAuthException(f'Response code is {response.status_code}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)
                else:
                    raise InstagramAuthException('Something went wrong. Please report issue.', response.status_code)

            if not response.json()['authenticated']:
                raise InstagramAuthException('User credentials are wrong.')


            cookies = response.cookies.get_dict()

            cookies['mid'] = mid
            Instagram.instanceCache.set_saved_cookies(json.dumps(cookies))

            self.userSession = cookies

        else:
            self.userSession = session

        return self.generateHeaders(self.userSession)


    def __verifyTwoStep(self, response, cookies, twoStepVerificator):
        '''
        param response
        param cookies
        param TwoStepVerificationInterface $twoStepVerificator
        return Unirest\Response
        throws InstagramAuthException
        '''

        new_cookies =  response.cookies.get_dict()
        cookies = {**cookies, **new_cookies}
        
        cookie_string = ''
        for key in cookies.keys():
            cookie_string += f'{key}={cookies[key]};'

        headers = {
            'cookie' : cookie_string,
            'referer' : Endpoints.LOGIN_URL,
            'x-csrftoken' : cookies['csrftoken'],
            'user-agent' : self.userAgent,
        }

        url = Endpoints.BASE_URL + response.json()['checkpoint_url']

        response = requests.get(url, headers=headers)
        data = Instagram.extractSharedDataFromBody(response.text)

        if data != None:
            try:
                choices = data['entry_data']['Challenge'][0]['extraData']['content'][3]['fields'][0]['values']
            except KeyError:
                try:
                    fields = data['entry_data']['Challenge'][0]['fields']
                    try:
                        choice = {'label' : f"Email: {fields['email']}", 'value': 1}
                        choices = {**choices, **choice}
                    except KeyError:
                        pass
                    try:
                        choice = {'label' : f"Phone: {fields['phone_number']}", 'value' : 0}
                        choices = {**choices, **choice}
                    except KeyError:
                        pass

                except KeyError:
                    pass

            if len(choices) > 0:
                selected_choice = twoStepVerificator.getVerificationType(choices)
                response = requests.post(url, data={'choice' : selected_choice}, headers=headers)
            
        
        if len(re.findall('name="security_code"',response.text)) <= 0:
            raise InstagramAuthException('Something went wrong when try two step verification. Please report issue.', response.status_code)

        security_code = twoStepVerificator.getSecurityCode()

        post_data = {
            'csrfmiddlewaretoken' : cookies['csrftoken'],
            'verify' : 'Verify Account',
            'security_code' : security_code,
        }
        response = requests.post(url, data=post_data, headers=headers)
        if response.status_code != Instagram.HTTP_OK or 'Please check the code we sent you and try again' in response.text:
            raise InstagramAuthException('Something went wrong when try two step verification and enter security code. Please report issue.', response.status_code)

        return response
    

    def addComment(self, mediaId, text, repliedToCommentId = None):
        '''
        param int|string|Media $mediaId
        param int|string $text
        param int|string|Comment|null $repliedToCommentId
     
        return Comment
        throws InstagramException
        '''
        mediaId = mediaId.identifier if isinstance(mediaId, Media) else mediaId
        
        repliedToCommentId = repliedToCommentId._data['id'] if isinstance(repliedToCommentId, Comment) else repliedToCommentId

        body = {'comment_text' : text, 'replied_to_comment_id' : repliedToCommentId if repliedToCommentId != None else ''}

        response = requests.post(Endpoints.getAddCommentUrl(mediaId), data=body, headers=self.generateHeaders(self.userSession))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        jsonResponse = response.json()

        if jsonResponse['status'] != 'ok':
            status = jsonResponse['status']
            raise InstagramException(f'Response status is {status}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)

        return Comment(jsonResponse)


    def deleteComment(self, mediaId, commentId):
        '''
        param string|Media $mediaId
        param int|string|Comment $commentId
        return void
        throws InstagramException
        '''
        mediaId = mediaId.identifier if isinstance(mediaId, Media) else mediaId
        commentId = commentId._data['id'] if isinstance(commentId, Comment) else commentId

        response = requests.post(Endpoints.getDeleteCommentUrl(mediaId, commentId), headers=self.generateHeaders(self.userSession))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        jsonResponse = response.json()

        if jsonResponse['status'] != 'ok':
            status = jsonResponse['status']
            raise InstagramException(f'Response status is {status}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)

    def like(self, mediaId):
        '''
        param int|string|Media $mediaId
     
        return void
        throws InstagramException
        '''
        mediaId = mediaId.identifier if isinstance(mediaId, Media) else mediaId
        response = requests.post(Endpoints.getLikeUrl(mediaId), headers=self.generateHeaders(self.userSession))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        jsonResponse = response.json()

        if jsonResponse['status'] != 'ok':
            status = jsonResponse['status']
            raise InstagramException(f'Response status is {status}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)

    def unlike(self, mediaId):
        '''
        param int|string|Media $mediaId
        return void
        throws InstagramException
        '''
        mediaId = mediaId.identifier if isinstance(mediaId, Media) else mediaId
        response = requests.post(Endpoints.getUnlikeUrl(mediaId), headers=self.generateHeaders(self.userSession))

        if (Instagram.HTTP_OK != response.status_code):
            raise InstagramException.default(response.text, response.status_code)

        jsonResponse = response.json()

        if jsonResponse['status'] != 'ok':
            status = jsonResponse['status']
            raise InstagramException(f'Response status is {status}. Body: {response.text} Something went wrong. Please report issue.', response.status_code)
