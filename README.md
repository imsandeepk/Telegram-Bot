# instagram_scaper
A minimalistic instagram scraper wrote in python. 
fetch medias, accounts, videos, comments and more. Comment and Like action also supported.  
Inspired by instagram-php-scraper. 

**Any star or contribution is appreciated if you like to project ~** 🤘

## install
Download the project via git clone and run the following:
```
pip install -r require.txt
```
(PyPi coming soon)

## usages
Some methods do require authentication:
```python
from instagram_scraper.instagram import Instagram

instagram = Instagram()

# authentication supported
instagram = Instagram.withCredentials('username', 'password')
instagram.login()

account = instagram.getAccountById(3)
# Available fields
print('Account info:')
print('Id', account.identifier)
print('Username', account.username)
print('Full name', account.full_name)
print('Biography', account.biography)
print('Profile pic url', account.getProfilePicUrlHd())
print('External Url', account.external_url)
print('Number of published posts', account.mediaCount)
print('Number of followers', account.followed_by_count)
print('Number of follows', account.follows_count)
print('Is private', account.is_private)
print('Is verified', account.is_verified)
# or simply for printing use 
print(account)
```
If you use authentication the program will cache the user session by default so one doen't need to create session everytime.  
If one want to disable the user session cache, assign `True` to Instagram.login() method

Two Factor Authentification is also supported through cli interface, simply use 'True' for second argument of login() function 
  
Many of the methods do not require authentication

for more info browse through the examples folder

Using proxy for requests:
```python
from instagram_scraper.instagram import Instagram

proxies = {
    'http': 'http://123.45.67.8:1087',
    'https': 'http://123.45.67.8:1087',
}

instagram = Instagram()
instagram.set_proxies(proxies)

account = instagram.getAccount('kevin')
print(account.identifier)
```

## more usages
See examples folder 

## other
php lib:https://github.com/postaddictme/instagram-php-scraper
