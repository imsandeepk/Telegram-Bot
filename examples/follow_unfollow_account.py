from igramscraper.instagram import Instagram

instagram = Instagram()
instagram.with_credentials('', '', 'pathtocache')
instagram.login()

instagram.follow('user_id')
instagram.unfollow('user_id')