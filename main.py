import discord  # https://guide.pycord.dev/installation/
import json  # for storing data
from discord import Option

# declare client
intents = discord.Intents.all()  # was default()
bot = discord.Bot(intents=intents)

# json config data
f = open('config.json', encoding="utf-8")  # open json file
config = json.load(f)  # load file into dict
f.close()  # close file

guild_ids = config["server_ids"]  # comma separated guild ids

UPDATE_EVERY = 10


@bot.event
async def on_ready():
    print(f"{bot.user.name} Online.")


copied_channel = None


@bot.slash_command(description="Copy the current channels messages.", guild_ids=guild_ids)
async def copy(ctx):
    global copied_channel
    copied_channel = ctx.channel

    await ctx.respond(content="Messages Copied", ephemeral=True)


@bot.slash_command(description="Paste the saved message data.", guild_ids=guild_ids)
async def paste(ctx, start_at: Option(int, "The message number to start at. Used for debugging",
                                      required=False, default=1)):
    await ctx.defer()
    all_messages = await copied_channel.history(limit=None, oldest_first=True).flatten()
    all_messages_count = len(all_messages)
    embed = discord.Embed(color=0xFFFF00,
                          title=f"⏳ Pasting {all_messages_count} Messages",
                          description=f"This may take a while. This message will update every {UPDATE_EVERY} messages.")
    loading_bar = "🔳🔳🔳🔳🔳🔳🔳🔳🔳🔳"  # 🟨
    embed.set_footer(text=f"{loading_bar}\n0/{all_messages_count} Sent")
    loading_message = await ctx.followup.send(embed=embed)

    webhooks = await ctx.channel.webhooks()
    history_webhook = None
    for webhook in webhooks:
        if webhook.name == "CopyMessages":
            history_webhook = webhook
            break
    else:
        # create the webhook
        history_webhook = await ctx.channel.create_webhook(name="CopyMessages", avatar=None, reason="For CopyMessages")

    count = 0
    # loop through messages
    for message in all_messages[start_at-1:]:
        try:
            content = None
            files = []
            embeds = []
            nick = None

            # get files
            for attachment in message.attachments:
                file = await attachment.to_file()
                files.append(file)

            # get embeds
            for old_embed in message.embeds:
                embeds.append(old_embed)

            # get content
            content = message.content

            # get name
            nick = message.author.display_name
            if nick is None:
                nick = "Deleted User"

            # get avatar
            avatar = message.author.display_avatar

            # send webhook
            await history_webhook.send(content=content, embeds=embeds, files=files,
                                       username=nick,
                                       avatar_url=avatar)

            count += 1

            if count % UPDATE_EVERY == 0:
                # edit message if applicable
                percent = (count / all_messages_count) * 100
                percent_string = "{0:02.0f}".format(percent)
                number_of_squares = int(str(percent_string)[0])
                number_of_blanks = 10 - number_of_squares
                squares = "🟨"*number_of_squares + "🔳"*number_of_blanks
                embed.set_footer(text=f"{squares}\n{count}/{all_messages_count} Sent")
                await loading_message.edit(embed=embed)
        except Exception as ex:
            # send error
            embed.color = 0x880808
            embed.title = f":x: Failed On Message {count}"
            embed.description = f"> ```{str(ex)}```"
            embed.url = message.jump_url
            await loading_message.edit(embed=embed)
            return

    embed = discord.Embed(color=0x00FF00, title=f"✅ {count} Messages Pasted")
    await loading_message.edit(embed=embed)


# run bot
# discord dev portal -> bot -> reset token -> copy
bot.run(config["token"])