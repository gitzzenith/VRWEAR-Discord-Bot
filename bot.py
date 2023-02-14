# bot.py
# Author: Zzenith
# Date: 8/7/21
# python 3.9

import os
import logging
import discord
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

submissionFolder = 'Submissions/'

@bot.event
async def on_ready():
    print(f'{bot.user}\'s connection established')

@bot.event
async def on_message(message):
    print(message.content)
    if(not message.content or message.content[0] != '!'):
        return
    # !submit
    if(message.content[1:7].lower() == 'submit'):
        # # checks 1
        if(len(message.attachments) != 1): # make sure exactly one image
            await message.reply('Please attach 1 image')
            return
        url = message.attachments[0].url
        if(url.split('.')[-1] != 'png'): # make sure its a png
            await message.reply('Make sure image is a .png')
            return
        if(message.attachments[0].size > 5000000000): # don't allow huge files
            await message.reply('Please keep image under 50MB')
            return
        width = message.attachments[0].width
        height = message.attachments[0].height
        if(width != height):
            await message.reply('Please submit a square image')
            return
        minSize = 1024
        if(width < minSize):
            await message.reply(f'Your submittion is under the minimum size of {minSize}x{minSize}')
            return

        # # success
        filename = f'{message.author.name}{message.author.discriminator}_submission.png' # title submission
        await message.attachments[0].save(submissionFolder + filename) # save submission into the submissions folder

        
        try:
            file = discord.File(submissionFolder + genMockup(filename)) # get file from path
        except Exception as e:
            logging.error(f'{message.author.name} caused an error at %s', 'division', exc_info=e)
            await message.reply('Something went wrong (<@219059572361527296> might be able to help)')
            return
        await message.reply(file=file, content='Your submission was successful. Feel free to resubmit with any changes') # send message with embed
        submissionsChannel = bot.get_channel(874715822898155611)
        
        submissionFile = discord.File(submissionFolder + filename)
        await submissionsChannel.send(file=submissionFile, content=f'{message.author.name} submitted this (<{url}>)') # log submission
        return

def genMockup(filename):
    final = Image.open('shirtBlack.png')
    shadowPass = Image.open('shirtshadow1.png')
    design = Image.open(submissionFolder + filename)
    design = design.resize((830, 830), Image.ANTIALIAS) # resize design

    try:
        final.paste(design, (531, 525), design) # paste design in correct position
    except Exception as e:
        logging.error('someone caused an error at %s', 'division', exc_info=e)
        final.paste(design, (531, 525))
        
    for x in range(5):
        shadowPass = shadowPass.filter(ImageFilter.GaussianBlur(radius=2)) # blur shadows each iteration
        final = Image.alpha_composite(final, shadowPass) # add shadows over final image
    
    final.save(submissionFolder + 'MOCKUP_' + filename)
    return 'MOCKUP_' + filename

bot.run(TOKEN) 