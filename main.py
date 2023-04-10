import discord  # https://guide.pycord.dev/installation/
import json  # for storing data

# declare client
intents = discord.Intents.all()  # was default()
bot = discord.Bot(intents=intents)

guild_ids = []  # comma separated guild ids

# json config data
f = open('config.json', encoding="utf-8")  # open json file
config = json.load(f)  # load file into dict
f.close()  # close file

f = open('data.json', encoding="utf-8")  # open json
data = json.load(f)  # read data
f.close()  # close

@bot.event
async def on_ready():
    print(f"{bot.user.name} Online.")


# run bot
# discord dev portal -> bot -> reset token -> copy
bot.run(config["Token"])