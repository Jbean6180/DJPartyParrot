import discord
import os
from discord.ext import commands, tasks
import random
from random import choice
from config import config
from musicstuffs.audiocontroller import AudioController
from musicstuffs.settings import Settings
from musicstuffs import utils
from musicstuffs.utils import guild_to_audiocontroller, guild_to_settings

from musicstuffs.commands.general import General


initial_extensions = ['musicstuffs.commands.music',
                      'musicstuffs.commands.general', 'musicstuffs.plugins.button']
bot = commands.Bot(command_prefix=config.BOT_PREFIX,
                   pm_help=True, case_insensitive=True)


if __name__ == '__main__':

    config.ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    config.COOKIE_PATH = config.ABSOLUTE_PATH + config.COOKIE_PATH

    if config.BOT_TOKEN == "":
        print("Error: No bot token!")
        exit

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)

status = ['Jamming out to music!', 'Partying!', 'Party Parrot Time!','Overdosing on Party', 'Osu','Beat Saber','Just Dance','Sailing the Seven Seas']

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}!  Ready to jam out? See `?help` command for details!')

@bot.event
async def on_ready():
    print(config.STARTUP_MESSAGE)
    change_status.start()

    for guild in bot.guilds:
        await register(guild)
        print("Joined {}".format(guild.name))

    print(config.STARTUP_COMPLETE_MESSAGE)

@tasks.loop(seconds=20)
async def change_status():
    await bot.change_presence(activity=discord.Game(choice(status)))

@bot.event
async def on_guild_join(guild):
    print(guild.name)
    await register(guild)


async def register(guild):

    guild_to_settings[guild] = Settings(guild)
    guild_to_audiocontroller[guild] = AudioController(bot, guild)

    sett = guild_to_settings[guild]

    await guild.me.edit(nick=sett.get('default_nickname'))

    if config.GLOBAL_DISABLE_AUTOJOIN_VC == True:
        return

    vc_channels = guild.voice_channels

    if sett.get('vc_timeout') == False:
        if sett.get('start_voice_channel') == None:
            try:
                await guild_to_audiocontroller[guild].register_voice_channel(guild.voice_channels[0])
            except Exception as e:
                print(e)

        else:
            for vc in vc_channels:
                if vc.id == sett.get('start_voice_channel'):
                    try:
                        await guild_to_audiocontroller[guild].register_voice_channel(vc_channels[vc_channels.index(vc)])
                    except Exception as e:
                        print(e)


bot.run(config.BOT_TOKEN, bot=True, reconnect=True)
