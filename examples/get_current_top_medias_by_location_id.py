from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram()
instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()

medias = instagram.getCurrentTopMediasByLocationId('1')

media = medias[0]
print(media)
print(media.owner)
# print('Username', account.username)
# print('Full Name', account.full_name)
# print('Profile Pic Url', account.getProfilePicUrlHd())
