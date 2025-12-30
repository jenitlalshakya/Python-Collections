import discord
import requests
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv
from google import genai
from gemini_ai_new import ask_gemini
import json
import random
import os
import re
import math
import asyncio
from bs4 import BeautifulSoup

def find_discord_env(cache_file=".gemini_cache.json", key_name="DISCORD_BOT_TOKEN"):
    """
    Searches for a .env file that contains the given Discord bot token key.
    1️⃣ First tries to load from .gemini_cache.json.
    2️⃣ If missing, scans all internal drives for .env and updates cache.
    """

    env_path = None
    target_keywords = [key_name, "DISCORD_", "GEMINI_"]

    # try cache
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
                env_path = cached.get("cached_env_path") or cached.get("env_path")
                if env_path and os.path.exists(env_path):
                    print(f"⚡ Using cached .env path: {os.path.basename(env_path)}")
        except Exception as e:
            print(f"⚠️ Failed reading {cache_file}: {e}")

    # If not found, search all drives manually
    if not env_path or not os.path.exists(env_path):
        print("🔍 Scanning drives for .env ...")
        drives = [f"{chr(d)}:\\" for d in range(65, 91) if os.path.exists(f"{chr(d)}:\\")]

        for drive in drives:
            for root, dirs, files in os.walk(drive):
                # Skip system folders for speed/safety
                if any(skip in root.lower() for skip in ["windows", "program files", "appdata", "$recycle", "system volume information"]):
                    continue
                if ".env" in files:
                    path = os.path.join(root, ".env")
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if any(k in content for k in target_keywords):
                                env_path = path
                                print(f"✅ Found .env at: {env_path}")
                                break
                    except Exception:
                        pass
            if env_path:
                break

        # Update cache if found
        if env_path:
            try:
                cached_data = {}
                if os.path.exists(cache_file):
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cached_data = json.load(f)
                cached_data["cached_env_path"] = env_path
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cached_data, f, indent=4)
                print(f"💾 Cached .env path updated: {os.path.basename(env_path)}")
            except Exception as e:
                print(f"⚠️ Failed to update cache: {e}")

    # Load env
    if env_path and os.path.exists(env_path):
        load_dotenv(env_path)
        print("✅ Environment loaded successfully.")
    else:
        print("❌ No .env file found! Make sure it exists.")

    token = os.getenv(key_name)
    if not token:
        print(f"⚠️ {key_name} not found in .env file.")
    return token


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
MAX_DISCORD_LEN = 4000

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game("Assisting you!"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "hello" in message.content.lower():
        await message.channel.send(f"Hello {message.author.mention}! How can I assist you today?")

    await bot.process_commands(message)

@bot.command(aliases=["assist", "commands"])
async def helpme(ctx):
    """Shows what this bot can do"""
    commands_list = """
🤖 **Assistant Bot Commands**
- `/helpme` → Shows this help message
- `/weather <city>` → Example: /weather London
- `/calculate <expression>` → Example: /calculate 2+2*5
- `/motivate` → Get a motivational quote
- `/joke` → Hear a random programming joke
- `/google <query>` → Search something on Google

🎲 **Fun**
- `/roll <NdM>` → Roll dice (e.g., /roll 2d6, /roll 1d20)
- `/trivia` → Answer a random trivia question

📅 **Utility**
- `/remindme <seconds> <task>` → Set a reminder  
   Example: `/remindme 10 drink water`
"""
    await ctx.send(commands_list)

@bot.command(name="ai")
async def g(ctx, *, prompt):
    """Send a prompt to AI and get the reponse in Discord."""
    await ctx.send("🤖 AI is thinking...")
    try:
        response = ask_gemini(prompt)
        if len(response) > MAX_DISCORD_LEN:
            chunks = [response[i:i+MAX_DISCORD_LEN] for i in range(0, len(response), MAX_DISCORD_LEN)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response)
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")

@bot.command()
async def weather(ctx, *, city: str):
    """Give weather report based in your location (format: /weather <your City>)"""
    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%w"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            await ctx.send(f"🌦️ Weather in {city}: {r.text}")
        else:
            await ctx.send("⚠️ Could not fetch weather data.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
async def calculate(ctx, *, expression: str):
    """Solves basic math expressions"""
    try:
        expression = re.sub(r'(\d+)!', r'math.factorial(\1)', expression)
        result = eval(expression)
        await ctx.send(f"🧮 Result: `{result}`")
    except Exception as e:
        await ctx.send(f"⚠️ Sorry, I couldn't calculate that. ({e})")

@bot.command(name="motivate")
async def motivation(ctx):
    """Sends a motivational quote"""
    quotes = [
        "Keep going, you're doing great! 🚀",
        "Everyday is a chance to learn something new. 📚",
        "Don't give up, success is closer than you think! 💪"
    ]
    await ctx.send(random.choice(quotes))

@bot.command()
async def roll(ctx, dice: str = "1d6"):
    """Rolls dice in NdM format (e.g., 2d6, 1d20)"""
    try:
        rolls, limit = map(int, dice.lower().split("d"))
        results = [random.randint(1, limit) for _ in range(rolls)]
        await ctx.send(f"🎲 You rolled: {results} → Total: {sum(results)}")
    except Exception:
        await ctx.send("⚠️ Use format like '2d6' or '1d20'.")

@bot.command()
async def trivia(ctx):
    """Ask a random trivia question"""
    questions = {
        "What is the capital of Nepal?": "kathmandu",
        "Who wrote 'Harry Potter'?": "j.k. rowling",
        "What is 9 x 9?": "81",
    }
    question, answer = random.choice(list(questions.items()))
    await ctx.send(f"❓ {question}")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=15)
        if msg.content.lower() == answer:
            await ctx.send("✅ Correct! 🎉")
        else:
            await ctx.send(f"❌ Nope, the correct answer is: **{answer}**.")
    except:
        await ctx.send("⌛ Time's up!")
        
@bot.command()
async def joke(ctx):
    """Sends random Jokes."""
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs. 🐛",
        "Why did the fuction break up with the loop? It felt trapped. 🔁",
        "What's a computer's favorite snack? Microchips! 🍟"
    ]
    await ctx.send(random.choice(jokes))

@bot.command()
async def remindme(ctx, time: int, *, task: str):
    """set a reminder (in seconds)"""
    await ctx.send (f"⏰ Okay {ctx.author.mention}, I'll remind you in {time} seconds to: {task}")
    await asyncio.sleep(time)
    await ctx.send(f"🔔 Reminder: {task}, {ctx.author.mention}!")

@bot.command()
async def google(ctx, *, query: str):
    """Gives a mock google search link"""
    await ctx.send(f"🔎 Hear's what I found for **{query}**: https://www.google.com/search?q={query.replace(' ', '+')}")

class SnakeView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Play Snake 🎮", style=discord.ButtonStyle.green)
    async def play_button(self, interaction: discord.Interaction, button: Button):
        #option 1: Disable button after click
        button.disabled = True
        await interaction.response.edit_message(view=self)

        # Send the link or start the session
        await interaction.followup.send(
            "Here's your game! 👉[Play Snake](https://playsnake.org)",
            ephemeral=True
        )

@bot.command(name="snake")
async def snake(ctx):
    embed = discord.Embed(
        title="🐍 Snake Game",
        description="Click the button below to start playing!",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=SnakeView())


TOKEN = find_discord_env()

bot.run(TOKEN)
