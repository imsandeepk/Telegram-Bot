from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()

medias = instagram.getMediasByLocationId('1', 20)
media = medias[0]
print(media)
print('Account info:')
account = media.owner
print('Id', account.identifier)
# print('Username', account.username)
# print('Full Name', account.full_name)
# print('Profile Pic Url', account.getProfilePicUrlHd())