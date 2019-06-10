from context import Instagram # pylint: disable=no-name-in-module

# If account is public you can query Instagram without auth
instagram = Instagram()

# If account is private and you subscribed to it, first login
# instagram = Instagram.withCredentials('username', 'password', 'cachePath')
# instagram.login()

media = instagram.getMediaByUrl('https://www.instagram.com/p/BHaRdodBouH')

print(media)
print(media.owner)
