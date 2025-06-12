import discord,os,aiohttp,io,asyncio,ollama,math,logging,yt_dlp
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta,datetime
ollama.base_url = "http://localhost:11434"

load_dotenv()
FFMPEG_PATH = os.getenv("FFMPEG_PATH")
tokn1 = os.getenv('DISCKI')
TARGET_CHANNEL_NAME1= os.getenv('WELCOMESERVER')
handler=logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.guilds = True
bot = commands.Bot(command_prefix='.', intents=intents)
user_personalities = {}
user_moods = {}
user_histories = {}
bancounter={}
xp_data = {}
@bot.event
@commands.has_permissions(moderate_members=True)
async def on_message(message):
    if message.author.bot:
        return

    now = datetime.now()
    if now.hour == 0 and now.minute == 0 and now.second == 0:
        bancounter.clear()
    bad_words = ["parijat"]
    if any(word in message.content.lower() for word in bad_words):
        await message.delete()
        user = message.author
        user_key = str(user.id)
        bancounter[user_key] = bancounter.get(user_key, 0) + 1

        if bancounter[user_key] < 10:
            await message.channel.send(f"{user.mention} - Warning no. {bancounter[user_key]} added.")
        else:
            bancounter[user_key] = 0
            try:
                duration = timedelta(minutes=5)
                await user.timeout(duration, reason="Slurring 10 times today.")
                await message.channel.send(f"{user.mention} has been muted for 5 minutes.")
            except Exception as e:
                await message.channel.send(f"Failed to mute: {e}")

    user_id = str(message.author.id)
    xp_data.setdefault(user_id, {"xp": 0, "level": 1})
    user_stats = xp_data[user_id]
    user_stats["xp"] += 50
    xp = xp_data[user_id]["xp"]
    level = xp_data[user_id]["level"]
    leveled_up = False

    while xp >= (level + 1) * 1000:
        level += 1
        leveled_up = True

    if leveled_up:
        user_stats["level"] = level
        xp_required = (level + 1) * 1000

        embed = discord.Embed(
            title="🎉 Level Up!",
            description=f"**{message.author.mention} just reached Level {level}!**\n"
                        f"Total XP: `{xp} / {xp_required}`",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=message.author.avatar.url)
        embed.set_footer(text="Keep chatting to earn more XP!")

        channel = discord.utils.get(message.guild.text_channels, name="bot-commands")
        if channel:
            await channel.send(embed=embed)

    await bot.process_commands(message)
@bot.command()
async def rank(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    if user_id in xp_data:
        xp = xp_data[user_id]["xp"]
        level = xp_data[user_id]["level"]
        await ctx.send(f"{member.name} is level {level} with {xp} XP.")
    else:
        await ctx.send(f"{member.name} has no XP yet.")
@bot.command()
async def setpersonality(ctx, *, ply):
    user_id = ctx.author.id
    user_personalities[user_id] = ply
    user_histories[user_id] = [{"role": "system", "content": ply}]
    await ctx.send(f"Personality set to:\n`{ply}`")
@bot.command()
async def setmood(ctx, *, mood):
    user_moods[ctx.author.id] = mood.lower()
    await ctx.send(f"Mood set to: `{mood}`")
@bot.command()
async def clear(ctx):
    user_id = ctx.author.id
    user_histories.pop(user_id, None)
    await ctx.send("Memory cleared!")
@bot.command()
async def kit(ctx, *, prompt):
    user_id = ctx.author.id
    personality = user_personalities.get(user_id, "You are a joyful assitant who identify as an ai girl")
    mood = user_moods.get(user_id, "happy")

    mood_tones = {
        "happy": "Respond cheerfully and playfully.",
        "sad": "Be gentle and comforting. a life depends upon you",
        "angry": "Be logical ,serious, non chalant and in mood of roasting. Answers in as less words possible and doesn't trash talk, try to keep talks in 5-8 words",
        "flirty": "Be uplifting,flirty and teasing. show less brain and use as much as tomfoolery possible, keep talks limited to no more than 15 words.uWu",
        "toxic": "try to prove you are the only one and prove nobody could ever like you do and be lustfully flirty, you can use very long paragraphs here",
        "neutral": ""
    }
    mood_influence = mood_tones.get(mood, "")
    full_personality = personality + " " + mood_influence

    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": full_personality}]
    else:
        user_histories[user_id][0] = {"role": "system", "content": full_personality}

    user_histories[user_id].append({"role": "user", "content": prompt})

    await ctx.send("...")

    try:
        response = ollama.chat(
            model="gemma:2b",
            messages=user_histories[user_id]
        )

        reply = response['message']['content']
        user_histories[user_id].append({"role": "assistant", "content": reply})
        await ctx.send(reply[:2000])
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")
@bot.event
async def on_ready():
    print(f"Bot online as {bot.user.name}")
@bot.event
async def on_member_join(member):
    w, h = 800, 250
    img = Image.new('RGB', (w, h), color=0)
    draw = ImageDraw.Draw(img)

    for x in range(w):
        r = 255
        g = int(94 - (94 - 42) * x / w)
        b = int(58 + (104 - 58) * x / w)
        for y in range(h):
            img.putpixel((x, y), (r, g, b))

    try:
        font = ImageFont.truetype("comic.ttf", size=60)
    except IOError:
        font = ImageFont.load_default()

    draw.text((250, 100), f"Welcome {member.name}!", font=font, fill=(255, 255, 255))

    async with aiohttp.ClientSession() as session:
        async with session.get(str(member.avatar.url)) as resp:
            if resp.status != 200:
                return
            avatar_data = io.BytesIO(await resp.read())

    avatar_img = Image.open(avatar_data).resize((200, 200)).convert("RGBA")

    def crop_circle(img):
        size = img.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        img = img.convert("RGBA")
        result = Image.new('RGBA', size, (0, 0, 0, 0))
        result.paste(img, (0, 0), mask=mask)
        return result
    def add_icon_badge(avatar_img, badge_path="bot_badge.png", position="bottom_right"):
        badge = Image.open(badge_path).convert("RGBA").resize((40, 40))
        if position == "bottom_right":
            x = avatar_img.width - badge.width
            y = avatar_img.height - badge.height
        elif position == "top_right":
            x = avatar_img.width - badge.width
            y = 0
        elif position == "bottom_left":
            x = 0
            y = avatar_img.height - badge.height
        else:  # top_left
            x = 0
            y = 0

        avatar_img.paste(badge, (x, y), badge)  # Use badge as mask
        return avatar_img
    avatar_img = crop_circle(avatar_img)
    avatar_img = add_icon_badge(avatar_img, badge_path="bot_badge.png", position="bottom_right")
    img.paste(avatar_img, (20, 25))
    with io.BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)

        channel = discord.utils.get(member.guild.text_channels, name="welcome")
        if channel:
            await channel.send(file=discord.File(fp=image_binary, filename='welcome.png'))
@bot.event
async def on_member_remove(member):
    w, h = 800, 250
    img = Image.new('RGB', (w, h), color=0)
    draw = ImageDraw.Draw(img)
    user_id = str(member.id)
    user_stats = xp_data[user_id]
    xp = xp_data[user_id]["xp"]
    level = xp_data[user_id]["level"]
    xp_required = (level+1)*1000
    for x in range(w):
        r = int(30 + (50 - 30) * x / w)
        g = 30
        b = int(60 + (120 - 60) * x / w)
        for y in range(h):
            img.putpixel((x, y), (r, g, b))

    try:
        font = ImageFont.truetype("comic.ttf", size=40)
        font_small = ImageFont.truetype("arial.ttf", size=24)
    except IOError:
        font = ImageFont.load_default()

    draw.text((250, 100), f"{member.name} left the team.", font=font, fill=(255, 255, 255))

    async with aiohttp.ClientSession() as session:
        async with session.get(str(member.avatar.url)) as resp:
            if resp.status != 200:
                return
            avatar_data = io.BytesIO(await resp.read())

    avatar_img = Image.open(avatar_data).resize((200, 200)).convert("RGBA")

    def crop_circle(img):
        size = img.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        result = Image.new('RGBA', size)
        result.paste(img, mask=mask)
        return result

    bar_x, bar_y = 240, 150
    bar_width, bar_height = 500, 30
    progress = xp / xp_required
    filled_width = int(bar_width * progress)

    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=(50, 50, 50))
    draw.rectangle([bar_x, bar_y, bar_x + filled_width, bar_y + bar_height], fill=(0, 255, 100))

    xp_text = f"{xp} / {xp_required} XP"
    text_width, _ = draw.textsize(xp_text, font=font_small)
    draw.text((bar_x + (bar_width - text_width) // 2, bar_y + 5), xp_text, font=font_small, fill=(0, 0, 0))

    avatar_img = crop_circle(avatar_img)
    img.paste(avatar_img, (20, 25))

    with io.BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)

        channel = discord.utils.get(member.guild.text_channels, name="welcome")
        if channel:
            del xp_data[f"{member.id}"]
            await channel.send(file=discord.File(fp=image_binary, filename='bye_gradient.png'))
@bot.command(name='play')
async def play(ctx, *, url: str):
    if ctx.author.voice is None:
        return await ctx.send("You must be in a voice channel.")

    channel = ctx.author.voice.channel
    vc = ctx.voice_client

    if vc is None:
        vc = await channel.connect()
    elif vc.channel != channel:
        await vc.move_to(channel)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'default_search': 'auto',
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            audio_url = info['url']
            title = info.get('title', 'Unknown Title')
        except Exception as e:
            return await ctx.send(f"Error extracting audio: {e}")

    ffmpeg_opts = {
        'executable': FFMPEG_PATH,
        'options': '-vn'
    }

    try:
        source = discord.FFmpegPCMAudio(audio_url, executable=FFMPEG_PATH, options='-vn')
        vc.stop()
        vc.play(source, after=lambda e: print(f"Playback error: {e}") if e else None)
        await ctx.send(f"Now playing: **{title}**")
    except Exception as e:
        await ctx.send(f"Playback error: {e}")
        print(f"Playback error: {e}")
@bot.command(name='pause')
async def pause(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("⏸ Paused.")
    else:
        await ctx.send("Nothing is playing right now.")
@bot.command(name='resume')
async def resume(ctx):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("▶Resumed.")
    else:
        await ctx.send("Nothing is paused.")
@bot.command(name='skip')
async def skip(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏭ Skipped.")
    else:
        await ctx.send("Nothing to skip.")
@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
@bot.command()
async def leave(ctx):
    try:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected.")
        else:
            await ctx.send("Not connected.")
    except Exception as e:
        print(f"Error in leave command: {e}")
        await ctx.send(f"Error: {e}")
@bot.command()
async def join(ctx):
    try:
        if ctx.author.voice:
            vc = await ctx.author.voice.channel.connect()
            await ctx.send(f"Joined: {vc.channel.name}")
        else:
            await ctx.send("You must be in a voice channel.")
    except discord.ClientException as e:
        await ctx.send(f"Already connected elsewhere.")
    except discord.errors.Forbidden:
        await ctx.send("I don’t have permission to join the channel.")
    except Exception as e:
        await ctx.send(f"Something went wrong: {e}")
        print(f"Join Error: {e}")
@bot.command()
async def pfp(ctx, member: discord.Member):
    async with aiohttp.ClientSession() as session:
        async with session.get(str(member.avatar.url)) as resp:
            if resp.status != 200:
                return
            avatar_data = io.BytesIO(await resp.read())

    avatar_img = Image.open(avatar_data).resize((200, 200)).convert("RGB")
    with io.BytesIO() as image_binary:
        avatar_img.save(image_binary, 'PNG')
        image_binary.seek(0)
        channel = discord.utils.get(ctx.guild.text_channels, name="bot-commands")
        if not channel or not channel.permissions_for(ctx.guild.me).send_messages:
            channel = ctx.channel

        await channel.send(file=discord.File(fp=image_binary, filename='pfp.png'))
        await channel.send(f"Profile Picture of: {member.name}")
bot.run(tokn1, log_handler=handler,log_level=logging.DEBUG)