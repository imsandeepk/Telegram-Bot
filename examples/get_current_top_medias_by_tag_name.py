from igramscraper.instagram import Instagram

instagram = Instagram()
instagram.with_credentials('username', 'password', 'path/to/cache/folder')
instagram.login()

medias = instagram.get_current_top_medias_by_tag_name('youneverknow')
media = medias[0]

print(media)
print(media.owner)
