import discord  # https://guide.pycord.dev/installation/
import json  # for storing data
from discord import Option
import random

# declare client
intents = discord.Intents.all()  # was default()
bot = discord.Bot(intents=intents)

# json config data
f = open('config.json', encoding="utf-8")  # open json file
config = json.load(f)  # load file into dict
f.close()  # close file

guild_ids = config["server_ids"]  # comma separated guild ids

UPDATE_EVERY = 5
copied_channel = None


@bot.event
async def on_ready():
    print(f"{bot.user.name} Online.")


@bot.slash_command(description="Copy the current channels messages.", guild_ids=guild_ids)
async def copy(ctx):
    global copied_channel
    copied_channel = ctx.channel

    await ctx.respond(content="Messages Copied", ephemeral=True)


async def get_webhook(ctx):
    webhooks = await ctx.channel.webhooks()
    history_webhook = None
    for webhook in webhooks:
        if webhook.name == "CopyMessages":
            history_webhook = webhook
            break
    else:
        # create the webhook
        history_webhook = await ctx.channel.create_webhook(name="CopyMessages", avatar=None, reason="For CopyMessages")
    return history_webhook


@bot.slash_command(description="Paste the saved message data.", guild_ids=guild_ids)
async def paste(ctx, start_at: Option(int, "The message number to start at. Used for debugging",
                                      required=False, default=1)):
    await ctx.defer()
    all_messages = await copied_channel.history(limit=None, oldest_first=True).flatten()
    all_messages_count = len(all_messages) - start_at + 1

    # check start at parameter
    if all_messages_count > len(all_messages):
        embed = discord.Embed(color=0x880808, title=f":x: Invalid `start_at` Parameter",
                              description="Higher then the total message count.")
        await ctx.respond(embed=embed, ephemeral=True)
        return
    elif all_messages_count <= 0:
        embed = discord.Embed(color=0x880808, title=f":x: Invalid `start_at` Parameter",
                              description="Can not be below `0`.")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(color=0xFFFF00,
                          title=f"⏳ Pasting {all_messages_count} Messages",
                          description=f"This may take a while. This message will update every {UPDATE_EVERY} percent.")
    loading_bar = "🔳🔳🔳🔳🔳🔳🔳🔳🔳🔳"  # 🟨
    embed.set_footer(text=f"{loading_bar}\n0/{all_messages_count} Sent")
    loading_message = await ctx.followup.send(embed=embed)

    history_webhook = await get_webhook(ctx)

    percentiles = []
    for multiple in range(1, 10):
        percentiles.append(int(all_messages_count/UPDATE_EVERY)*multiple+1)
    count = 0
    # loop through messages
    for message in all_messages[start_at - 1:]:
        try:
            files = []
            embeds = []

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

            if count in percentiles:
                # edit message if applicable
                embed = discord.Embed(color=0xFFFF00,
                                      title=f"⏳ Pasting {all_messages_count} Messages",
                                      description=f"This may take a while. This message will update every {UPDATE_EVERY} percent.")
                percent = (count / all_messages_count) * 100
                percent_string = "{0:02.0f}".format(percent)
                number_of_squares = int(str(percent_string)[0])
                number_of_blanks = 10 - number_of_squares
                squares = "🟨" * number_of_squares + "🔳" * number_of_blanks
                embed.set_footer(text=f"{squares}\n{count}/{all_messages_count} Sent")
                await loading_message.edit(embed=embed)
            print(count)
        except Exception as ex:
            nick = "Server Message"
            avatar = "https://cdn.discordapp.com/attachments/929182726203002920/1110112696889786418/Discord-Logo-Circle.png"
            default = False
            text = ""
            match message.type:
                case discord.MessageType.pins_add:
                    text = f"<:pin:1110118275662237759> {message.author.mention} pinned **a message** to this channel. See all **pinned messages**."
                case discord.MessageType.new_member:
                    join_messages = ["Yay you made it, User!",
                               "User is here.",
                               "User just showed up!",
                               "User hopped into the server.",
                               "Welcome User. Say hi!",
                               "User joined the party.",
                               "Everyone welcome User!",
                               "Good to see you, User.",
                               "Glad you're here, User.",
                               "User just landed.",
                               "User just slid into the server.",
                               "A wild User appeared.",
                               "Welcome, User. We hope you brought pizza."]
                    random_element = random.choice(join_messages)
                    text = "<:join:1110122592955813988> " + random_element.replace('User', message.author.mention)
                case discord.MessageType.premium_guild_subscription:
                    text = f"<:nitro:1110122830030446694> {message.author.mention} just boosted the server!"
                case discord.MessageType.premium_guild_tier_1:
                    text = f"<:nitro:1110122830030446694> {message.author.mention} just boosted the server! {message.guild.name} has achieved **Level 1!**"
                case discord.MessageType.premium_guild_tier_2:
                    text = f"<:nitro:1110122830030446694> {message.author.mention} just boosted the server! {message.guild.name} has achieved **Level 2!**"
                case discord.MessageType.premium_guild_tier_3:
                    text = f"<:nitro:1110122830030446694> {message.author.mention} just boosted the server! {message.guild.name} has achieved **Level 3!**"
                case _:
                    # default case
                    default = True
                    embed = discord.Embed(color=0x880808,
                                          title=f":x: Failed on Message {count}",
                                          description=f"``` > {str(ex)} ```",
                                          url=message.jump_url)
                    await loading_message.edit(embed=embed)
                    await history_webhook.send(embed=embed, avatar_url=avatar, username=nick)
            if not default:
                await history_webhook.send(content=text, avatar_url=avatar, username=nick)

        count += 1


    embed = discord.Embed(color=0x00FF00, title=f"✅ {count} Messages Pasted")
    await loading_message.edit(embed=embed)


@bot.message_command(name="Get Message Number", guild_ids=guild_ids)
async def get_message_number(ctx, message: discord.Message):
    await ctx.defer()
    messages = await message.channel.history(limit=None, oldest_first=True).flatten()
    message_number = messages.index(message) + 1
    embed = discord.Embed(color=0x00FF00, title=f"Message Number: {message_number}", url=message.jump_url)
    await ctx.followup.send(embed=embed)


# run bot
# discord dev portal -> bot -> reset token -> copy
bot.run(config["token"])
