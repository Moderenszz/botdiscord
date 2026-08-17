import os
import random
from datetime import datetime
import discord
from discord.ext import tasks
from PIL import Image, ImageDraw, ImageFont
import io
import aiohttp
import math

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)

# Konfigurasi
MY_DISCORD_ID = 1473994384059011124
is_afk = False
afk_pesan = ""
recent_joins = []

@tasks.loop(hours=24)
async def update_status_tanggal():
    now = datetime.now()
    tanggal_str = now.strftime('%d/%m/%Y')
    await client.change_presence(activity=discord.Game(name=f"📅 {tanggal_str} | !cinfo"))

@client.event
async def on_ready():
    print(f'Bot aktif sebagai {client.user}')
    if not update_status_tanggal.is_running():
        update_status_tanggal.start()

def is_staff(member):
    staff_roles = ["owner", "admin", "supervisor", "staff", "moderator", "junior mod", "elite guard", "trial mod"]
    return any(role.name.lower() in staff_roles for role in member.roles) or member.guild_permissions.administrator

async def get_circular_avatar(user):
    avatar_url = user.display_avatar.url
    async with aiohttp.ClientSession() as session:
        async with session.get(str(avatar_url)) as resp:
            data = await resp.read()
            img = Image.open(io.BytesIO(data)).convert("RGBA").resize((120, 120))
            mask = Image.new("L", (120, 120), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 120, 120), fill=255)
            output = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
            output.paste(img, (0, 0), mask=mask)
            return output

async def create_jodoh_image(user1, user2, percent):
    image = Image.new('RGB', (800, 400), (20, 20, 40))
    draw = ImageDraw.Draw(image)
    
    avatar1 = await get_circular_avatar(user1)
    avatar2 = await get_circular_avatar(user2)

    image.paste(avatar1, (50, 80), avatar1)
    image.paste(avatar2, (50, 230), avatar2)
    
    draw.text((190, 85), f"Jodoh: {user1.display_name}", fill=(255, 255, 255))
    draw.text((190, 235), f"Jodoh: {user2.display_name}", fill=(255, 255, 255))
    draw.text((500, 100), f"Kecocokan: {percent}%", fill=(255, 255, 0))
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

@client.event
async def on_message(message):
    global is_afk, afk_pesan
    if message.author == client.user or not message.guild: return
    
    content = message.content.lower()
    
    # 1. !jodoh
    if content.startswith('!jodoh'):
        if len(message.mentions) < 2: return
        img = await create_jodoh_image(message.mentions[0], message.mentions[1], random.randint(1, 100))
        await message.channel.send(file=discord.File(img, "jodoh.png"))

    # 2. !dadu
    elif content.startswith('!dadu'):
        await message.channel.send(f"🎲 Hasil dadu: **{random.randint(1, 6)}**")

    # 3. !bantuan (Kalkulator)
    elif content.startswith('!bantuan'):
        expr = message.content.replace('!bantuan', '').strip()
        try:
            result = eval(expr, {"__builtins__": None}, {"math": math})
            await message.channel.send(f"🧮 Hasil: **{result}**")
        except: await message.channel.send("❌ Rumus salah!")

    # 4. !tanggal
    elif content == '!tanggal':
        await message.channel.send(f"📅 Wanci: {datetime.now().strftime('%H:%M:%S')}, Tanggal: {datetime.now().strftime('%d/%m/%Y')}")

    # 5. !ping
    elif content == '!ping':
        await message.channel.send(f"🏓 Pong! Latensi: **{round(client.latency * 1000)}ms**")

    # 6. !server
    elif content == '!server':
        await message.channel.send(f"🏰 Server: {message.guild.name} | Total Member: {message.guild.member_count}")

    # 7. !afk
    elif content.startswith('!afk'):
        afk_pesan = message.content[5:] or "Lagi AFK"
        is_afk = True
        await message.channel.send("💤 Mode AFK aktif!")

    # Moderasi (Singkat)
    elif content.startswith('!clear') and is_staff(message.author):
        n = int(message.content.split()[1])
        await message.channel.purge(limit=n+1)

# Ngambil token otomatis ti Repository Secrets GitHub
client.run(os.getenv('DISCORD_TOKEN'))
