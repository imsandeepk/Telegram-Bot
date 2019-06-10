from context import Instagram # pylint: disable=no-name-in-module

# If account is public you can query Instagram without auth
instagram = Instagram()

# If account is private and you subscribed to it, first login
# instagram = Instagram.withCredentials('username', 'password', 'cachepath')
# instagram.login()

media = instagram.getMediaById('1270593720437182847')

print(media)
print('Account info:')
account = media.owner
print('Id', account.identifier)
# print('Username', account.username)
# print('Full Name', account.full_name)
# print('Profile Pic Url', account.getProfilePicUrlHd())