import discord,os,ollama,math,logging
from discord.ext import commands
from dotenv import load_dotenv
ollama.base_url = "http://localhost:11434"
load_dotenv()

tokn1 = os.getenv('DISCKI')
tokn2 = os.getenv('MODELNAME')
handler=logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='.', intents=intents)
user_personalities = {}
user_moods = {}
user_histories = {}

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
    personality = user_personalities.get(user_id, "You are a joyful assitant")
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
            model=str(tokn2),
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
bot.run(tokn1, log_handler=handler, log_level=logging.DEBUG)
