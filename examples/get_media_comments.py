#TODO does not work currently instagram changed api

from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()

# echo "Number of comments: {$medias[0]->getCommentsCount()}\n";
# echo "Fetched: " . count($comments) . "\n";
# or by id
comments = instagram.getMediaCommentsById('1130748710921700586', 10000)

# Let's take first comment in array and explore available fields

comment = comments[0]
print(vars(comment))

# You can start loading comments from specific comment by providing comment id
# comments = instagram.getMediaCommentsByCode('BG3Iz-No1IZ', 200, comment.identifier)