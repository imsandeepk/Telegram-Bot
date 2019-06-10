from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()

# Location id from facebook
location = instagram.getLocationById(1)
print(location)

