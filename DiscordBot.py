# bot.py
import os
import discord
import PictureManipulation
import json

TOKEN = '' # DON'T LEAVE THIS HERE WHEN PUTTING IT ON GITHUB

client = discord.Client(intents=discord.Intents.all())

async def sendPossibleDays(verified_data, message):
    if(verified_data):
        days_off = []
        blocked_by_events = []
        finishes_early_enough_days = []
        with open('session_start_time', 'r') as file:
            start_time = int(file.readline())
        for value in PictureManipulation.getPossibleDays(verified_data, start_time):
            if('Tuesday' in value or 'Thursday' in value):
                blocked_by_events.append(value)
            elif('-' in value):
                finishes_early_enough_days.append(value)
            else:
                days_off.append(value)
        message_to_send = ""
        message_to_send += 'The following are days that are available for sure: \n'
        for day in days_off:
            message_to_send += day + '\n'
        message_to_send += 'The following are days that are blocked by other events: \n'
        for day in blocked_by_events:
            message_to_send += day + '\n'
        message_to_send += 'The following are days where Ross finishes early enough to play: \n'
        for day in finishes_early_enough_days:
            message_to_send += day + '\n'

        await message.channel.send(message_to_send)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message: discord.Message):
    if client.user.mention in message.content:
        if('/RossRota' in message.content):
            if(message.attachments):
                for attachment in message.attachments:
                    if attachment.content_type.startswith("image"):
                        # download the image content
                        await message.channel.send("Just processing, GIVE ME A MOMENT")
                        content = await attachment.read()
                        #data = bytes.fromhex(content[2:])
                        with open('discord_upload.png', 'wb') as file:
                            file.write(content)
                        verified_data = PictureManipulation.ripTextFromImage('discord_upload.png')
                        with open('newest_verified_data.txt', 'w') as file:
                            #for line in verified_data:
                            verified_data_string = json.dumps(verified_data)
                            file.write(verified_data_string)
                        await sendPossibleDays(verified_data, message)
                    else:
                        await message.channel.send("Please attach an image of Ross' rota")
        elif('/CurrentRota' in message.content):
            with open('newest_verified_data.txt', 'r') as file:
                current_verified_data = json.loads(file.readline())
                await sendPossibleDays(current_verified_data, message)
        elif('/SetStartTime' in message.content):
            #/SetStartTime x to set start time from
            with open('session_start_time', 'w') as file:
                try:
                    start_time = message.content.split()[-1]
                    if(len(start_time) > 4):
                        raise Exception()
                    int(start_time)
                    file.write(start_time)
                except:
                    await message.channel.send("Enter a 24 hour time with no special characters")
        elif('/SetBlockedDays' in message.content):
            #/SetBlockedDays M-F, M-F, ... to set blocked days
            await message.channel.send("SetBlockedDays")
        elif('/Help' in message.content):
            #list of commands
            await message.channel.send("'/RossRota <image>' takes the uploaded image and gets all available days from it \n \
                                        '/CurrentRota' shows a list of possible days from todays date onwards \n \
                                        '/SetStartTime <time>' changes the current start time \n \
                                        '/SetBlockedDays <Monday-Sunday, ...> Sets the blocked days, input days in a comma seperated list \n \
                                        '/RossPoint will be added at some point")
        else:
            await message.channel.send("Write /Help to get a command list")

client.run(TOKEN)
