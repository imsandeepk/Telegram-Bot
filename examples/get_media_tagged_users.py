from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()

media = instagram.getMediaById('1880687465858169462')

#not optimal to many calls
tagged_users = instagram.getMediaTaggedUsersByCode(media.shortCode)

print(tagged_users)
