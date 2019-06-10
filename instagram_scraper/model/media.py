import urllib.parse
import textwrap

from .initializer_model import InitializerModel
from ..endpoints.endpoints import Endpoints
from .comment import Comment
# there is one more import when Media.owner is set


class Media(InitializerModel):
    
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_SIDECAR = 'sidecar'
    TYPE_CAROUSEL = 'carousel'

    @staticmethod
    def getIdFromCode(code):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        id = 0
        
        for i in range(len(code)):
           c = code[i]
           id = id * 64 + alphabet.index(c) 
 
        return id


    @staticmethod
    def getLinkFromId(id):
        code = Media.getCodeFromId(id)
        return Endpoints.getMediaPageLink(code)

    @staticmethod
    def getCodeFromId(id):
        id = int(id)

        parts = str(id).partition('_')
        id = int(parts[0])
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        code = ''

        while (id > 0):
            remainder = int(id) % 64
            id = (id - remainder) // 64
            code = alphabet[remainder] + code

        return code

    def __str__(self):
        string=f'''
        Media Info:
        'Id: {self.identifier}
        Shortcode: {self.shortCode}
        Created at: {self.createdTime}
        Caption: {self.caption}
        Number of comments: {self.commentsCount if hasattr(self, 'commentsCount') else 0}
        Number of likes: {self.likesCount}
        Link: {self.link}
        Hig res image: {self.imageHighResolutionUrl}
        Media type: {self.type}
        '''
        
        return textwrap.dedent(string)

    def _initPropertiesCustom(self, value, prop, arr):

        if prop == 'id':
            self.identifier = value
        
        standart_properties = [
            'type',
            'link',
            'thumbnail_src',
            'caption',
            'video_view_count',
            'caption_is_edited',
            'is_ad'
        ]

        if prop in standart_properties:
            self.__setattr__(prop, value)

        elif prop == 'created_time' or prop == 'taken_at_timestamp' or prop == 'date':
            self.createdTime = int(value)

        elif prop == 'code':
            self.shortCode = value
            self.link = Endpoints.getMediaPageLink(self.shortCode)

        elif prop == 'comments':
            self.commentsCount = arr[prop]['count']
        elif prop == 'likes':
            self.likesCount = arr[prop]['count']

        elif prop == 'display_resources':
            mediasUrl = []
            for media in value:
                mediasUrl.append(media['src'])

                if media['config_width'] == 640:
                    self.imageThumbnailUrl = media['src']
                elif media['config_width'] == 750:
                    self.imageLowResolutionUrl = media['src']
                elif media['config_width'] == 1080:
                    self.imageStandardResolutionUrl = media['src']
        
        elif prop == 'display_src' or prop == 'display_url':
            self.imageHighResolutionUrl = value
            if self.type == None:
                self.type = Media.TYPE_IMAGE

        elif prop == 'thumbnail_resources':
            squareImagesUrl = []
            for squareImage in value:
                squareImagesUrl.append(squareImage['src'])
            self.squareImages = squareImagesUrl
        
        elif prop == 'carousel_media':
            self.type = Media.TYPE_CAROUSEL
            self.carouselMedia = []
            print(arr["carousel_media"])
            exit()
            for carouselArray in arr["carousel_media"]:
                self.setCarouselMedia(arr, carouselArray)

        elif prop == 'video_views':
            self.videoViews = value
            self.type = Media.TYPE_VIDEO

        elif prop == 'videos':
                self.videoLowResolutionUrl = arr[prop]['low_resolution']['url']
                self.videoStandardResolutionUrl = arr[prop]['standard_resolution']['url']
                self.videoLowBandwidthUrl = arr[prop]['low_bandwidth']['url']

        elif prop == 'video_resources':
            for video in value:
                if video['profile'] == 'MAIN':
                    self.videoStandardResolutionUrl = video['src']
                elif video['profile'] == 'BASELINE':
                    self.videoLowResolutionUrl = video['src']
                    self.videoLowBandwidthUrl = video['src']

        elif prop == 'location' and value != None:
            self.locationId = arr[prop]['id']
            self.locationName = arr[prop]['name']
            self.locationSlug = arr[prop]['slug']
        
        elif prop == 'user' or prop == 'owner':
            from .account import Account
            self.owner = Account(arr[prop])
        
        elif prop == 'is_video':
            if bool(value):
                self.type = Media.TYPE_VIDEO

        elif prop == 'video_url':
            self.videoStandardResolutionUrl = value

        elif prop == 'shortcode':
            self.shortCode = value
            self.link = Endpoints.getMediaPageLink(self.shortCode)

        elif prop == 'edge_media_to_comment':
            try:
                self.commentsCount = int(arr[prop]['count'])
            except KeyError:
                pass
            try:
                edges = arr[prop]['edges']

                for commentData in edges:
                    self.comments.append(Comment(commentData['node']))
            except KeyError:
                pass
            try:
                self.hasMoreComments = bool(arr[prop]['page_info']['has_next_page'])
            except KeyError:
                pass
            try:
                self.commentsNextPage = str(arr[prop]['page_info']['end_cursor'])
            except KeyError:
                pass

        elif prop == 'edge_media_preview_like':
            self.likesCount = arr[prop]['count']
        elif prop == 'edge_liked_by':
            self.likesCount = arr[prop]['count']

        elif prop == 'edge_media_to_caption':
            try:
                self.caption = arr[prop]['edges'][0]['node']['text']
            except (KeyError, IndexError):
                pass
            
        elif prop == 'edge_sidecar_to_children':
            pass
            # #TODO implement
            # if (!is_array($arr[$prop]['edges'])) {
            #     break;
            # }
            # foreach ($arr[$prop]['edges'] as $edge) {
            #     if (!isset($edge['node'])) {
            #         continue;
            #     }

            #     $this->sidecarMedias[] = static::create($edge['node']);
            # }
        elif prop == '__typename':
            if value == 'GraphImage':
                self.type = Media.TYPE_IMAGE
            elif value == 'GraphVideo':
                self.type = Media.TYPE_VIDEO
            elif value == 'GraphSidecar':
                self.type = Media.TYPE_SIDECAR

        # if self.ownerId and self.owner != None:
        #     self.ownerId = self.getOwner().getId()

     
    @staticmethod
    def setCarouselMedia(mediaArray, carouselArray):
        print(carouselArray)
        #TODO implement
        '''
        param mediaArray
        param carouselArray
        param instance
        return mixed
        '''
        carouselMedia = CarouselMedia()
        carouselMedia.type(carouselArray['type'])

        try:
            images = carouselArray['images']
        except KeyError:
            pass
        
        carouselImages = self.getImageUrls(carouselArray['images']['standard_resolution']['url'])
        carouselMedia.imageLowResolutionUrl = carouselImages['low']
        carouselMedia.imageThumbnailUrl = carouselImages['thumbnail']
        carouselMedia.imageStandardResolutionUrl = carouselImages['standard']
        carouselMedia.imageHighResolutionUrl = carouselImages['high']
            
        if carouselMedia.type == Media.TYPE_VIDEO: 
            try:
                carouselMedia.video_views = carouselArray['video_views']
            except KeyError:
                pass

            if 'videos' in carouselArray.keys():
                carouselMedia.videoLowResolutionUrl(carouselArray['videos']['low_resolution']['url'])
                carouselMedia.videoStandardResolutionUrl(carouselArray['videos']['standard_resolution']['url'])
                carouselMedia.videoLowBandwidthUrl(carouselArray['videos']['low_bandwidth']['url'])
        
        mediaArray.append(carouselMedia)
        # array_push($instance->carouselMedia, $carouselMedia);
        return mediaArray

    @staticmethod
    def __getImageUrls(imageUrl):
        parts = '/'.split(urllib.parse(imageUrl)['path'])
        imageName = parts[len(parts) - 1]
        urls = {
            'thumbnail' : Endpoints.INSTAGRAM_CDN_URL + 't/s150x150/' + imageName,
            'low' : Endpoints.INSTAGRAM_CDN_URL + 't/s320x320/' + imageName,
            'standard' : Endpoints.INSTAGRAM_CDN_URL + 't/s640x640/' + imageName,
            'high' : Endpoints.INSTAGRAM_CDN_URL + 't/' + imageName,
        }
        return urls
