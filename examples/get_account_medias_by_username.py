from context import Instagram # pylint: disable=no-name-in-module

# If account is public you can query Instagram without auth

instagram = Instagram()

medias = instagram.getMedias("kevin", 25)
media = medias[6]

print(media)
account = media.owner
print(account)
# print('Username', account.username)
# print('Full Name', account.full_name)
# print('Profile Pic Url', account.getProfilePicUrlHd())


# If account private you should be subscribed and after auth it will be available

# username = ''
# password = ''
# session_folder = ''
# instagram = Instagram.withCredentials(username, password, session_folder)
# instagram = Instagram()
# instagram.login()
# instagram.getMedias('private_account', 100)
