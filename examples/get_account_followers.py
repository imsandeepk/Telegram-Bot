from context import Instagram # pylint: disable=no-name-in-module
from time import sleep

instagram = Instagram()
instagram.with_credentials('login', 'password', 'pathtocache')
instagram.login()

sleep(2) # Delay to mimic user

username = 'kevin'
followers = []
account = instagram.get_account(username)
sleep(1)
followers = instagram.get_followers(account.identifier, 150, 100, True) # Get 150 followers of 'kevin', 100 a time with random delay between requests
print('Followers fetched')
print(followers)