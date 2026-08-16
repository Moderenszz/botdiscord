import os
import random
from datetime import datetime
import discord
from PIL import Image, ImageDraw, ImageFont # Peryogi library Pillow
import io

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# --- FUNGSI GENERATE GAMBAR JODOH ---
def create_jodoh_image(user1, user2, percent):
    # Jieun gambar gradiasi biru tua ka biru muda (Ukuran 400x200)
    width, height = 400, 200
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Logika gradiasi manual
    for y in range(height):
        r = int(0 + (135 - 0) * (y / height))    # Gradiasi biru tua ka biru muda
        g = int(0 + (206 - 0) * (y / height))
        b = int(139 + (235 - 139) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Tambah teks persenan
    draw.text((10, 50), f"{user1.name} & {user2.name}", fill=(255, 255, 255))
    draw.text((150, 100), f"{percent}% Cocok!", fill=(255, 255, 0))
    
    # Simpen ka buffer
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()

    # --- COMMAND JODOH (Visual Gradiasi) ---
    if msg.startswith('!jodoh'):
        if len(message.mentions) < 2:
            await message.channel.send("⚠️ Tag dua jalma! Conto: `!jodoh @user1 @user2`")
            return
        
        user1, user2 = message.mentions[0], message.mentions[1]
        percent = random.randint(1, 100)
        
        img_buffer = create_jodoh_image(user1, user2, percent)
        await message.channel.send(file=discord.File(img_buffer, filename="jodoh.png"))

    # --- COMMAND UTILITAS (Lain Jokes) ---
    elif msg == '!tanggal':
        now = datetime.now()
        await message.channel.send(f"📅 Wanci: {now.strftime('%d/%m/%Y %H:%M:%S')}")

    elif msg == '!ping':
        await message.channel.send(f"🏓 Latensi: {round(client.latency * 1000)}ms")

    elif msg.startswith('!translate'):
        # Logika translate anu sateuacanna tetep aya
        ... 

    elif msg == '!cinfo':
        balasan = (
            "🛠️ **Command Fungsional:**\n"
            "> `!jodoh @u1 @u2` - Cek kecocokan (Visual)\n"
            "> `!tanggal` - Cek wanci\n"
            "> `!ping` - Latensi\n"
            "> `!translate` - Tarjamahkeun\n"
            "> `!clear`, `!mute`, `!kick`, `!ban` (Staf Only)"
        )
        await message.channel.send(balasan)

client.run(os.getenv('DISCORD_TOKEN'))
