#TODO does not work currently instagram changed api
from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()

# Get media comments by shortcode
likes = instagram.getMediaLikesByCode('BG3Iz-No1IZ', 8000)

print("Result count: " + len(likes))

print(vars(likes))

# foreach ($likes as $like) {
# 	echo "username: " . $like->getUserName() . "\n";
# }

# ...



