from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()


# add comment to post
mediaId = '1874597980243548658'
comment = instagram.addComment(mediaId, 'nice!!')
# replied to comment
comment_b = instagram.addComment(mediaId, 'cool man', comment)

    
instagram.deleteComment(mediaId, comment)

