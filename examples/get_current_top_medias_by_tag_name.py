from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram()
instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()

medias = instagram.getCurrentTopMediasByTagName('youneverknow')
media = medias[0]

print(media)
print(media.owner)
