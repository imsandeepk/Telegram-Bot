from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()

stories = instagram.getStories()
user_stories = stories[0]
print(user_stories.owner)
for story in user_stories.stories:
    print(story)