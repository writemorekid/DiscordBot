import discord
from discord.ext import commands
import aiohttp
import io

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.command()
async def stealsticker(ctx, name: str = None):
    if not ctx.message.reference:
        return await ctx.send("❌ Reply to a sticker message to use this command.")

    replied = ctx.message.reference.resolved
    if not replied.stickers:
        return await ctx.send("❌ The replied message doesn't contain a sticker.")

    sticker = replied.stickers[0]

    if not name:
        name = sticker.name

    url = f"https://media.discordapp.net/stickers/{sticker.id}.webp"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send("❌ Failed to download sticker.")
                data = await resp.read()

        await ctx.guild.create_sticker(
            name=name,
            description=f"Stolen by {ctx.author}",
            emoji="🙂",  # Required placeholder
            file=discord.File(io.BytesIO(data), filename=f"{name}.webp")
        )

        await ctx.send(f"✅ Sticker `{name}` added to the server.")

    except discord.Forbidden:
        await ctx.send("❌ I need 'Manage Emojis and Stickers' permission.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Failed to add sticker: {e}")

@bot.command()
async def stealemoji(ctx, emoji_str: str, name: str = None):
    try:
        if emoji_str.startswith("<a:"):  # animated emoji
            animated = True
        elif emoji_str.startswith("<:"):  # static emoji
            animated = False
        else:
            return await ctx.send("❌ That's not a custom Discord emoji.")

        emoji_id = emoji_str.split(":")[-1].replace(">", "")
        emoji_name = name or emoji_str.split(":")[1]

        file_ext = "gif" if animated else "png"
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{file_ext}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send("❌ Could not fetch the emoji.")
                data = await resp.read()

        emoji = await ctx.guild.create_custom_emoji(name=emoji_name, image=data)
        await ctx.send(f"✅ Emoji added: <:{emoji.name}:{emoji.id}>")

    except discord.Forbidden:
        await ctx.send("❌ Missing 'Manage Emojis and Stickers' permission.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Failed to add emoji: {e}")

# 🔑 Replace this with your actual bot token
bot.run("MTM3MTUwNDgzMDk4MzcwNDU5OA.G6IQ86.gXBxzom3AOrt87nbb92bQo06krTgkxQzwDX_Q4")
