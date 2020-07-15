from igramscraper.instagram import Instagram
import time
from telethon import TelegramClient,events,sync,Button

instagram= Instagram()
username= '_photo__paradise_'
password= 'insta@photoparadise'

instagram.with_credentials(username,password)

instagram.login()

account= instagram.get_account("iam_sandeepk10")


followers = account.followed_by_count
following = account.follows_count


folowers=[]
folowers = instagram.get_followers(account.identifier, 150, 100, delayed=True)




    


api_id="1012749"
api_hash="d8e99e31ce89bd37fe565a15c56477d0"
bot_token="1312048087:AAG01Rm_RbbUy3S_r1BrQCaLF16FhguEf7M"

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage)
async def my_event_handler(event):
    if 'start' in event.raw_text:
        await event.reply('Hi!,Sandeep welcome to instabot this will update you about who unfollowed you on instagram recently')

    if "update" in event.raw_text:
        await event.respond("This feature is still unavailable.")

    if "followers" in event.raw_text:
        await event.respond( "At this moment you are having "+str(followers)+" Followers")

    if "following" in event.raw_text:
        await event.respond("At this moment you are following "+str(following)+ " people")

    if "list" in event.raw_text:
        for follower in folowers['accounts']:
            await event.respond(str(follower))

        


client.start().run_until_disconnected()


