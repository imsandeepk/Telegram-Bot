from time import sleep
from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()

sleep(2) # Delay to mimic user

username = 'kevin'
followers = []
account = instagram.getAccount(username)
sleep(1)
followers = instagram.getFollowers(account.identifier, 1000, 100, True) # Get 1000 followers of 'kevin', 100 a time with random delay between requests
print(followers)